import os
from flask import Flask
from extensions import db, migrate, login_manager
from models import User, Host, LogSource, LogArchive, IPRegistry, Alert
from commands import setup

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
    app.cli.add_command(setup)

    # Simple route to verify app is running
    @app.route('/')
    def index():
        return f"SIEM System Online. Database: {app.config['SQLALCHEMY_DATABASE_URI']}"

    return app

# Entry point for running the app
if __name__ == '__main__':
    app = create_app()