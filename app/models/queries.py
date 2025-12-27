"""
Query helper functions per il database
"""
from datetime import date
from app.models.database import get_db
from app.utils.helpers import formatta_data_italiana


def get_next_match():
    """Ottiene la prossima partita in programma"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, 
                   sc.nome as squadra_casa_nome, sc.logo as logo_casa,
                   st.nome as squadra_trasferta_nome, st.logo as logo_trasferta
            FROM partite p
            JOIN squadre sc ON p.squadra_casa_id = sc.id
            JOIN squadre st ON p.squadra_trasferta_id = st.id
            WHERE p.risultato_casa IS NULL OR p.risultato_trasferta IS NULL
            ORDER BY p.data ASC, p.ora ASC
            LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data_formattata = formatta_data_italiana(row['data'])
            risultato = None
            if row['risultato_casa'] is not None and row['risultato_trasferta'] is not None:
                risultato = f"{row['risultato_casa']}-{row['risultato_trasferta']}"
            
            return {
                'data': data_formattata,
                'ora': str(row['ora'])[:5],
                'stadio': row['stadio'],
                'squadra_casa': row['squadra_casa_nome'],
                'logo_casa': row['logo_casa'],
                'squadra_trasferta': row['squadra_trasferta_nome'],
                'logo_trasferta': row['logo_trasferta'],
                'tipo_partita': row['tipo_partita'] or '',
                'risultato': risultato or ''
            }
        return None
    except Exception as e:
        print(f"Errore nella lettura della prossima partita: {e}")
        return None


def get_teams():
    """Ottiene le rose delle squadre"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        teams = {}
        
        cursor.execute('''
            SELECT s.id, s.nome, s.logo, g.id as giocatore_id, g.nome as giocatore_nome, g.goal
            FROM squadre s
            LEFT JOIN giocatori g ON s.id = g.squadra_id
            ORDER BY s.nome, g.nome
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            squadra_nome = row['nome']
            if squadra_nome not in teams:
                teams[squadra_nome] = {
                    'logo': row['logo'],
                    'players': []
                }
            
            if row['giocatore_nome']:
                teams[squadra_nome]['players'].append({
                    'Giocatore': row['giocatore_nome'],
                    'Squadra': squadra_nome,
                    'Goal': row['goal'] if row['goal'] is not None else 0
                })
        
        return teams
    except Exception as e:
        print(f"Errore nella lettura delle rose: {e}")
        return {}


def get_standings():
    """Ottiene la classifica completa"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nome as Squadra, logo as Logo, girone as Girone,
                   punti as Punti, partite_giocate as PG,
                   partite_vinte as V, partite_pareggiate as N,
                   partite_perse as P, goal_fatti as GF,
                   goal_subiti as GS, differenza_reti as DR
            FROM squadre
            ORDER BY girone, punti DESC, differenza_reti DESC, goal_fatti DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        # Converti le row in dizionari e aggiungi Posizione
        result = []
        pos_per_girone = {}
        for row in rows:
            row_dict = dict(row)
            girone = row_dict.get('Girone', '')
            if girone not in pos_per_girone:
                pos_per_girone[girone] = 0
            pos_per_girone[girone] += 1
            row_dict['Pos'] = pos_per_girone[girone]
            row_dict['PT'] = row_dict['Punti']  # Alias per compatibilità template
            row_dict['Logo Casa'] = row_dict['Logo']  # Alias per compatibilità template
            result.append(row_dict)
        
        return result
    except Exception as e:
        print(f"Errore nella lettura della classifica: {e}")
        return []


def get_matches():
    """Ottiene tutte le partite del calendario"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.data, p.ora, p.stadio,
                   sc.nome as squadra_casa, sc.logo as logo_casa,
                   st.nome as squadra_trasferta, st.logo as logo_trasferta,
                   p.risultato_casa, p.risultato_trasferta,
                   p.tipo_partita, p.girone
            FROM partite p
            JOIN squadre sc ON p.squadra_casa_id = sc.id
            JOIN squadre st ON p.squadra_trasferta_id = st.id
            ORDER BY p.data ASC, p.ora ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        matches = []
        for row in rows:
            data_formattata = formatta_data_italiana(row['data'])
            risultato = '-'
            if row['risultato_casa'] is not None and row['risultato_trasferta'] is not None:
                risultato = f"{row['risultato_casa']}-{row['risultato_trasferta']}"
            
            matches.append({
                'Data': data_formattata,
                'Ora': str(row['ora'])[:5],
                'Stadio': row['stadio'],
                'Squadra Casa': row['squadra_casa'],
                'Logo Casa': row['logo_casa'],
                'Squadra Trasferta': row['squadra_trasferta'],
                'Logo Trasferta': row['logo_trasferta'],
                'Risultato': risultato,
                'Tipo Partita': row['tipo_partita'] or '',
                'Girone': row['girone'] or ''
            })
        return matches
    except Exception as e:
        print(f"Errore nella lettura del calendario: {e}")
        return []


def get_top_scorers():
    """Ottiene i top 5 cannonieri"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.nome as Giocatore, s.nome as Squadra, g.goal as Goal
            FROM giocatori g
            JOIN squadre s ON g.squadra_id = s.id
            ORDER BY g.goal DESC, g.nome ASC
            LIMIT 5
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Errore nel calcolo dei top cannonieri: {e}")
        return []


def get_winner():
    """Ottiene la squadra vincitrice della finale"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.nome, s.logo
            FROM vincitore_finale vf
            JOIN squadre s ON vf.squadra_id = s.id
            LIMIT 1
        ''')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'nome': row['nome'],
                'logo': row['logo']
            }
        return None
    except Exception as e:
        print(f"Errore nella lettura del vincitore: {e}")
        return None

