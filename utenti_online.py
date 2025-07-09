import time
from flask import request
import re

# Dizionario in memoria: {ip: (timestamp_ultimo_accesso, sistema_operativo)}
utenti_attivi = {}

# Timeout in secondi per considerare un utente "online" (es: 5 minuti)
TIMEOUT = 300

def estrai_sistema_operativo(user_agent):
    # Semplice estrazione del sistema operativo dal campo User-Agent
    if not user_agent:
        return "?"
    ua = user_agent.lower()
    if "android" in ua:
        return "Android"
    if "iphone" in ua or "ipad" in ua:
        return "iOS"
    if "windows" in ua:
        return "Windows"
    if "mac os" in ua or "macintosh" in ua:
        return "MacOS"
    if "linux" in ua:
        return "Linux"
    return "Altro"

def aggiorna_utente_online():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    sistema = estrai_sistema_operativo(user_agent)
    utenti_attivi[ip] = (time.time(), sistema)

def conta_utenti_online():
    now = time.time()
    utenti_vivi = {ip: (ts, so) for ip, (ts, so) in utenti_attivi.items() if now - ts < TIMEOUT}
    utenti_attivi.clear()
    utenti_attivi.update(utenti_vivi)
    return len(utenti_attivi)

def get_ip_attivi(secondi=180):
    now = time.time()
    # Restituisce lista di tuple (ip, sistema operativo)
    return [(ip, so) for ip, (ts, so) in utenti_attivi.items() if now - ts < secondi] 