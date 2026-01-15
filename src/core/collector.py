import paramiko
import json
import time
from datetime import datetime

class LogCollector:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def fetch_logs(self, host, last_fetch_time=None):
        """
        Fetches logs from a remote host via SSH using Cloudflare Tunnel.
        """
        logs = []
        try:
            # 1. Konfiguracja klucza prywatnego
            key_path = '/root/.ssh/id_rsa' 
            my_key = paramiko.RSAKey.from_private_key_file(key_path)

            # Configure Cloudflare Tunnel as a proxy
            sock = paramiko.ProxyCommand(f"cloudflared access ssh --hostname {host.ip_address}")

            # 3. Connecting to the host
            print(f"[SSH] Connecting to {host.ip_address} ({host.name})...")
            self.ssh.connect(
                hostname=host.ip_address,
                username='mikolaj_mazur05',
                pkey=my_key,
                sock=sock
            )

            # 4. Building the command (Incremental Logic)
            # Use journalctl with JSON output
            cmd = "journalctl -u ssh --output=json --no-pager"
            
            if last_fetch_time:
                # Format date for journalctl: "YYYY-MM-DD HH:MM:SS"
                since_str = last_fetch_time.strftime("%Y-%m-%d %H:%M:%S")
                cmd += f' --since "{since_str}"'
            else:
                # Default to last 100 lines on first run
                cmd += " -n 100"

            print(f"[SSH] Executing: {cmd}")
            stdin, stdout, stderr = self.ssh.exec_command(cmd)

            # 5. Parsing results
            for line in stdout:
                try:
                    entry = json.loads(line)
                    # Data normalization
                    logs.append({
                        'timestamp': entry.get('__REALTIME_TIMESTAMP', time.time()), # Timestamp from Linux
                        'message': entry.get('MESSAGE', ''),
                        'hostname': entry.get('_HOSTNAME', host.name),
                        'raw': line.strip()
                    })
                except json.JSONDecodeError:
                    continue
            
            self.ssh.close()
            return logs

        except Exception as e:
            print(f"[SSH Error] {e}")
            return []