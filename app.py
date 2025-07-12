import pandas as pd
from flask import Flask, render_template
from datetime import datetime
import os
import locale
from utenti_online import aggiorna_utente_online, conta_utenti_online, get_utenti_attivi, browser_accetta_cookie, conta_accessi_24h, conta_accessi_totali, filtra_utenti_doppi

# Inizializza l'app Flask
app = Flask(__name__)

# Imposta la localizzazione italiana per le date
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    # Su alcuni sistemi MacOS potrebbe essere 'it_IT' o potrebbe non essere disponibile
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT')
    except locale.Error:
        pass  # fallback: non cambiare locale

# Funzione per formattare la data in stile italiano: 'Lunedì-01-gennaio-2024'
def formatta_data_italiana(data_str):
    mesi = {
        "January": "Gennaio", "February": "Febbraio", "March": "Marzo",
        "April": "Aprile", "May": "Maggio", "June": "Giugno",
        "July": "Luglio", "August": "Agosto", "September": "Settembre",
        "October": "Ottobre", "November": "Novembre", "December": "Dicembre"
    }
    giorni = {
        "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
        "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
    }
    try:
        # Gestisce sia stringhe che oggetti datetime
        if isinstance(data_str, str):
            # Prova a convertire la stringa in datetime
            data = pd.to_datetime(data_str)
        else:
            data = data_str
        nome_giorno = giorni[data.strftime("%A")]
        nome_mese = mesi[data.strftime("%B")]
        # Formato: Giovedì-10-Luglio-2025
        return f"{nome_giorno}-{data.day:02d}-{nome_mese}-{data.year}"
    except Exception as e:
        print(f"Errore nella formattazione della data: {e}")
        return str(data_str)

# Funzione per creare il file Excel con i fogli e colonne necessari se non esiste già
# Questo permette all'app di funzionare anche al primo avvio senza dati reali
# I dati di esempio sono utili per test e sviluppo

# RIMOSSA LA FUNZIONE create_excel_if_not_exists()

# Funzione per ottenere la prossima partita in programma
# Restituisce un dizionario con tutte le info necessarie per il template

def get_next_match():
    try:
        df = pd.read_excel('DATITORNEO.xlsx', sheet_name='Prossime Partite', engine='openpyxl')
        print('DEBUG - Squadre Casa in Prossime Partite:', df['Squadra Casa'].unique())
        if not df.empty:
            next_match = df.iloc[0]
            # Usa la nuova funzione per la data
            data_formattata = formatta_data_italiana(next_match['Data'])
            return {
                'data': data_formattata,
                'ora': str(next_match['Ora']),
                'stadio': next_match['Stadio'],
                'squadra_casa': next_match['Squadra Casa'],
                'logo_casa': next_match['Logo Casa'],
                'squadra_trasferta': next_match['Squadra Trasferta'],
                'logo_trasferta': next_match['Logo Trasferta'],
                'tipo_partita': next_match.get('Tipo Partita', ''),
                'risultato': next_match.get('Risultato', '')
            }
    except Exception as e:
        print(f"Errore nella lettura del file Excel: {e}")
        return None

# Funzione per ottenere le rose delle squadre
# Ora usa la colonna 'Logo' dal foglio Classifiche se presente, così puoi associare qualsiasi file logo a qualsiasi squadra

def get_teams():
    try:
        df = pd.read_excel('DATITORNEO.xlsx', sheet_name='Rose', engine='openpyxl')
        # Normalizza la colonna Goal/Gol come in get_top_scorers
        if 'Gol' in df.columns:
            df = df.rename(columns={'Gol': 'Goal'})
        df['Goal'] = pd.to_numeric(df['Goal'], errors='coerce').fillna(0).astype(int)
        # Carica anche la tabella Classifiche per i loghi personalizzati
        df_logo = pd.read_excel('DATITORNEO.xlsx', sheet_name='Classifiche', engine='openpyxl')
        print('DEBUG - Squadre in Classifiche:', df_logo['Squadra'].unique())
        logo_dict = {row['Squadra']: row.get('Logo', '') for _, row in df_logo.iterrows()}
        teams = {}
        for squadra, players in df.groupby('Squadra'):
            # Prende il logo dalla colonna Logo del foglio Classifiche, se presente
            logo = logo_dict.get(squadra, squadra.lower().replace(' ', '') + '.png')
            teams[squadra] = {
                'logo': logo,
                'players': players.to_dict('records')
            }
        return teams
    except Exception as e:
        print(f"Errore nella lettura delle rose: {e}")
        return {}

# Funzione per ottenere la classifica completa (tutti i gironi)
def get_standings():
    try:
        df = pd.read_excel('DATITORNEO.xlsx', sheet_name='Classifiche', engine='openpyxl')
        return df.to_dict('records')
    except Exception as e:
        print(f"Errore nella lettura della classifica: {e}")
        return []

# Funzione per ottenere tutte le partite del calendario (giocate e future)
def get_matches():
    try:
        df = pd.read_excel('DATITORNEO.xlsx', sheet_name='Calendario Partite', engine='openpyxl')
        df['Data'] = pd.to_datetime(df['Data'])
        matches = []
        for _, row in df.iterrows():
            data_formattata = formatta_data_italiana(row['Data'])
            matches.append({
                'Data': data_formattata,
                'Ora': str(row['Ora'])[:5],
                'Stadio': row['Stadio'],
                'Squadra Casa': row['Squadra Casa'],
                'Logo Casa': row['Logo Casa'],
                'Squadra Trasferta': row['Squadra Trasferta'],
                'Logo Trasferta': row['Logo Trasferta'],
                'Risultato': row['Risultato'],
                'Tipo Partita': row.get('Tipo Partita', ''),
                'Girone': row.get('Girone', '')
            })
        return matches
    except Exception as e:
        print(f"Errore nella lettura del calendario: {e}")
        return []

# Funzione per ottenere i top 5 cannonieri dal foglio Rose

def get_top_scorers():
    try:
        df = pd.read_excel('DATITORNEO.xlsx', sheet_name='Rose', engine='openpyxl')
        # Correggi eventuali colonne 'Gol' in 'Goal'
        if 'Gol' in df.columns:
            df = df.rename(columns={'Gol': 'Goal'})
        # Se la colonna è già 'Goal', non fa nulla
        # Sostituisci NaN con 0 per i goal
        df['Goal'] = pd.to_numeric(df['Goal'], errors='coerce').fillna(0).astype(int)
        # Ordina per Goal decrescente e prendi i primi 5
        top5 = df.sort_values(by='Goal', ascending=False).head(5)
        # Restituisci solo le colonne utili
        return top5[['Giocatore', 'Squadra', 'Goal']].to_dict('records')
    except Exception as e:
        print(f"Errore nel calcolo dei top cannonieri: {e}")
        return []

# ROUTES FLASK
# Homepage: mostra la prossima partita
@app.route('/')
def index():
    aggiorna_utente_online()
    next_match = get_next_match()
    top_scorers = get_top_scorers()
    return render_template('index.html', next_match=next_match, top_scorers=top_scorers)

# Pagina rose: mostra le rose delle squadre
@app.route('/rose')
def rose():
    teams = get_teams()
    return render_template('rose.html', teams=teams)

# Pagina classifica: mostra la classifica per gironi
@app.route('/classifica')
def classifica():
    standings = get_standings()
    return render_template('classifica.html', standings=standings)

# Pagina partite: mostra tutte le partite del calendario
@app.route('/partite')
def partite():
    matches = get_matches()
    return render_template('partite.html', matches=matches)

# Pagina about: info torneo
@app.route('/about')
def about():
    return render_template('about.html')

# Pagina menu mobile
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Pagina cerca giocatore: mostra tutte le rose per la ricerca
@app.route('/cerca-giocatore')
def cerca_giocatore():
    teams = get_teams()
    return render_template('cerca_giocatore.html', teams=teams)

# Pagina nascosta: mostra il numero di utenti online e i dettagli utenti (identificatore, ip, os, browser, device, modello)
@app.route('/admin/utenti-online')
def admin_utenti_online():
    n_utenti = conta_utenti_online()
    utenti = get_utenti_attivi(180)
    utenti = filtra_utenti_doppi(utenti)
    cookies_ok = browser_accetta_cookie()
    accessi_24h = conta_accessi_24h()
    accessi_totali = conta_accessi_totali()
    return render_template('utenti_online.html', n_utenti=n_utenti, utenti=utenti, cookies_ok=cookies_ok, accessi_24h=accessi_24h, accessi_totali=accessi_totali)

# Avvio dell'app Flask in modalità debug (solo per sviluppo)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)