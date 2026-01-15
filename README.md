# mini-SIEM

## Architecture - (High-Level)

1. **SIEM Server**
    - WebApp UI for monitoring
    - Docker Container (SIEM App):
        - Python/Flask
        - Client libraries
    - Docker Volume:
        - maps a local folder to store `.parquet` files (for data persistence)
    - `on dev:` Localhost

2. **Monitored Hosts**
    - Cloudflared (Daemon): running on the VM, creating an outbound tunnel to the Cloudflare network
    - SSH Daemon: listening locally (localhost)
    - `on dev:` Google Cloud Platform VMs

3. **Connectivity**
    - SSH traffic is tunneled through the Cloudflare network (Cloudflare Access/Tunnel)
    - Authentication: mTLS (Client Certificate) or Service Token, verified by Cloudflare before allowing traffic to reach the SSH service

## Project Structure

```
/my-custom-siem
├── docker-compose.yml       # Orchestration
├── Dockerfile               # SIEM Image definition
├── .env                     # Secrets (DB, Cloudflare Tokens)
├── data/                    # Volume for SQLite DB and Parquet files
│   ├── db.sqlite3
│   └── archives/            # Directory where .parquet files will be stored
├── src/                     # Application Source Code
│   ├── app.py               # Entrypoint
│   ├── config.py
│   ├── database.py          # SQLAlchemy Models
│   ├── core/                # Business Logic
│   │   ├── collector.py     # SSH/WMI Logic
│   │   ├── forensics.py     # Parquet Handling
│   │   └── analyzer.py      # Threat Intel Logic
│   └── web/                 # Flask Blueprints and Templates
└── requirements.txt         # List of dependencies
```
