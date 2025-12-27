"""
Entry point per l'applicazione Flask
"""
import os
import locale
from dotenv import load_dotenv
from app import create_app

# Carica variabili d'ambiente
load_dotenv()

# Imposta la localizzazione italiana per le date
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT')
    except locale.Error:
        pass  # fallback: non cambiare locale

# Crea l'applicazione
app = create_app()

# Configurazione server
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', '1234'))

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)

