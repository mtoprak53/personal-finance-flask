import os
from .base import Config

class ProductionConfig(Config):
    """Production ortamı config"""
    
    DEBUG = False
    TESTING = False
    
    # Security
    FORCE_HTTPS = True
    ENABLE_CSP = False  # Test edene kadar False bırakın
    
    # Production security headers (opsiyonel override)
    SECURITY_HEADERS = {
        # Ek production header'lar buraya
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
    }
    
    # Database (Railway/Heroku PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security (production'da sıkı)
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production!")
    
    # Logging
    LOG_LEVEL = 'WARNING'
    
    # Email (gerçek email)
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = False
    
    # CORS (production'da sınırlı)
    CORS_ORIGINS = [
        'https://finans-app.railway.app',
        'https://www.finansapp.com',  # Custom domain
    ]
    
    # Performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Cache (production için Redis)
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initializations
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/finans_app.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.WARNING)
        app.logger.info('Production startup')