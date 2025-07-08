import pandas as pd
from flask import Flask, render_template
from datetime import datetime
import os

# Inizializza l'app Flask
app = Flask(__name__)

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
            return {
                'data': str(next_match['Data']),
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
            matches.append({
                'Data': row['Data'].strftime('%d/%m/%Y'),
                'Ora': str(row['Ora'])[:5],
                'Stadio': row['Stadio'],
                'Squadra Casa': row['Squadra Casa'],
                'Logo Casa': row['Logo Casa'],
                'Squadra Trasferta': row['Squadra Trasferta'],
                'Logo Trasferta': row['Logo Trasferta'],
                'Risultato': row['Risultato'],
                'Tipo Partita': row.get('Tipo Partita', '')
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

# Avvio dell'app Flask in modalità debug (solo per sviluppo)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)