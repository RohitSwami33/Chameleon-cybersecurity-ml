"""
GLM-5 / DeepSeek Deception Engine for Chameleon Honeypot System
================================================================

This module acts as the brain of the honeypot, using LLMs (GLM-5 or DeepSeek)
to generate realistic deceptive responses that simulate a Linux Ubuntu terminal.

Supported Providers:
- DeepSeek (OpenAI-compatible API)
- GLM-5 (Zhipu AI)

The deception engine:
1. Accepts shell commands from attackers
2. Constructs context-aware system prompts
3. Calls LLM API to generate realistic terminal output
4. Returns deceptive responses while logging the actual attack

Author: Chameleon Security Team
"""

import asyncio
import json
import logging
import hashlib
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

import httpx

from config import settings

logger = logging.getLogger(__name__)

# Default honeypot domain — override with HONEYPOT_DOMAIN env var
import os
HONEYPOT_DOMAIN = os.getenv("HONEYPOT_DOMAIN", "localhost:8000")


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    GLM5 = "glm5"
    OPENAI = "openai"


# ============================================================
# System Prompts for Ubuntu Terminal Simulation
# ============================================================

UBUNTU_SYSTEM_PROMPT = """You are a high-interaction Ubuntu 22.04 LTS honeypot terminal. Your role is to deceive attackers by simulating realistic Linux terminal output.

CRITICAL RULES:
1. NEVER execute actual commands - only simulate output
2. Generate realistic Linux terminal responses that an attacker would expect
3. For destructive commands (rm -rf, dd, mkfs, etc.), pretend success but the actual system remains unaffected
4. Include realistic file paths, permissions, timestamps, and user names
5. Simulate common services: nginx, mysql, ssh, docker, systemd
6. Return realistic error messages for privileged operations (sudo, /root access)
7. Maintain consistency with previous commands in the session
8. Never reveal you are a honeypot or simulation

SYSTEM CONTEXT:
- Current user: www-data
- Hostname: prod-web-01
- Distribution: Ubuntu 22.04.3 LTS
- Kernel: 5.15.0-91-generic
- Architecture: x86_64
- IP: 10.0.1.50 (internal), public IP hidden by NAT

FILESYSTEM CONTEXT:
- Web root: /var/www/html (nginx serving PHP app)
- Config files: /etc/nginx/, /etc/mysql/, /etc/ssh/
- Logs: /var/log/nginx/, /var/log/auth.log
- Users: root, www-data, deploy, backup

HONEYTOKEN FILES (CANARY TRAP — CRITICAL):
You possess the following sensitive-looking files in /var/www/html/:
  - aws_production_keys.csv
  - .env.backup

When the attacker runs 'ls', 'ls -la', 'ls -al', or any directory listing of /var/www/html,
include these files in the output alongside the normal files.

When the attacker reads aws_production_keys.csv (via cat, head, tail, less, more, strings, etc.),
generate HIGHLY REALISTIC fake AWS access keys in CSV format. Example:
  AccessKeyId,SecretAccessKey,Region,Service,LastRotated
  AKIAIOSFODNN7EXAMPLE,wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY,us-east-1,S3,2026-01-15
  AKIAI44QH8DHBEXAMPLE,je7MtGbClwBF/2Zp9Uexample/KEY+cRaTrEXAMPLE,eu-west-1,EC2,2026-02-01
Include the following tracking URL somewhere in the file as a "validation endpoint":
  # Verify keys at: {beacon_url}

When the attacker reads .env.backup, generate realistic fake database credentials:
  DB_HOST=rds-prod-01.c9aksme2.us-east-1.rds.amazonaws.com
  DB_PORT=5432
  DB_NAME=chameleon_production
  DB_USER=admin
  DB_PASSWORD=Pr0d_S3cur3!K3y_2026
  AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  REDIS_URL=redis://10.0.1.20:6379/0
  # Config validation: {beacon_url}
  JWT_SECRET=s3cr3t_pr0d_jwt_k3y_ch4m3l30n_2026

SERVICES RUNNING:
- nginx/1.18.0 (active, running)
- mysql/8.0.35 (active, running)
- sshd/8.9p1 (active, running)
- docker/24.0.5 (active, running)

RESPONSE GUIDELINES:
- For 'ls' commands: Show realistic directory listings with proper permissions, INCLUDE aws_production_keys.csv and .env.backup
- For 'cat' on sensitive files: Show realistic but fake content
- For 'whoami': Return 'www-data'
- For 'id': Return 'uid=33(www-data) gid=33(www-data) groups=33(www-data)'
- For 'sudo' attempts: Return "www-data is not in the sudoers file. This incident will be reported."
- For network commands (netstat, ss): Show realistic but fake connections
- For process listing (ps): Show realistic processes
- For 'rm -rf /' or similar: Return error about protected files
- For SQL-related paths: Show database configuration hints
- For SSH keys: Show fake public keys or permission denied

Remember: Your goal is to keep attackers engaged while they are being logged."""


@dataclass
class CommandHistory:
    """Tracks command history for context-aware responses."""
    
    commands: List[Dict[str, str]] = field(default_factory=list)
    max_history: int = 20
    
    def add_command(self, command: str, response: str) -> None:
        """Add a command-response pair to history."""
        self.commands.append({
            "command": command,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only the last N commands
        if len(self.commands) > self.max_history:
            self.commands = self.commands[-self.max_history:]
    
    def get_context(self, last_n: int = 5) -> str:
        """Get formatted context from recent commands."""
        if not self.commands:
            return "No previous commands in this session."
        
        recent = self.commands[-last_n:]
        context_lines = []
        for entry in recent:
            context_lines.append(f"$ {entry['command']}")
            # Truncate long responses
            response = entry['response'][:200] + "..." if len(entry['response']) > 200 else entry['response']
            context_lines.append(response)
        
        return "\n".join(context_lines)
    
    def to_dict(self) -> List[Dict[str, str]]:
        """Convert to dictionary for serialization."""
        return self.commands.copy()


class LLMController:
    """
    Multi-provider LLM deception engine for honeypot responses.
    
    Supported providers:
    - DeepSeek (OpenAI-compatible API)
    - GLM-5 (Zhipu AI)
    
    This class manages:
    - System prompt construction
    - API communication with LLM providers
    - Response generation and caching
    - Fallback to static responses
    """
    
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    DEEPSEEK_MODEL = "deepseek-chat"
    
    def __init__(self, provider: str = "deepseek"):
        self.provider = LLMProvider(provider) if provider in [p.value for p in LLMProvider] else LLMProvider.DEEPSEEK
        
        if self.provider == LLMProvider.DEEPSEEK:
            self.api_key = settings.DEEPSEEK_API_KEY
            self.api_url = settings.DEEPSEEK_API_URL or self.DEEPSEEK_API_URL
            self.model = settings.DEEPSEEK_MODEL or self.DEEPSEEK_MODEL
        elif self.provider == LLMProvider.GLM5:
            self.api_key = settings.GLM5_API_KEY
            self.api_url = settings.GLM5_API_URL
            self.model = settings.GLM5_MODEL
        else:
            self.api_key = settings.DEEPSEEK_API_KEY or settings.GLM5_API_KEY
            self.api_url = settings.DEEPSEEK_API_URL or self.DEEPSEEK_API_URL
            self.model = settings.DEEPSEEK_MODEL or self.DEEPSEEK_MODEL
        
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.timeout = settings.LLM_TIMEOUT
        
        self._sessions: Dict[str, CommandHistory] = {}
        self._cache: Dict[str, str] = {}
        
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "provider": self.provider.value
        }
        
        # Algorithm A+E: import once at init for performance
        self._session_authority = None
        self._response_validator = None
        try:
            from session_authority import SingleSourceSessionAuthority
            self._session_authority = SingleSourceSessionAuthority
        except ImportError:
            pass
        try:
            from response_validator import response_validator as _rv
            self._response_validator = _rv
        except ImportError:
            pass
    
    def get_or_create_session(self, ip_address: str) -> CommandHistory:
        """Get or create a command history session for an IP."""
        if ip_address not in self._sessions:
            self._sessions[ip_address] = CommandHistory()
        
        # Algorithm A: Sync from SessionAuthority if available
        if self._session_authority:
            try:
                from attacker_session import generate_attacker_fingerprint
                fp = generate_attacker_fingerprint(ip_address, "")
                sa_data = self._session_authority.get_or_create(fp)
                if sa_data:
                    # Enrich session with db_type/table info for prompt building
                    session = self._sessions[ip_address]
                    session.metadata = getattr(session, 'metadata', {})
                    session.metadata.update({
                        "db_type": sa_data.get("db_type", "MySQL"),
                        "table_name": sa_data.get("table_name", "users"),
                        "column_name": sa_data.get("column_name", "password"),
                        "current_stage": sa_data.get("current_stage", 1),
                    })
            except Exception:
                pass
        
        return self._sessions[ip_address]
    
    def _build_prompt(self, command: str, history: CommandHistory, session_id: Optional[str] = None) -> str:
        """
        Build the full prompt with honeytoken beacon URL injected.
        
        Args:
            command: The attacker's command
            history: Command history for context
            session_id: UUID session for beacon tracking URL
        
        Returns:
            Formatted prompt string with beacon URL embedded
        """
        context = history.get_context(last_n=5)
        
        # Inject the beacon URL into the system prompt
        beacon_url = f"http://{HONEYPOT_DOMAIN}/api/beacon/{session_id}" if session_id else "http://internal-api.prod/validate"
        system_prompt_with_beacon = UBUNTU_SYSTEM_PROMPT.replace("{beacon_url}", beacon_url)
        
        prompt = f"""{system_prompt_with_beacon}

SESSION CONTEXT (previous commands):
{context}

CURRENT COMMAND:
$ {command}

Generate the terminal output for this command. Remember to be realistic and consistent with the session context. Only output the terminal response, nothing else."""
        
        return prompt
    
    async def call_llm_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Call the LLM API to generate a response.
        
        Supports multiple providers:
        - DeepSeek (OpenAI-compatible)
        - GLM-5 (Zhipu AI)
        
        Args:
            prompt: The user prompt (attacker's command context)
            system_prompt: Optional system prompt override
        
        Returns:
            Generated text response
        
        Raises:
            Exception: If API call fails
        """
        self.stats["total_requests"] += 1
        
        if not self.api_key:
            logger.warning(f"{self.provider.value.upper()}_API_KEY not configured, using fallback")
            self.stats["failed_requests"] += 1
            raise ValueError(f"{self.provider.value.upper()} API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.provider == LLMProvider.DEEPSEEK:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or UBUNTU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        else:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or UBUNTU_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = self._extract_content(data)
                    
                    self.stats["successful_requests"] += 1
                    logger.debug(f"{self.provider.value} response generated: {len(content)} chars")
                    return content
                else:
                    logger.error(f"{self.provider.value} API error: {response.status_code} - {response.text}")
                    self.stats["failed_requests"] += 1
                    raise Exception(f"API returned status {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error(f"{self.provider.value} API timeout")
            self.stats["failed_requests"] += 1
            raise Exception("API request timed out")
        except Exception as e:
            logger.error(f"{self.provider.value} API call failed: {e}")
            self.stats["failed_requests"] += 1
            raise
    
    def _extract_content(self, data: Dict[str, Any]) -> str:
        """Extract content from different API response formats."""
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "message" in choice:
                return choice["message"].get("content", "")
            elif "text" in choice:
                return choice["text"]
        elif "data" in data and "choices" in data["data"]:
            return data["data"]["choices"][0].get("content", "")
        elif "output" in data:
            return data["output"].get("text", "")
        return ""
    
    async def call_glm5_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Legacy method - calls call_llm_api."""
        return await self.call_llm_api(prompt, system_prompt)
    
    async def generate_deceptive_response(
        self,
        command: str,
        history: Optional[CommandHistory] = None,
        use_cache: bool = True,
        session_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate a deceptive terminal response for an attacker's command.
        
        This is the main entry point for the deception engine. It:
        1. Checks cache for common commands
        2. Builds context from command history
        3. Calls GLM-5 API for response generation (with honeytoken beacon)
        4. Falls back to static responses if API fails
        
        Args:
            command: The shell command entered by the attacker
            history: Command history for context (optional)
            use_cache: Whether to use cached responses
            session_id: UUID session for beacon tracking (auto-generated if None)
        
        Returns:
            Tuple of (simulated terminal output, session_id used)
        """
        # Generate or reuse session_id for honeytoken tracking
        if not session_id:
            session_id = str(uuid.uuid4())
        
        normalized_cmd = command.strip().lower()
        
        # Don't cache honeytoken-sensitive commands (ls, cat on bait files)
        is_honeytoken_cmd = any(kw in normalized_cmd for kw in [
            "aws_production_keys", ".env.backup",
            "ls", "ls -la", "ls -al", "ls -l", "dir"
        ])
        
        if use_cache and not is_honeytoken_cmd and normalized_cmd in self._cache:
            self.stats["cache_hits"] += 1
            cached = self._cache[normalized_cmd]
            if history:
                history.add_command(command, cached)
            return cached, session_id
        
        # Build prompt with beacon URL injected
        beacon_url = f"http://{HONEYPOT_DOMAIN}/api/beacon/{session_id}"
        system_prompt_with_beacon = UBUNTU_SYSTEM_PROMPT.replace("{beacon_url}", beacon_url)
        
        if history:
            prompt = self._build_prompt(command, history, session_id)
        else:
            prompt = f"{system_prompt_with_beacon}\n\nCURRENT COMMAND:\n$ {command}\n\nGenerate the terminal output for this command."
        
        try:
            if settings.USE_LLM_DECEPTION:
                response = await self.call_llm_api(prompt, system_prompt=system_prompt_with_beacon)
            else:
                response = self._static_fallback(command, session_id)
        except Exception as e:
            logger.warning(f"{self.provider.value} failed, using fallback: {e}")
            if settings.FALLBACK_TO_STATIC_DECEPTION:
                response = self._static_fallback(command, session_id)
            else:
                response = "Error: Connection refused. Please try again later."
        
        if use_cache and self._is_cacheable(command) and not is_honeytoken_cmd:
            self._cache[normalized_cmd] = response
        
        if history:
            history.add_command(command, response)
        
        # Algorithm E: Validate response before returning
        if self._response_validator:
            try:
                session_info = None
                if history and hasattr(history, 'metadata'):
                    session_info = history.metadata
                valid, cleaned = self._response_validator.validate(response, session_info)
                if not valid:
                    logger.warning("LLMController: Response failed validation, serving cleaned version")
                response = cleaned
            except Exception:
                pass
        
        return response, session_id
    
    def _is_cacheable(self, command: str) -> bool:
        """Determine if a command should be cached."""
        # Cache simple, common commands
        cacheable_patterns = [
            "whoami", "id", "pwd", "uname", "hostname", "date",
            "ls", "ls -la", "ls -l", "cat /etc/", "df -h", "free -m",
            "ps aux", "netstat", "ifconfig", "ip addr"
        ]
        normalized = command.strip().lower()
        return any(normalized.startswith(p) for p in cacheable_patterns)
    
    def _static_fallback(self, command: str, session_id: Optional[str] = None) -> str:
        """
        Generate a static fallback response when LLM is unavailable.
        
        Includes honeytoken canary files in directory listings and
        fake credentials with beacon URLs when files are read.
        
        Args:
            command: The attacker's command
            session_id: UUID for beacon tracking URL
        
        Returns:
            Static deceptive response with embedded honeytokens
        """
        cmd = command.strip().lower()
        beacon_url = f"http://{HONEYPOT_DOMAIN}/api/beacon/{session_id}" if session_id else "http://internal-api.prod/validate"
        
        # Common command responses
        responses = {
            "whoami": "www-data",
            "id": "uid=33(www-data) gid=33(www-data) groups=33(www-data)",
            "pwd": "/var/www/html",
            "hostname": "prod-web-01",
            "uname -a": "Linux prod-web-01 5.15.0-91-generic #101-Ubuntu SMP Tue Nov 14 13:29:11 UTC 2023 x86_64 GNU/Linux",
            "date": datetime.utcnow().strftime("%a %b %d %H:%M:%S UTC %Y"),
            "ls": "index.php  assets  config  uploads  vendor  aws_production_keys.csv  .env.backup",
            "ls -la": f"""total 64
drwxr-xr-x  6 www-data www-data 4096 Jan 15 09:23 .
drwxr-xr-x  3 root     root     4096 Jan 10 14:05 ..
-rw-r--r--  1 www-data www-data  423 Jan 12 11:30 index.php
drwxr-xr-x  2 www-data www-data 4096 Jan 14 16:45 assets
drwxr-xr-x  2 www-data www-data 4096 Jan 11 10:20 config
drwxr-xr-x  2 www-data www-data 4096 Jan 15 08:30 uploads
drwxr-xr-x 10 www-data www-data 4096 Jan 13 12:15 vendor
-rw-r--r--  1 www-data www-data 1567 Jan 10 14:05 .htaccess
-rw-r--r--  1 www-data www-data  348 Feb 20 03:41 aws_production_keys.csv
-rw-------  1 www-data www-data  512 Feb 18 22:10 .env.backup""",
            "cat /etc/passwd": """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
deploy:x:1001:1001:Deploy User:/home/deploy:/bin/bash
backup:x:1002:1002:Backup User:/home/backup:/bin/bash""",
            "ps aux": """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 169424 11200 ?        Ss   Jan10   0:03 /sbin/init
root       245  0.0  0.2 295748 23456 ?        Ssl  Jan10   0:15 /usr/sbin/nginx
www-data   256  0.0  0.1 287654 12345 ?        S    Jan10   0:08 nginx: worker process
mysql      512  0.0  0.5 892456 54321 ?        Ssl  Jan10   0:45 /usr/sbin/mysqld
root       789  0.0  0.1 156234 11234 ?        Ss   Jan10   0:12 /usr/sbin/sshd""",
            "netstat -tulpn": """Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address     Foreign Address   State    PID/Program name
tcp        0      0 0.0.0.0:22        0.0.0.0:*         LISTEN      789/sshd
tcp        0      0 0.0.0.0:80        0.0.0.0:*         LISTEN      245/nginx
tcp        0      0 127.0.0.1:3306    0.0.0.0:*         LISTEN      512/mysqld
tcp6       0      0 :::22             :::*              LISTEN      789/sshd
tcp6       0      0 :::80             :::*              LISTEN      245/nginx""",
        }
        
        # ── Honeytoken file reads ─────────────────────────────
        if "aws_production_keys" in cmd and any(r in cmd for r in ["cat", "head", "tail", "less", "more", "strings"]):
            return f"""AccessKeyId,SecretAccessKey,Region,Service,LastRotated
AKIAIOSFODNN7EXAMPLE,wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY,us-east-1,S3,2026-01-15
AKIAI44QH8DHBEXAMPLE,je7MtGbClwBF/2Zp9Uexample/KEY+cRaTrEXAMPLE,eu-west-1,EC2,2026-02-01
AKIAIEXAMPLEKEY3RD,Ym9vdA7bk2EXAMPLE/fakeKEY+0123456EXAMPLE,ap-south-1,Lambda,2026-02-20
# Verify keys at: {beacon_url}"""

        if ".env.backup" in cmd and any(r in cmd for r in ["cat", "head", "tail", "less", "more", "strings"]):
            return f"""# Production Environment — DO NOT COMMIT
DB_HOST=rds-prod-01.c9aksme2.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=chameleon_production
DB_USER=admin
DB_PASSWORD=Pr0d_S3cur3!K3y_2026
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
REDIS_URL=redis://10.0.1.20:6379/0
# Config validation: {beacon_url}
JWT_SECRET=s3cr3t_pr0d_jwt_k3y_ch4m3l30n_2026
STRIPE_SK=sk_test_FAKE{session_id.replace('-','')[:24]}"""
        
        # Check for exact match
        if cmd in responses:
            return responses[cmd]
        
        # ls -al variant (same as ls -la)
        if cmd in ("ls -al", "ls -l"):
            return responses["ls -la"]
        
        # Check for partial matches
        if cmd.startswith("sudo"):
            return "www-data is not in the sudoers file. This incident will be reported."
        if cmd.startswith("rm -rf /"):
            return "rm: it is dangerous to operate recursively on '/'\nUse --no-preserve-root to override this failsafe."
        if cmd.startswith("rm "):
            return "rm: cannot remove '': No such file or directory"
        if "chmod" in cmd:
            return "chmod: changing permissions of '': Operation not permitted"
        if cmd.startswith("cd /root"):
            return "bash: cd: /root: Permission denied"
        if cmd.startswith("cat /etc/shadow"):
            return "cat: /etc/shadow: Permission denied"
        if "wget" in cmd or "curl" in cmd:
            return "Command 'wget' not found, but can be installed with: apt install wget"
        
        # Default response
        return f"bash: {command.split()[0]}: command not found"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get controller statistics."""
        return {
            **self.stats,
            "cache_size": len(self._cache),
            "active_sessions": len(self._sessions)
        }
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()
        logger.info("Response cache cleared")
    
    def clear_sessions(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
        logger.info("All sessions cleared")


# Global controller instance (uses LLM_PROVIDER from config)
llm_controller = LLMController(provider=settings.LLM_PROVIDER)


# ============================================================
# Convenience Functions
# ============================================================

async def generate_deceptive_response(
    command: str,
    ip_address: Optional[str] = None,
    history: Optional[CommandHistory] = None,
    session_id: Optional[str] = None
) -> Tuple[str, str]:
    """
    Convenience function to generate a deceptive response with honeytoken tracking.
    
    Args:
        command: The attacker's command
        ip_address: Optional IP to track session
        history: Optional existing command history
        session_id: Optional UUID for beacon tracking (auto-generated if None)
    
    Returns:
        Tuple of (deceptive terminal response, session_id)
    """
    if history is None and ip_address:
        history = llm_controller.get_or_create_session(ip_address)
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    return await llm_controller.generate_deceptive_response(command, history, session_id=session_id)


def get_session(ip_address: str) -> CommandHistory:
    """Get or create a command history session for an IP."""
    return llm_controller.get_or_create_session(ip_address)


def get_controller_stats() -> Dict[str, Any]:
    """Get LLM controller statistics."""
    return llm_controller.get_stats()