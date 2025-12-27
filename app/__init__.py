"""
Application Factory Pattern per Flask
"""
from flask import Flask
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()


def create_app(config_name='default'):
    """Factory function per creare l'applicazione Flask"""
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder='static',
                template_folder='templates')
    
    # Assicurati che la directory instance esista
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Configurazione
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chiave-segreta-cambiami-in-produzione')
    app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME', 'admin')
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'torneo.db')
    
    # Inizializza il database
    from app.models.database import init_db, set_db_path
    db_path = os.path.join(app.instance_path, app.config['DB_NAME'])
    set_db_path(db_path)  # Imposta il percorso per get_db()
    if not os.path.exists(db_path):
        init_db(db_path)
    
    # Registra i blueprints
    from app.routes import main, torneo, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(torneo.bp)
    app.register_blueprint(admin.bp)
    
    return app

