from flask import Blueprint, jsonify
from flask_login import login_required
from models import Alert, Host
from extensions import db

alerts_bp = Blueprint('alerts_api', __name__, url_prefix='/api/alerts')

@alerts_bp.route('/stats', methods=['GET'])
@login_required
def get_alert_stats():
    """Retrieves alert statistics grouped by severity"""
    stats_raw = db.session.query(Alert.severity, db.func.count(Alert.id)).group_by(Alert.severity).all()
    
    result = {'CRITICAL': 0, 'WARNING': 0, 'INFO': 0}
    
    for sev, count in stats_raw:
        if sev in result:
            result[sev] = count
            
    return jsonify(result)

@alerts_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_alerts():
    """Retrieves a list of all alerts for the table"""
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(50).all()
    return jsonify([{
        'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'severity': a.severity,
        'host': a.host.name if a.host else 'Unknown',
        'message': a.message
    } for a in alerts])

@alerts_bp.route('/ip-stats', methods=['GET'])
@login_required
def get_ip_threats():
    """Returns IP addresses with more than 10 alerts"""
    from sqlalchemy import func
    
    # Query to find IPs with more than 10 alerts
    results = db.session.query(
        Alert.source_ip, 
        func.count(Alert.id).label('total'),
        func.max(Alert.severity).label('max_severity')
    ).group_by(Alert.source_ip).having(func.count(Alert.id) > 10).all()

    return jsonify([{
        'ip': r.source_ip,
        'count': r.total,
        'severity': r.max_severity
    } for r in results])