import time
from flask import request

# Dizionario in memoria: {ip: timestamp_ultimo_accesso}
utenti_attivi = {}

# Timeout in secondi per considerare un utente "online" (es: 5 minuti)
TIMEOUT = 300

def aggiorna_utente_online():
    ip = request.remote_addr
    utenti_attivi[ip] = time.time()

def conta_utenti_online():
    now = time.time()
    # Rimuovi utenti "scaduti"
    utenti_vivi = {ip: ts for ip, ts in utenti_attivi.items() if now - ts < TIMEOUT}
    utenti_attivi.clear()
    utenti_attivi.update(utenti_vivi)
    return len(utenti_attivi) 