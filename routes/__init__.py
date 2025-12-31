from .main import main_bp
from .api import api_bp
# from .auth import auth_bp  # Eğer auth ekleyecekseniz

def init_routes(app):
    """Tüm route blueprint'lerini app'e kaydet"""
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    # app.register_blueprint(auth_bp, url_prefix='/auth')