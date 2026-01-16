import os
from flask import Flask, render_template
from flask_login import login_required
import api
from extensions import db, migrate, login_manager
from models import User, Host, LogSource, LogArchive, IPRegistry, Alert
from commands import setup
from auth import auth_bp
from api.hosts import hosts_bp
from api.alerts import alerts_bp

def create_app():
    app = Flask(__name__)
    
    # Environment-based configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////app/data/siem.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Extensions initialization
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register CLI commands
    # docker compose exec app flask setup
    app.cli.add_command(setup)

    # Blueprints registration
    app.register_blueprint(auth_bp)
    app.register_blueprint(hosts_bp)
    app.register_blueprint(alerts_bp)

    # Simple route to verify app is running
    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')