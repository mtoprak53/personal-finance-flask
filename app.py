import os
from flask import Flask, jsonify, request, redirect
from zoneinfo import ZoneInfo
from config import get_config

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Config yükle
    if config_name:
        from config import configs
        config_class = configs.get(config_name)
    else:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Config class'ının init_app metodunu çağır
    config_class.init_app(app)
    
    # Database
    from models import db
    db.init_app(app)
    
    # Timezone (config'ten al)
    import pytz
    from datetime import datetime
    tz = pytz.timezone(app.config.get('TIMEZONE', 'America/New_York'))
    
    # ROUTE'LARI BURADA IMPORT ET VE KAYDET
    from routes import init_routes
    init_routes(app)  # Bu satır tüm route'larınızı app'e kaydedecek
    
    # GÜVENLİK HEADER'LARINI AYARLA
    setup_security_headers(app)
    

    # Context processor (tüm template'lere değişken ekle)
    @app.context_processor
    def inject_vars():
        return {
            'app_name': app.config.get('APP_NAME', 'Finans Takip'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'timezone': app.config.get('TIMEZONE', 'America/New_York'),
            'current_time': datetime.now(tz),
        }
    
    
    # Timezone'a göre tarih formatlayan helper
    @app.template_filter('localtime')
    def localtime_filter(value, format='%Y-%m-%d %H:%M:%S'):
        if value is None:
            return ''
        if isinstance(value, str):
            # String'den datetime'a çevir
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                return value
        
        # UTC zamanını config'teki timezone'a çevir
        if value.tzinfo is None:
            # Naive datetime ise, UTC olduğunu varsay
            utc_time = pytz.utc.localize(value)
        else:
            utc_time = value
        
        local_time = utc_time.astimezone(tz)
        return local_time.strftime(format)
    

    # Request handlers
    @app.before_request
    def before_request():
        """Her request'ten önce çalışır"""
        pass
    

    # HTTPS yönlendirmesi (production'da)
    if app.config.get('FORCE_HTTPS', False):
        @app.before_request
        def force_https():
            """HTTP'yi HTTPS'ye yönlendir (sadece production'da)"""
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, code=301)
    

    # Health check endpoint (Railway için)
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy', 
            'time': datetime.now(tz).isoformat(),
            'environment': app.config.get('ENV', 'unknown'),
            'app': app.config.get('APP_NAME', 'Finans Takip')
        })
    
    return app


def setup_security_headers(app):
    """Güvenlik header'larını config'e göre ayarla"""
    
    # Default security headers (tüm environment'lar için)
    default_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
    }
    
    # Production için ek header'lar
    if app.config.get('ENV') == 'production' or app.config.get('FLASK_ENV') == 'production':
        default_headers.update({
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Cross-Origin-Opener-Policy': 'same-origin',
            'Cross-Origin-Resource-Policy': 'same-origin'
        })
        
        # CSP (Content Security Policy) - production'da aktif
        # Not: CSP aktif etmek siteyi kırabilir, test etmelisiniz
        if app.config.get('ENABLE_CSP', False):
            default_headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
    
    # Config'den override al (eğer varsa)
    config_headers = app.config.get('SECURITY_HEADERS', {})
    security_headers = {**default_headers, **config_headers}
    
    @app.after_request
    def add_security_headers(response):
        """Tüm response'lara güvenlik header'ları ekle"""
        for header, value in security_headers.items():
            # Header zaten eklenmemişse ekle
            if header not in response.headers:
                response.headers[header] = value
        return response
    
    return app


# Mevcut app instance'ını oluştur
app = create_app()

if __name__ == '__main__':
    # Environment kontrolü (opsiyonel)
    try:
        from utils.env_checker import EnvironmentChecker
        EnvironmentChecker.check()
    except ImportError:
        print("⚠️  EnvironmentChecker not found, skipping environment check")
    
    port = int(os.environ.get('PORT', 5000))
    # debug = os.getenv('FLASK_DEBUG', '0') == '1'    # Eskisi
    debug = app.config.get('DEBUG', False)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )