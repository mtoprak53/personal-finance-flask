import os
from .base import Config

class DevelopmentConfig(Config):
    """Geliştirme ortamı config"""
    
    DEBUG = True
    DEVELOPMENT = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://finans_user:finans123@localhost/finans_db'
        # 'postgresql://finans_dev:dev123@localhost/finans_dev'
    
    # Security (development'ta gevşek)
    FORCE_HTTPS = False
    ENABLE_CSP = False
    
    # Development için özel header'lar
    SECURITY_HEADERS = {
        'X-Robots-Tag': 'noindex, nofollow',  # Search engine'ları engelle
    }
    
    # Security (development'ta daha gevşek)
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Email (development için mock)
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = True
    
    # CORS (development'ta tüm origin'lere izin ver)
    CORS_ORIGINS = ['*']
    
    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Development-specific initializations
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
        
        print("🚀 Development mode activated")