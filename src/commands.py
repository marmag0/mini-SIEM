import click
import os
from flask.cli import with_appcontext
from extensions import db
from models import User

@click.command(name='setup')
@with_appcontext
def setup():
    """Creates database tables and an admin user from .env"""
    
    # Create all database tables
    db.create_all()
    print("Database tables created.")

    # Create admin user from .env
    admin_user = os.environ.get('ADMIN_USER', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin')

    # Check if admin user already exists
    if not User.query.filter_by(username=admin_user).first():
        u = User(username=admin_user)
        # Set hashed password
        u.set_password(admin_pass) 
        db.session.add(u)
        db.session.commit()
        print(f"Added user '{admin_user}' with password from .env")
    else:
        print("Skipping... User admin already exists")