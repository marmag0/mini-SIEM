from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Host

# API Blueprint for Host Management
hosts_bp = Blueprint('hosts_api', __name__, url_prefix='/api/hosts')

@hosts_bp.route('/', methods=['GET'])
@login_required
def get_hosts():
    """Retrieves the list of monitored hosts in JSON format"""
    hosts = Host.query.all()
    data = []
    for h in hosts:
        data.append({
            'id': h.id,
            'name': h.name,
            'ip': h.ip_address,
            'os': h.os_type,
            'status': 'unknown' # TODO status online/offline 
        })
    return jsonify(data), 200

@hosts_bp.route('/', methods=['POST'])
@login_required
def add_host():
    """Adds a new monitored host"""
    data = request.get_json()
    
    # Simple validation
    if not data or not data.get('name') or not data.get('ip'):
        return jsonify({'error': 'Missing name or IP address'}), 400
    
    # Check for duplicate host name
    if Host.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Host with this name already exists'}), 409

    # Add to database
    new_host = Host(
        name=data['name'],
        ip_address=data['ip'],
        os_type=data.get('os', 'linux')
    )
    db.session.add(new_host)
    db.session.commit()

    return jsonify({'message': 'Host added successfully', 'id': new_host.id}), 201

@hosts_bp.route('/<int:host_id>', methods=['DELETE'])
@login_required
def delete_host(host_id):
    """Deletes a monitored host by ID"""
    host = db.session.get(Host, host_id)
    if not host:
        return jsonify({'error': 'Host not found'}), 404
        
    db.session.delete(host)
    db.session.commit()
    return jsonify({'message': 'Host deleted successfully'}), 200