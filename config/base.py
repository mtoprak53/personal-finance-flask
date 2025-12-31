import os
import secrets
from datetime import timedelta

class Config:
    """Tüm config'ler için base class"""
    
    # DEBUG
    DEBUG = False
    TESTING = False
    
    # SECURITY
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # SESSION
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # SECURITY HEADERS
    # SECURITY
    SECURITY_HEADERS = {}  # Boş, default'lar kullanılacak
    FORCE_HTTPS = False    # Production'da True yapın
    ENABLE_CSP = False     # Dikkat: CSP'yi test etmeden açmayın
    
    # APP SPECIFIC
    APP_NAME = "Finans Takip"
    APP_VERSION = "1.0.0"
    TIMEZONE = 'America/New_York'
    
    # LOGGING
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # UPLOADS (eğer dosya yükleme ekleyecekseniz)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # EMAIL (opsiyonel)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # CACHE (opsiyonel)
    CACHE_TYPE = 'simple'  # 'redis', 'memcached', 'filesystem'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API
    API_PREFIX = '/api/v1'
    API_TITLE = 'Finans API'
    API_VERSION = 'v1'
    
    @staticmethod
    def init_app(app):
        """App initialization"""
        pass