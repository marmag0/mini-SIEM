import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from flask import current_app

class DataManager:
    @staticmethod
    def save_logs(host_id, logs_list):
        """
        Saves logs to a Parquet file for forensic analysis.
        Returns the filename if successful, None otherwise.
        """
        if not logs_list:
            return None

        # Convert logs_list to DataFrame
        df = pd.DataFrame(logs_list)

        # Generate a unique filename
        # Format: hostID_TIMESTAMP_UUID.parquet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{host_id}_{timestamp}.parquet"
        
        # Get storage path from config
        storage_path = current_app.config.get('STORAGE_PATH', './data/archives')
        full_path = os.path.join(storage_path, filename)

        # Save to Parquet (with compression to save space)
        # Requires: pandas, pyarrow
        try:
            # Ensure directory exists
            os.makedirs(storage_path, exist_ok=True)
            
            df.to_parquet(full_path, engine='pyarrow', compression='snappy')
            print(f"[Forensics] Logs saved to {full_path}")
            return filename
        except Exception as e:
            print(f"[Error] Failed to save parquet: {e}")
            return None

    @staticmethod
    def load_logs(filename):
        """Loads logs from a file for analysis"""
        storage_path = current_app.config.get('STORAGE_PATH', './data/archives')
        full_path = os.path.join(storage_path, filename)
        
        if os.path.exists(full_path):
            return pd.read_parquet(full_path)
        return pd.DataFrame()