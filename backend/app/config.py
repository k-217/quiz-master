import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    # flask session and csrf protection
    SECRET_KEY = os.getenv('SECRET_KEY')

    # flask app
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    DEBUG = os.getenv('DEBUG')

    # flask_sqlalchemy    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), os.getenv('DATABASE_NAME'))}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_NAME = os.getenv('ADMIN_NAME')
    ADMIN_QUALIFICATION = os.getenv('ADMIN_QUALIFICATION')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

    # caching    
    CACHE_TYPE = os.getenv('CACHE_TYPE')
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('CACHE_REDIS_PORT')
    
    # celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    
    # flask_security
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_REGISTERABLE = True
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USER_IDENTITY_ATTRIBUTES = [{'username': {'mapper': None, 'case_insensitive': False}}]
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_EMAIL_SENDER = os.getenv('MAIL_USERNAME')
    SECURITY_CONFIRMABLE = False # change to True for required email confirmation by the user, then also add confirmed_at attribute to User model
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    SECURITY_TOKEN_IDENTIFICATION_HEADER = "Authentication-Token"

    # mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    WTF_CSRF_ENABLED = False

# handle errors for missing values in .env file