"""
Script per migrare i dati dall'Excel al database SQLite
Eseguire questo script una volta per importare tutti i dati esistenti
"""
import pandas as pd
import os
from app.models.database import get_db, init_db, set_db_path, update_classifica_from_partite

def migrate_from_excel():
    """Importa tutti i dati dall'Excel al database"""
    print("Inizio migrazione dati da Excel a SQLite...")
    
    # Determina il percorso del database
    db_name = os.getenv('DB_NAME', 'torneo.db')
    db_path = os.path.join('instance', db_name)
    if not os.path.exists('instance'):
        os.makedirs('instance', exist_ok=True)
    if os.path.exists(db_name) and not os.path.exists(db_path):
        # Se il database esiste nella root, usalo
        db_path = db_name
    
    set_db_path(db_path)
    
    # Inizializza il database
    init_db(db_path)
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. Importa Squadre dal foglio Classifiche
        print("Importo squadre...")
        df_classifiche = pd.read_excel('DATITORNEO.xlsx', sheet_name='Classifiche', engine='openpyxl')
        squadre_dict = {}  # Per mappare nome squadra -> id
        
        for _, row in df_classifiche.iterrows():
            nome_squadra = row['Squadra']
            logo = row.get('Logo', nome_squadra.lower().replace(' ', '') + '.png')
            girone = row.get('Girone', '')
            punti = int(row.get('Punti', 0))
            pg = int(row.get('PG', 0))
            v = int(row.get('V', 0))
            n = int(row.get('N', 0))
            p = int(row.get('P', 0))
            gf = int(row.get('GF', 0))
            gs = int(row.get('GS', 0))
            dr = int(row.get('DR', 0))
            
            cursor.execute('''
                INSERT OR REPLACE INTO squadre 
                (nome, logo, girone, punti, partite_giocate, partite_vinte, 
                 partite_pareggiate, partite_perse, goal_fatti, goal_subiti, differenza_reti)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome_squadra, logo, girone, punti, pg, v, n, p, gf, gs, dr))
            
            # Ottieni l'ID della squadra inserita
            cursor.execute('SELECT id FROM squadre WHERE nome = ?', (nome_squadra,))
            squadre_dict[nome_squadra] = cursor.fetchone()['id']
        
        print(f"Importate {len(squadre_dict)} squadre")
        
        # 2. Importa Giocatori dal foglio Rose
        print("Importo giocatori...")
        df_rose = pd.read_excel('DATITORNEO.xlsx', sheet_name='Rose', engine='openpyxl')
        
        # Normalizza colonna Goal/Gol
        if 'Gol' in df_rose.columns:
            df_rose = df_rose.rename(columns={'Gol': 'Goal'})
        if 'Goal' not in df_rose.columns:
            df_rose['Goal'] = 0
        
        giocatori_importati = 0
        for _, row in df_rose.iterrows():
            nome_giocatore = row['Giocatore']
            nome_squadra = row['Squadra']
            goal = int(pd.to_numeric(row.get('Goal', 0), errors='coerce') or 0)
            
            if nome_squadra in squadre_dict:
                squadra_id = squadre_dict[nome_squadra]
                cursor.execute('''
                    INSERT OR REPLACE INTO giocatori (nome, squadra_id, goal)
                    VALUES (?, ?, ?)
                ''', (nome_giocatore, squadra_id, goal))
                giocatori_importati += 1
        
        print(f"Importati {giocatori_importati} giocatori")
        
        # 3. Importa Partite dal foglio Calendario Partite
        print("Importo partite...")
        df_calendario = pd.read_excel('DATITORNEO.xlsx', sheet_name='Calendario Partite', engine='openpyxl')
        partite_importate = 0
        
        for _, row in df_calendario.iterrows():
            data = pd.to_datetime(row['Data']).date()
            ora = str(row['Ora'])[:5] if pd.notna(row['Ora']) else '18:00'
            stadio = row['Stadio']
            squadra_casa = row['Squadra Casa']
            squadra_trasferta = row['Squadra Trasferta']
            tipo_partita = row.get('Tipo Partita', '')
            girone = row.get('Girone', '')
            
            # Gestisci risultato
            risultato_str = row.get('Risultato', '-')
            risultato_casa = None
            risultato_trasferta = None
            
            if pd.notna(risultato_str) and risultato_str != '-' and risultato_str != '':
                try:
                    # Gestisci formato "X-Y"
                    if isinstance(risultato_str, str) and '-' in risultato_str:
                        parts = risultato_str.split('-')
                        risultato_casa = int(parts[0].strip())
                        risultato_trasferta = int(parts[1].strip())
                except:
                    pass
            
            if squadra_casa in squadre_dict and squadra_trasferta in squadre_dict:
                casa_id = squadre_dict[squadra_casa]
                trasferta_id = squadre_dict[squadra_trasferta]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO partite 
                    (data, ora, stadio, squadra_casa_id, squadra_trasferta_id, 
                     risultato_casa, risultato_trasferta, tipo_partita, girone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (data, ora, stadio, casa_id, trasferta_id, 
                      risultato_casa, risultato_trasferta, tipo_partita, girone))
                partite_importate += 1
        
        print(f"Importate {partite_importate} partite")
        
        # 4. Importa Vincitore Finale
        print("Importo vincitore finale...")
        try:
            df_finale = pd.read_excel('DATITORNEO.xlsx', sheet_name='Finale', engine='openpyxl')
            vincitore_row = df_finale[df_finale['Vincitore'] == 1]
            if not vincitore_row.empty:
                nome_vincitore = vincitore_row.iloc[0]['Squadra']
                if nome_vincitore in squadre_dict:
                    squadra_id = squadre_dict[nome_vincitore]
                    # Rimuovi vecchi vincitori
                    cursor.execute('DELETE FROM vincitore_finale')
                    cursor.execute('INSERT INTO vincitore_finale (squadra_id) VALUES (?)', (squadra_id,))
                    print(f"Vincitore finale impostato: {nome_vincitore}")
        except Exception as e:
            print(f"Nessun vincitore finale trovato o errore: {e}")
        
        # Salva le modifiche
        conn.commit()
        print("\nMigrazione completata con successo!")
        
        # Aggiorna classifica calcolandola dalle partite
        print("\nAggiorno classifica dalle partite...")
        update_classifica_from_partite()
        print("Classifica aggiornata!")
        
    except Exception as e:
        print(f"Errore durante la migrazione: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    import os
    # Aggiungi la directory root al path per importare app
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    migrate_from_excel()

