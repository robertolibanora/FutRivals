import time
from flask import request
import re

# Dizionario in memoria: {(user_id, ip): (timestamp_ultimo_accesso, sistema_operativo, browser, device, modello)}
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

def estrai_modello(user_agent):
    if not user_agent:
        return "?"
    ua = user_agent
    # Android: cerca modello tra ; e )
    if "Android" in ua:
        m = re.search(r"Android [^;]+; ([^)]+)\)", ua)
        if m:
            return m.group(1).strip()
    # iPhone/iPad: solo tipo
    if "iPhone" in ua:
        return "iPhone"
    if "iPad" in ua:
        return "iPad"
    # Windows/Mac/Linux: generico
    if "Windows" in ua:
        return "PC Windows"
    if "Macintosh" in ua:
        return "Mac"
    if "Linux" in ua:
        return "PC Linux"
    return "?"

def get_user_id():
    user_id = request.cookies.get('user_id')
    return user_id

def aggiorna_utente_online():
    user_id = get_user_id()
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    sistema = estrai_sistema_operativo(user_agent)
    browser = estrai_browser(user_agent)
    device = estrai_device(user_agent)
    modello = estrai_modello(user_agent)
    key = (user_id if user_id else None, ip)
    utenti_attivi[key] = (time.time(), sistema, browser, device, modello)

def conta_utenti_online():
    now = time.time()
    utenti_vivi = {k: v for k, v in utenti_attivi.items() if now - v[0] < TIMEOUT}
    utenti_attivi.clear()
    utenti_attivi.update(utenti_vivi)
    return len(utenti_attivi)

def get_utenti_attivi(secondi=180):
    now = time.time()
    # Restituisce lista di tuple (user_id, ip, sistema operativo, browser, device, modello)
    return [((uid if uid else 'NOCOOKIE'), ip, so, br, dev, mod) for (uid, ip), (ts, so, br, dev, mod) in utenti_attivi.items() if now - ts < secondi] 