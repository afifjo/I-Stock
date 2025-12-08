from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Global extensions (used by blueprints)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

# Where users get redirected when not logged in
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
