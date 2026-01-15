from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initializacjon empty instances
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Login configuration
login_manager.login_view = 'auth.login'
login_manager.login_message = "Login, to get access."