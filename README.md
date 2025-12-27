# Torneo App - Applicazione Flask per Gestione Torneo

Applicazione web per la gestione di un torneo di calcio, sviluppata con Flask e SQLite.

## Quick Start

### 1. Installazione

```bash
# Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Configurazione

Il file `.env` è già presente con le configurazioni di default. 

⚠️ **IMPORTANTE**: Cambia `ADMIN_PASSWORD` e `SECRET_KEY` prima di andare in produzione!

Per generare una nuova SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Migrazione Dati (se necessario)

Se hai bisogno di migrare dati dall'Excel:
```bash
python migrations/migrate_excel_to_db.py
```

### 4. Avvio

```bash
python run.py
```

L'applicazione sarà disponibile su `http://localhost:1234`

## Struttura del Progetto

```
torneoapp/
├── app/                    # Package principale
│   ├── routes/            # Blueprints (main, torneo, admin)
│   ├── models/            # Database e query
│   ├── utils/             # Utilities
│   ├── static/            # CSS, JS, immagini
│   └── templates/         # Template Jinja2
├── instance/              # Database e file locali (ignorato da Git)
├── migrations/            # Script di migrazione
├── docs/                  # Documentazione
├── data/backup/           # Backup file Excel
├── .env                   # Configurazione (NON committare!)
├── run.py                 # Entry point
└── requirements.txt       # Dipendenze
```

## Area Admin

Accedi su `/admin` con:
- Username: `admin` (configurabile in `.env`)
- Password: `admin123` (configurabile in `.env`)

## Variabili d'Ambiente

Vedi `.env.example` per tutte le variabili disponibili.

Variabili principali:
- `SECRET_KEY`: Chiave segreta Flask
- `ADMIN_USERNAME`: Username admin
- `ADMIN_PASSWORD`: Password admin
- `FLASK_DEBUG`: Modalità debug (False in produzione)
- `FLASK_HOST`: Host server
- `FLASK_PORT`: Porta server
- `DB_NAME`: Nome database

## Documentazione

Vedi la directory `docs/` per la documentazione completa:
- [Guida migrazione database](docs/MIGRAZIONE_DATABASE.md)
- [Istruzioni deploy](docs/ISTRUZIONI_GIT_DEPLOY.txt)

## Deployment

### Fly.io / Heroku

1. Configura variabili d'ambiente dal pannello
2. Imposta `FLASK_DEBUG=False`
3. Usa gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:$PORT run:app
```

## Note

- Il database viene creato automaticamente in `instance/` al primo avvio
- Il file Excel in `data/backup/` è solo per riferimento
- Mantieni `.env` privato e non committarlo
