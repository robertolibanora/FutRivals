import pandas as pd
from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

def create_excel_if_not_exists():
    excel_path = 'dati_torneo.xlsx'
    if not os.path.exists(excel_path):
        # Foglio 1: Prossime Partite
        df_prossime = pd.DataFrame([
            {"Data": "2025-07-15", "Ora": "20:30", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team A", "Logo Casa": "teamA.png", "Squadra Trasferta": "Team B", "Logo Trasferta": "teamB.png"},
            {"Data": "2025-07-16", "Ora": "21:00", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team C", "Logo Casa": "teamC.png", "Squadra Trasferta": "Team D", "Logo Trasferta": "teamD.png"}
        ])
        # Foglio 2: Rose
        df_rose = pd.DataFrame([
            {"Squadra": "Team A", "Giocatore": "Mario Rossi", "Ruolo": "Attaccante", "Numero": 10},
            {"Squadra": "Team A", "Giocatore": "Luigi Verdi", "Ruolo": "Centrocampista", "Numero": 8},
            {"Squadra": "Team A", "Giocatore": "Paolo Bianchi", "Ruolo": "Difensore", "Numero": 4},
            {"Squadra": "Team B", "Giocatore": "Carlo Neri", "Ruolo": "Attaccante", "Numero": 9},
            {"Squadra": "Team B", "Giocatore": "Marco Gialli", "Ruolo": "Centrocampista", "Numero": 6},
            {"Squadra": "Team B", "Giocatore": "Antonio Rossi", "Ruolo": "Difensore", "Numero": 3},
            {"Squadra": "Team C", "Giocatore": "Giuseppe Verdi", "Ruolo": "Attaccante", "Numero": 11},
            {"Squadra": "Team C", "Giocatore": "Roberto Bianchi", "Ruolo": "Centrocampista", "Numero": 7},
            {"Squadra": "Team C", "Giocatore": "Francesco Neri", "Ruolo": "Difensore", "Numero": 2},
            {"Squadra": "Team D", "Giocatore": "Alberto Rossi", "Ruolo": "Attaccante", "Numero": 10},
            {"Squadra": "Team D", "Giocatore": "Marco Verdi", "Ruolo": "Centrocampista", "Numero": 8},
            {"Squadra": "Team D", "Giocatore": "Paolo Gialli", "Ruolo": "Difensore", "Numero": 5}
        ])
        # Foglio 3: Classifiche
        df_classifiche = pd.DataFrame([
            {"Pos": 1, "Squadra": "Team A", "Girone": "Girone A", "PG": 3, "V": 2, "N": 1, "P": 0, "GF": 7, "GS": 2, "PT": 7},
            {"Pos": 2, "Squadra": "Team B", "Girone": "Girone A", "PG": 3, "V": 2, "N": 0, "P": 1, "GF": 5, "GS": 3, "PT": 6},
            {"Pos": 1, "Squadra": "Team C", "Girone": "Girone B", "PG": 3, "V": 3, "N": 0, "P": 0, "GF": 8, "GS": 1, "PT": 9},
            {"Pos": 2, "Squadra": "Team D", "Girone": "Girone B", "PG": 3, "V": 1, "N": 1, "P": 1, "GF": 4, "GS": 4, "PT": 4}
        ])
        # Foglio 4: Calendario Partite
        df_calendario = pd.DataFrame([
            {"Data": "2025-07-15", "Ora": "20:30", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team A", "Logo Casa": "teamA.png", "Squadra Trasferta": "Team B", "Logo Trasferta": "teamB.png", "Risultato": "3-1"},
            {"Data": "2025-07-16", "Ora": "21:00", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team C", "Logo Casa": "teamC.png", "Squadra Trasferta": "Team D", "Logo Trasferta": "teamD.png", "Risultato": "2-2"},
            {"Data": "2025-07-17", "Ora": "20:30", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team A", "Logo Casa": "teamA.png", "Squadra Trasferta": "Team C", "Logo Trasferta": "teamC.png", "Risultato": "-"},
            {"Data": "2025-07-18", "Ora": "21:00", "Stadio": "Delta Volley Stadium", "Squadra Casa": "Team B", "Logo Casa": "teamB.png", "Squadra Trasferta": "Team D", "Logo Trasferta": "teamD.png", "Risultato": "-"}
        ])
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_prossime.to_excel(writer, sheet_name='Prossime Partite', index=False)
            df_rose.to_excel(writer, sheet_name='Rose', index=False)
            df_classifiche.to_excel(writer, sheet_name='Classifiche', index=False)
            df_calendario.to_excel(writer, sheet_name='Calendario Partite', index=False)
        print(f"Creato file Excel: {excel_path}")

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

def get_teams():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Rose', engine='openpyxl')
        teams = {}
        for squadra, players in df.groupby('Squadra'):
            logo = squadra.lower().replace(' ', '') + '.png'
            teams[squadra] = {
                'logo': logo,
                'players': players.to_dict('records')
            }
        print("DEBUG get_teams:", teams)  # DEBUG
        return teams
    except Exception as e:
        print(f"Errore nella lettura delle rose: {e}")
        return {}

def get_standings():
    create_excel_if_not_exists()
    try:
        df = pd.read_excel('dati_torneo.xlsx', sheet_name='Classifiche', engine='openpyxl')
        return df.to_dict('records')
    except Exception as e:
        print(f"Errore nella lettura della classifica: {e}")
        return []

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

@app.route('/')
def index():
    next_match = get_next_match()
    return render_template('index.html', next_match=next_match)

@app.route('/rose')
def rose():
    teams = get_teams()
    print("DEBUG TEAMS:", teams)  # DEBUG
    return render_template('rose.html', teams=teams)

@app.route('/classifica')
def classifica():
    standings = get_standings()
    return render_template('classifica.html', standings=standings)

@app.route('/partite')
def partite():
    matches = get_matches()
    return render_template('partite.html', matches=matches)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=1234)