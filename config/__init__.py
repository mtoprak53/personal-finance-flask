import os
from pathlib import Path
from dotenv import load_dotenv

# Proje kök dizinini bul
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR / 'environments'

def load_environment():
    """Environment dosyalarını yükle"""
    
    # 1. Environment belirle
    env = os.getenv('FLASK_ENV', 'development')
    
    print(f"🔧 Loading environment: {env}")
    
    # 2. Önce genel .env yükle (eğer varsa)
    general_env = ENV_DIR / '.env'
    if general_env.exists():
        load_dotenv(general_env)
        print(f"📁 Loaded: {general_env}")
    
    # 3. Environment-spesifik .env yükle
    env_file = ENV_DIR / f'.env.{env}'
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"📁 Loaded: {env_file}")
    else:
        print(f"⚠️  {env_file} not found")
    
    # 4. Lokal override yükle (eğer varsa)
    local_env = ENV_DIR / '.env.local'
    if local_env.exists():
        load_dotenv(local_env, override=True)
        print(f"📁 Loaded: {local_env} (local overrides)")
    
    # 5. Production'da kritik değişkenleri kontrol et
    if env == 'production':
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(
                f"Missing required environment variables in production: {missing}\n"
                f"Please check: {env_file}"
            )
    
    return env

# Environment'ı yükle
current_env = load_environment()

# Config class'larını import et
from .base import Config
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': ProductionConfig,  # Staging production gibi
    'default': DevelopmentConfig
}

def get_config():
    """Mevcut environment'a göre config döndür"""
    return configs.get(current_env, configs['default'])