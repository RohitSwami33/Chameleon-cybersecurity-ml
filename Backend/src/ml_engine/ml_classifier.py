try:
    import tensorflow as tf
except ImportError:
    tf = None  # TensorFlow not available (e.g. Python 3.14) — heuristic mode only
import numpy as np
import re
from src.core.config import settings, MODEL_PATH
from src.core.models import AttackType, ClassificationResult
import os

class MLClassifier:
    def __init__(self):
        self.model = None
        self.char_to_idx = {}
        self.idx_to_class = {
            0: AttackType.BENIGN,
            1: AttackType.SQLI,
            2: AttackType.XSS,
            3: AttackType.SSI
        }
        
        try:
            if tf is not None and os.path.exists(MODEL_PATH):
                # Register custom objects before loading
                custom_objects = {
                    'custom_standardization': lambda x: x,  # Placeholder
                    'char_split': lambda x: x  # Placeholder
                }
                self.model = tf.keras.models.load_model(
                    MODEL_PATH,
                    custom_objects=custom_objects,
                    compile=False  # Skip compilation to avoid issues
                )
                print(f"[OK] Loaded ML model from {MODEL_PATH}")
            else:
                print(f"[WARN] Model file not found at {MODEL_PATH}")
                print(f"[WARN] Using heuristic-based classification only")
        except Exception as e:
            print(f"[WARN] Error loading ML model: {e}")
            print(f"[WARN] Falling back to heuristic-based classification")
            self.model = None
            
        self.build_char_mapping()

    def build_char_mapping(self):
        # Printable ASCII characters
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        self.char_to_idx = {char: idx + 1 for idx, char in enumerate(chars)}
        # 0 is reserved for padding

    def encode_input(self, text: str) -> np.ndarray:
        text = str(text)
        encoded = [self.char_to_idx.get(c, 0) for c in text]
        encoded = encoded[:settings.MAX_INPUT_LENGTH]
        # Pad with zeros
        if len(encoded) < settings.MAX_INPUT_LENGTH:
            encoded += [0] * (settings.MAX_INPUT_LENGTH - len(encoded))
        return np.array([encoded])

    def heuristic_fallback(self, text: str) -> tuple[AttackType, float]:
        text_lower = text.lower()

        # =====================================================================
        # BENIGN EXCEPTIONS - Common legitimate commands (check FIRST)
        # =====================================================================
        benign_patterns = [
            r"python\d*\s+--version",
            r"node\s+--version",
            r"npm\s+--version",
            r"pip\d*\s+--version",
            r"java\s+--version",
            r"git\s+--version",
            r"docker\s+--version",
            r"curl\s+--version",
            r"wget\s+--version",
            r"python\d*\s+-m\s+pip",
            r"npm\s+(install|run|build|start|test|dev)",
            r"git\s+(status|log|pull|push|commit|checkout|branch)",
            r"docker\s+(ps|images|run|build|stop|start)",
            r"systemctl\s+(status|start|stop|restart)",
            r"journalctl\s+-u",
        ]
        for pattern in benign_patterns:
            if re.search(pattern, text_lower):
                return AttackType.BENIGN, 0.0

        # =====================================================================
        # SSI (Server-Side Injection) Patterns - Check first (most specific)
        # =====================================================================
        ssi_patterns = [
            r"<!--#exec", r"<!--#include", r"<!--#echo", r"<!--#config",
            r"<!--#set", r"<!--#printenv", r"<!--#flastmod", r"<!--#fsize",
            r"\{\{.*\}\}",           # SSTI: Jinja2, Angular
            r"\$\{.*\}",             # SSTI: Spring EL, JavaScript
            r"<%.*%>",               # SSTI: JSP, ASP
            r"\[\[.*\]\]",           # SSTI: Some templates
            r"#\{.*\}",              # SSTI: Ruby, OGNL
            r"\{\%.*\%\}",           # SSTI: Jinja2 blocks
            r"\{\{7\*7\}\}",         # SSTI test payload
            r"\{\{.*\*.*\}\}",       # SSTI arithmetic
        ]
        for pattern in ssi_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SSI, 0.90

        # =====================================================================
        # XSS (Cross-Site Scripting) Patterns
        # =====================================================================
        xss_patterns = [
            r"<script", r"</script>", r"javascript:", r"onerror\s*=",
            r"onload\s*=", r"onclick\s*=", r"onmouseover\s*=",
            r"<iframe", r"<svg.*on", r"<math", r"<img.*onerror",
            r"document\.cookie", r"document\.location", r"document\.write",
            r"alert\s*\(", r"confirm\s*\(", r"prompt\s*\(",
            r"eval\s*\(", r"setTimeout\s*\(", r"setInterval\s*\(",
            r"innerHTML\s*=", r"outerHTML\s*=", r"insertAdjacentHTML",
            r"fromcharcode", r"atob\s*\(", r"btoa\s*\(",
            r"<body.*on", r"<input.*on", r"<form.*on",
            r"data:text/html", r"<embed", r"<object",
            r"<details.*ontoggle", r"<marquee.*onstart",
        ]
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.XSS, 0.90

        # =====================================================================
        # SQL Injection (SQLi) Patterns
        # =====================================================================
        sqli_patterns = [
            r"union\s+select", r"union\s+all\s+select",
            r"or\s+1\s*=\s*1", r"and\s+1\s*=\s*1",
            r"'\s*or\s*'", r"'\s*and\s*'",
            r"--\s*$", r"--\s+", r"#\s*$",
            r"drop\s+table", r"drop\s+database",
            r"insert\s+into", r"update\s+.*\s+set",
            r"delete\s+from", r"truncate\s+table",
            r"admin'\s*--", r"admin'\s*#",
            r"'\s*or\s+'1'\s*=\s*'1", r"'\s*or\s+true",
            r"select\s+.*\s+from", r"select\s+.*\s+where",
            r"exec\s+xp_", r"execute\s+xp_",
            r"waitfor\s+delay", r"sleep\s*\(",
            r"benchmark\s*\(", r"pg_sleep",
            r"information_schema", r"sys\.(tables|columns|objects)",
            r"concat\s*\(", r"char\s*\(", r"hex\s*\(",
            r"0x[0-9a-fA-F]+",  # Hex values
            r"'\s*;\s*",        # Statement termination
        ]
        for pattern in sqli_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SQLI, 0.85

        # =====================================================================
        # Path Traversal Patterns
        # =====================================================================
        path_traversal_patterns = [
            r"\.\./",              # Basic Linux ../
            r"\.\.\\",             # Windows ..\
            r"\.\.%2f",            # URL encoded ../
            r"\.\.%5c",            # URL encoded ..\
            r"%2e%2e%2f",          # Fully URL encoded
            r"%2e%2e/",            # Partially URL encoded
            r"\.\.%252f",          # Double URL encoded
            r"%252e%252e%252f",    # Double URL encoded
            r"\.\.%c0%af",         # Unicode encoding
            r"\.\.%c1%9c",         # Unicode encoding (Windows)
            r"/etc/passwd",        # Sensitive Linux files
            r"/etc/shadow",        # Sensitive Linux files
            r"/proc/self",         # Linux proc filesystem
            r"/var/log",           # Linux logs
            r"\\windows\\system32", # Windows system files
            r"\\windows\\repair",   # Windows repair
            r"boot\.ini",          # Windows boot
            r"win\.ini",           # Windows ini files
            r"web\.config",        # ASP.NET config
            r"\.htaccess",         # Apache config
            r"wp-config\.php",     # WordPress config
            r"\.env",              # Environment files
            r"\.git/",             # Git directory
            r"\.svn/",             # SVN directory
        ]
        for pattern in path_traversal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SSI, 0.90

        # =====================================================================
        # Pipe & Command Injection Patterns
        # =====================================================================
        pipe_injection_patterns = [
            r"\|\s*\w+",           # | command
            r"\|&",                # |&
            r"\|\|",               # ||
            r";\s*\w+",            # ; command
            r"&\s*\w+",            # & command
            r"`[^`]+`",            # Backtick execution
            r"\$\([^)]+\)",        # $(command) substitution
            r">\s*/",              # Redirect to root
            r"<\s*/",              # Redirect from root
            r"&&\s*\w+",           # && command
            r"\|\s*cat\s+",        # | cat
            r"\|\s*ls\s+",         # | ls
            r"\|\s*whoami",        # | whoami
            r"\|\s*id\s",          # | id
            r"\|\s*uname",         # | uname
        ]
        for pattern in pipe_injection_patterns:
            if re.search(pattern, text):
                return AttackType.SSI, 0.90

        # =====================================================================
        # OS Command Injection / Destructive Commands
        # =====================================================================
        os_patterns = [
            r"rm\s+-rf", r"rm\s+-fr", r"rm\s+/\s",
            r"wget\s+http", r"wget\s+https",
            r"curl\s+.*\|\s*bash", r"curl\s+.*\|\s*sh",
            r"cat\s+/etc/passwd", r"cat\s+/etc/shadow",
            r"nc\s+-e", r"nc\s+.*-e", r"netcat\s+-e",
            r"bash\s+-i", r"bash\s+-c",
            r"chmod\s+\+x", r"chmod\s+777",
            r"chown\s+root", r"chown\s+sudo",
            r"sudo\s+su", r"sudo\s+bash", r"sudo\s+-i",
            r"su\s+-", r"su\s+root",
            r"mkfifo", r"mknod",
            r"telnet\s+", r"ssh\s+.*@",
            r"python.*-c\s+.*import\s+socket",
            r"perl.*-e\s+.*socket",
            r"ruby.*-e\s+.*socket",
            r"php.*-r\s+.*fsockopen",
            r"lua.*-e\s+.*socket",
            r"nmap\s+", r"masscan\s+",
            r"hydra\s+", r"john\s+", r"hashcat\s+",
            r"sqlmap\s+", r"nikto\s+", r"nuclei\s+",
            r"metasploit", r"msfconsole",
            r"meterpreter", r"reverse.*shell",
            r"bind.*shell", r"payload.*sh",
            r"backdoor", r"trojan", r"rat\s",
            r"keylog", r"screen\s+capture",
            r"/dev/tcp/", r"/dev/udp/",
            r"base64\s+-d", r"base64\s+--decode",
            r"xxd\s+-r", r"xxd\s+--revert",
        ]
        for pattern in os_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SSI, 0.95

        # =====================================================================
        # NoSQL Injection Patterns
        # =====================================================================
        nosql_patterns = [
            r"\{\s*\"\s*\$\s*gt\s*:",    # {$gt:
            r"\{\s*\"\s*\$\s*lt\s*:",    # {$lt:
            r"\{\s*\"\s*\$\s*ne\s*:",    # {$ne:
            r"\{\s*\"\s*\$\s*regex\s*:", # {$regex:
            r"\{\s*\"\s*\$\s*where\s*:", # {$where:
            r"\{\s*\"\s*\$\s*or\s*:",    # {$or:
            r"\{\s*\"\s*\$\s*and\s*:",   # {$and:
            r"\{\s*\"\s*\$\s*in\s*:",    # {$in:
            r"\{\s*\"\s*\$\s*nin\s*:",   # {$nin:
            r"\"password\"\s*:\s*\{",    # password: {
            r"\"username\"\s*:\s*\{",    # username: {
        ]
        for pattern in nosql_patterns:
            if re.search(pattern, text):
                return AttackType.SQLI, 0.85

        # =====================================================================
        # SSRF (Server-Side Request Forgery) Patterns
        # =====================================================================
        ssrf_patterns = [
            r"http://127\.0\.0\.1",
            r"http://localhost",
            r"http://0\.0\.0\.0",
            r"http://\[::1\]",
            r"http://169\.254\.169\.254",  # AWS metadata
            r"http://metadata\.google",     # GCP metadata
            r"http://169\.254\.170\.2",     # ECS metadata
            r"gopher://",
            r"dict://",
            r"file://",
            r"ldap://",
            r"tftp://",
            r"netdoc://",
            r"http://.*:22",  # SSH port
            r"http://.*:23",  # Telnet port
            r"http://.*:3306", # MySQL port
            r"http://.*:5432", # PostgreSQL port
            r"http://.*:6379", # Redis port
            r"http://.*:27017", # MongoDB port
        ]
        for pattern in ssrf_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SSI, 0.85

        # =====================================================================
        # XXE (XML External Entity) Patterns
        # =====================================================================
        xxe_patterns = [
            r"<!DOCTYPE.*\[",
            r"<!ENTITY",
            r"SYSTEM\s+['\"]file:",
            r"SYSTEM\s+['\"]http:",
            r"SYSTEM\s+['\"]expect:",
            r"PUBLIC\s+['\"]",
            r"<!ATTLIST",
            r"<!NOTATION",
        ]
        for pattern in xxe_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return AttackType.SSI, 0.90

        # =====================================================================
        # Brute Force (heuristic: short text with common keywords)
        # =====================================================================
        bf_keywords = ["password", "123456", "admin", "root"]
        if len(text) < 15 and any(keyword in text_lower for keyword in bf_keywords):
            if any(c.isdigit() for c in text) or "password" in text_lower:
                return AttackType.BRUTE_FORCE, 0.75

        # =====================================================================
        # Default: BENIGN
        # =====================================================================
        return AttackType.BENIGN, 0.0

    def classify(self, text: str) -> ClassificationResult:
        attack_type = AttackType.BENIGN
        confidence = 0.0
        is_malicious = False

        # Disable ML model prediction on Render due to dtype issues
        # Use heuristic-based detection which works reliably
        # TODO: Fix ML model compatibility with TensorFlow 2.16.1
        
        # Use heuristic detection
        heuristic_type, heuristic_conf = self.heuristic_fallback(text)
        if heuristic_type != AttackType.BENIGN:
            attack_type = heuristic_type
            confidence = heuristic_conf

        is_malicious = attack_type != AttackType.BENIGN
        
        return ClassificationResult(
            attack_type=attack_type,
            confidence=confidence,
            is_malicious=is_malicious
        )

classifier = MLClassifier()
