import os
from .base import Config

class TestingConfig(Config):
    """Test ortamı config"""
    
    TESTING = True
    DEBUG = True
    
    # Test database (in-memory SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    
    # Security
    SECRET_KEY = 'test-secret-key'
    SESSION_COOKIE_SECURE = False
    
    # Email
    MAIL_SUPPRESS_SEND = True
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Test-specific
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        print("🧪 Testing mode activated")