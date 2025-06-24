import pandas as pd
from flask import Flask, render_template
from datetime import datetime
import os

# Inizializza l'app Flask
app = Flask(__name__)

# Funzione per creare il file Excel con i fogli e colonne necessari se non esiste già
# Questo permette all'app di funzionare anche al primo avvio senza dati reali
# I dati di esempio sono utili per test e sviluppo

def create_excel_if_not_exists():
    """
    Crea il file dati_torneo.xlsx con la struttura adatta al torneo a 10 squadre.
    Ogni foglio ha le colonne richieste dal codice e i loghi sono personalizzabili tramite la colonna 'Logo'.
    """
    excel_path = 'dati_torneo.xlsx'
    if not os.path.exists(excel_path):
        # Lista delle 10 squadre e relativi loghi
        squadre = [
            ("Real Matadors", "realmatadors.png"),
            ("I Gatti Rossi", "igattirossi.png"),
            ("Team Rocket", "rocket.png"),
            ("Blue Sharks", "bluesharks.png"),
            ("Green Lions", "greenlions.png"),
            ("Red Bulls", "redbulls.png"),
            ("Black Panthers", "blackpanthers.png"),
            ("White Eagles", "whiteeagles.png"),
            ("Orange Foxes", "orangefoxes.png"),
            ("Yellow Tigers", "yellowtigers.png")
        ]
        # Foglio 1: Prossime Partite (solo una partita di esempio per ogni squadra)
        df_prossime = pd.DataFrame([
            {"Data": "2025-07-15", "Ora": "20:30", "Stadio": "Delta Stadium", "Squadra Casa": squadre[i%10][0], "Logo Casa": squadre[i%10][1], "Squadra Trasferta": squadre[(i+1)%10][0], "Logo Trasferta": squadre[(i+1)%10][1]} for i in range(10)
        ])
        # Foglio 2: Rose (3 giocatori di esempio per squadra)
        df_rose = pd.DataFrame([
            {"Squadra": nome, "Giocatore": f"Giocatore {i+1}", "Ruolo": ruolo, "Numero": 10+i} 
            for nome, _ in squadre for i, ruolo in enumerate(["Attaccante", "Centrocampista", "Difensore"])
        ])
        # Foglio 3: Classifiche (gironi A e B, 5 squadre per girone, con colonna Logo)
        gironi = ["Girone A"]*5 + ["Girone B"]*5
        df_classifiche = pd.DataFrame([
            {"Pos": i+1, "Squadra": squadre[i][0], "Girone": gironi[i], "PG": 0, "V": 0, "N": 0, "P": 0, "GF": 0, "GS": 0, "PT": 0, "Logo": squadre[i][1]} for i in range(10)
        ])
        # Foglio 4: Calendario Partite (tutte le partite, esempio andata tra tutte le squadre)
        calendario = []
        for i in range(10):
            for j in range(i+1, 10):
                calendario.append({
                    "Data": f"2025-07-{15 + (i+j)%10}",
                    "Ora": "21:00",
                    "Stadio": "Delta Stadium",
                    "Squadra Casa": squadre[i][0],
                    "Logo Casa": squadre[i][1],
                    "Squadra Trasferta": squadre[j][0],
                    "Logo Trasferta": squadre[j][1],
                    "Risultato": "-"
                })
        df_calendario = pd.DataFrame(calendario)
        # Scrittura su file Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_prossime.to_excel(writer, sheet_name='Prossime Partite', index=False)
            df_rose.to_excel(writer, sheet_name='Rose', index=False)
            df_classifiche.to_excel(writer, sheet_name='Classifiche', index=False)
            df_calendario.to_excel(writer, sheet_name='Calendario Partite', index=False)
        print(f"Creato file Excel: {excel_path} (10 squadre, struttura aggiornata)")

# Funzione per ottenere la prossima partita in programma
# Restituisce un dizionario con tutte le info necessarie per il template

def get_next_match():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Prossime Partite', engine='openpyxl')
        df['Data'] = pd.to_datetime(df['Data'])
        today = datetime.now()
        future_matches = df[df['Data'] >= today]
        if not future_matches.empty:
            next_match = future_matches.iloc[0]
            return {
                'data': next_match['Data'].strftime('%d/%m/%Y'),
                'ora': next_match['Ora'][:5],
                'stadio': next_match['Stadio'],
                'squadra_casa': next_match['Squadra Casa'],
                'logo_casa': next_match['Logo Casa'],
                'squadra_trasferta': next_match['Squadra Trasferta'],
                'logo_trasferta': next_match['Logo Trasferta'],
                'tipo_partita': next_match.get('Tipo Partita', '')
            }
    except Exception as e:
        print(f"Errore nella lettura del file Excel: {e}")
    return None

# Funzione per ottenere le rose delle squadre
# Ora usa la colonna 'Logo' dal foglio Classifiche se presente, così puoi associare qualsiasi file logo a qualsiasi squadra

def get_teams():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Rose', engine='openpyxl')
        # Carica anche la tabella Classifiche per i loghi personalizzati
        df_logo = pd.read_excel('dati_torneo.xlsx', sheet_name='Classifiche', engine='openpyxl')
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
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Classifiche', engine='openpyxl')
        return df.to_dict('records')
    except Exception as e:
        print(f"Errore nella lettura della classifica: {e}")
        return []

# Funzione per ottenere tutte le partite del calendario (giocate e future)
def get_matches():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Calendario Partite', engine='openpyxl')
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

# ROUTES FLASK
# Homepage: mostra la prossima partita
@app.route('/')
def index():
    next_match = get_next_match()
    return render_template('index.html', next_match=next_match)

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

# Avvio dell'app Flask in modalità debug (solo per sviluppo)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)