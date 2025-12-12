import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '7tk50zd4sv13x9wytj2q7g9hi0j1d4nr8vzgna20go77k5xmq2x2svyidbeykioi')

    # SQLite Database
    # Database Configuration (SQLite Local, PostgreSQL Prod)
    DATABASE_PATH = os.path.join(BASE_DIR, "inventory.db")
    # Render provides 'DATABASE_URL', but SQLAlchemy requires 'postgresql://', not 'postgres://'
    uri = os.environ.get("DATABASE_URL", "sqlite:///" + DATABASE_PATH)
    if uri and uri.startswith("postgres"):
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        
        # Ensure SSL mode is enabled for Koyeb/Neon
        if "sslmode" not in uri:
            if "?" in uri:
                uri += "&sslmode=require"
            else:
                uri += "?sslmode=require"
        
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pagination
    ITEMS_PER_PAGE = 6

    # Mail Configuration
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    
    # Email Credentials
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'afifjouili9@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Papa22030671')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'afifjouili9@gmail.com')
    
    # Security
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'security-password-salt')
