import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """
    Health Check
    """
    storage_path = os.environ.get('STORAGE_PATH', './data')
    storage_exists = os.path.exists(storage_path)
    
    python_version = sys.version

    return jsonify({
        "status": "SIEM Online",
        "app_name": "Mini-SIEM",
        "python_version": python_version,
        "forensics_storage": {
            "path": storage_path,
            "exists": storage_exists,
            "writable": os.access(storage_path, os.W_OK) if storage_exists else False
        },
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)