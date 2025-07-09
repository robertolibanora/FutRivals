import time
from flask import request
import re

# Dizionario in memoria: {ip: (timestamp_ultimo_accesso, sistema_operativo, browser, device)}
utenti_attivi = {}

# Timeout in secondi per considerare un utente "online" (es: 5 minuti)
TIMEOUT = 300

def estrai_sistema_operativo(user_agent):
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

def estrai_browser(user_agent):
    if not user_agent:
        return "?"
    ua = user_agent.lower()
    if "chrome" in ua and "edg" not in ua and "opr" not in ua:
        return "Chrome"
    if "firefox" in ua:
        return "Firefox"
    if "safari" in ua and "chrome" not in ua:
        return "Safari"
    if "edg" in ua:
        return "Edge"
    if "opr" in ua or "opera" in ua:
        return "Opera"
    return "Altro"

def estrai_device(user_agent):
    if not user_agent:
        return "?"
    ua = user_agent.lower()
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        return "Mobile"
    if "ipad" in ua or "tablet" in ua:
        return "Tablet"
    if "windows" in ua or "macintosh" in ua or "linux" in ua:
        return "Desktop"
    return "Altro"

def aggiorna_utente_online():
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    sistema = estrai_sistema_operativo(user_agent)
    browser = estrai_browser(user_agent)
    device = estrai_device(user_agent)
    utenti_attivi[ip] = (time.time(), sistema, browser, device)

def conta_utenti_online():
    now = time.time()
    utenti_vivi = {ip: (ts, so, br, dev) for ip, (ts, so, br, dev) in utenti_attivi.items() if now - ts < TIMEOUT}
    utenti_attivi.clear()
    utenti_attivi.update(utenti_vivi)
    return len(utenti_attivi)

def get_ip_attivi(secondi=180):
    now = time.time()
    # Restituisce lista di tuple (ip, sistema operativo, browser, device)
    return [(ip, so, br, dev) for ip, (ts, so, br, dev) in utenti_attivi.items() if now - ts < secondi] 