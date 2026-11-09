import os
from flask import Flask, render_template
from flask_login import LoginManager
from datetime import datetime

from config import Config
from models import db, User
from routes.main import main_bp
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.admin import admin_bp
from routes.billing import billing_bp

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar Base de Datos
    db.init_app(app)

    # Inicializar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a TechHelp IA.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(billing_bp)

    # Inyección de variables globales en plantillas Jinja
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.utcnow(),
            'app_name': 'TechHelp IA',
            'support_email': 'soporte@techhelp.ia',
            'free_limit': Config.FREE_TIER_DAILY_LIMIT
        }

    # Manejo de errores amigable
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Inicialización de tablas y usuario administrador por defecto
    with app.app_context():
        db.create_all()
        _init_default_admin(app)

    return app


def _init_default_admin(app):
    """Crea la cuenta de administrador predeterminada si la base de datos está vacía."""
    admin_email = app.config.get('ADMIN_EMAIL', 'admin@techhelp.ia').lower()
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_pass = app.config.get('ADMIN_PASSWORD', 'Admin123456!')
        admin_name = app.config.get('ADMIN_NAME', 'Administrador TechHelp')
        admin = User(
            email=admin_email,
            name=admin_name,
            role='admin',
            subscription_tier='pro',
            subscription_status='active'
        )
        admin.set_password(admin_pass)
        db.session.add(admin)
        db.session.commit()
        print(f"[TechHelp IA] Administrador creado: {admin_email} / {admin_pass}")


app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
