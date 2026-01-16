import pandas as pd
import re
from datetime import datetime, timezone
import sys

class LogParser:
    PATTERNS = {
        'ssh_failed': r"(?:Failed password|Connection closed by authenticating user|Connection closed by)\s+(?:for\s+)?(?:invalid\s+user\s+)?(?P<user>\S+)\s+(?:from\s+)?(?P<ip>[\d\.]+)",
        'ssh_success': r"Accepted\s+(?:password|publickey)\s+for\s+(?P<user>\S+)\s+from\s+(?P<ip>[\d\.]+)"
    }

    def __init__(self, filepath):
        self.filepath = filepath

    def clean_text(self, text):
        """Poprawione dekodowanie bajtów i czyszczenie tekstu."""
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        if not isinstance(text, str):
            text = str(text)
        
        # ANSI escape codes removal
        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        return " ".join(text.split())

    def parse(self):
        detected_events = []
        try:
            df = pd.read_parquet(self.filepath)
            if df.empty: return []

            msg_col = 'message' if 'message' in df.columns else 'MESSAGE'

            for _, row in df.iterrows():
                message = self.clean_text(row.get(msg_col, ""))
                if not message: continue

                raw_ts = row.get('timestamp')
                if raw_ts and not pd.isna(raw_ts):
                    dt_object = datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
                else:
                    dt_object = datetime.now(timezone.utc)

                for event_type, pattern in self.PATTERNS.items():
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        data = match.groupdict()
                        
                        print(f"DEBUG HIT: {event_type} | User: {data['user']} | IP: {data['ip']}", file=sys.stdout)
                        
                        severity = "INFO"
                        if event_type == 'ssh_failed':
                            severity = "CRITICAL" if data['user'] == 'root' else "WARNING"

                        detected_events.append({
                            'timestamp': dt_object,
                            'type': event_type,
                            'severity': severity,
                            'source_ip': data['ip'],
                            'target_user': data['user'],
                            'message': message
                        })
        except Exception as e:
            print(f"[PARSER ERROR] {e}", file=sys.stdout)
            
        return detected_events