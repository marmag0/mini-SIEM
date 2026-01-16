from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

# IAM & SECURITY
class User(UserMixin, db.Model):
    """
    Table for application users (SIEM operators)
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        """Saves hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies password during login"""
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# ASSET MANAGEMENT
class Host(db.Model):
    """
    Table for monitored hosts (servers/workstations)
    """
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)  # hostname in SIEM
    ip_address = db.Column(db.String(64))  # IP address or Hostname from SSH Config
    os_type = db.Column(db.String(20))     # linux / windows
    
    # relationships
    log_sources = db.relationship('LogSource', backref='host', lazy='dynamic')
    alerts = db.relationship('Alert', backref='host', lazy='dynamic')


# DATA ENGINEERING
class LogSource(db.Model):
    """
    Table for log sources per host (e.g., SSH Auth Logs, Windows Security Events)
    """
    __tablename__ = 'log_sources'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    log_type = db.Column(db.String(32))  # e.g. 'ssh_auth', 'security_event'
    last_fetch = db.Column(db.DateTime, nullable=True) 


# --- 4. FORENSICS (Rejestr Plików Parquet) ---
class LogArchive(db.Model):
    """
    Table for archived log files stored in Parquet format
    """
    __tablename__ = 'log_archives'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    filename = db.Column(db.String(256), nullable=False) # e.g. '1_20260115_1200.parquet'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    record_count = db.Column(db.Integer, default=0)


# --- 5. THREAT INTEL ---
class IPRegistry(db.Model):
    """
    Table for IP address reputation registry
    """
    __tablename__ = 'ip_registry'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(64), unique=True, nullable=False)
    reputation = db.Column(db.String(20), default='UNKNOWN') # UNKNOWN, TRUSTED, BANNED
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# --- 6. ALERTS ---
class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'))
    severity = db.Column(db.String(20)) # INFO, WARNING, CRITICAL
    source_ip = db.Column(db.String(64))  # <---
    target_user = db.Column(db.String(64))  # <---
    message = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)