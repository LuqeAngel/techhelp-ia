"""
Script para inicializar o resetear la base de datos de TechHelp IA.
Uso:
    python init_db.py
"""
import sys
from app import create_app
from models import db, User, Conversation, Message

app = create_app()

def init():
    with app.app_context():
        print("[*] Creando tablas en la base de datos...")
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"[✓] Administrador activo: {admin.email}")
        else:
            print("[!] Creando administrador por defecto...")
        print("[✓] Base de datos SQLite lista para usar.")

if __name__ == '__main__':
    init()
