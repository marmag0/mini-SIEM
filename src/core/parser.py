import pandas as pd
import re
from datetime import datetime

class LogParser:
    # Patterns for detecting security events
    PATTERNS = {
        'ssh_failed': r"Failed password for (invalid user )?(?P<user>\w+) from (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        'ssh_success': r"Accepted password for (?P<user>\w+) from (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    }

    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        """
        Opens a Parquet file and returns a list of detected security events.
        """
        detected_events = []
        
        try:
            # Load Parquet file
            df = pd.read_parquet(self.filepath)
            
            # Iterate through log entries
            for index, row in df.iterrows():
                message = row.get('message', '')
                timestamp = row.get('timestamp') # Linux timestamp
                
                # Check each pattern
                for event_type, pattern in self.PATTERNS.items():
                    match = re.search(pattern, message)
                    if match:
                        # Extract relevant data
                        data = match.groupdict()
                        
                        event = {
                            'timestamp': datetime.fromtimestamp(float(timestamp)),
                            'type': event_type, # np. 'ssh_failed'
                            'source_ip': data.get('ip'),
                            'target_user': data.get('user'),
                            'raw_text': message
                        }
                        detected_events.append(event)
                        
        except Exception as e:
            print(f"[Parser Error] {e}")
            
        return detected_events