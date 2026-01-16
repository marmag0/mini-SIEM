import pandas as pd
import re
from datetime import datetime
import sys

class LogParser:
    # Regex patterns for detecting events
    PATTERNS = {
        'ssh_failed': r"Failed\s+password\s+for\s+(?:invalid\s+user\s+)?(?P<user>\S+)\s+from\s+(?P<ip>[\d\.]+)"
    }

    def __init__(self, filepath):
        self.filepath = filepath

    def clean_text(self, text):
        """Remove ANSI codes and extra spaces from text."""
        if not isinstance(text, str):
            text = str(text)
        # Remove ANSI escape sequences
        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
        # Replace tabs and multiple spaces with single spaces
        return " ".join(text.split())

    def parse(self):
        detected_events = []
        try:
            df = pd.read_parquet(self.filepath)
            if df.empty:
                return []

            for _, row in df.iterrows():
                # Clean the log message
                message = self.clean_text(row.get('message', ''))
                
                # Extract and convert timestamp
                raw_ts = row.get('timestamp', 0)
                try:
                    ts_val = float(raw_ts)
                    if ts_val > 9999999999: ts_val /= 1000000.0
                    event_time = datetime.fromtimestamp(ts_val)
                except:
                    event_time = datetime.utcnow()

                for event_type, pattern in self.PATTERNS.items():
                    # Match the pattern
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        data = match.groupdict()
                        print(f"✅ [PARSER]: {data['user']} IP: {data['ip']}", file=sys.stdout)
                        
                        detected_events.append({
                            'timestamp': event_time,
                            'type': event_type,
                            'source_ip': data['ip'],
                            'target_user': data['user'],
                            'raw_text': message
                        })
        except Exception as e:
            print(f"[PARSER ERROR] {e}", file=sys.stdout)
            
        return detected_events