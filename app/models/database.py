"""
Gestione database SQLite
"""
import sqlite3
import os
from flask import current_app


_db_path = None


def set_db_path(db_path):
    """Imposta il percorso del database"""
    global _db_path
    _db_path = db_path


def get_db():
    """Crea una connessione al database"""
    if _db_path is None:
        # Fallback per compatibilità con script esterni
        db_name = os.getenv('DB_NAME', 'torneo.db')
        db_path = os.path.join('instance', db_name)
        if not os.path.exists('instance'):
            db_path = db_name
    else:
        db_path = _db_path
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permette di accedere alle colonne come dizionari
    return conn


def init_db(db_path=None):
    """
    Inizializza il database creando tutte le tabelle
    
    Args:
        db_path: Percorso del file database (opzionale)
    """
    global _db_path
    if db_path:
        _db_path = db_path
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabella Squadre
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS squadre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            logo TEXT NOT NULL,
            girone TEXT,
            punti INTEGER DEFAULT 0,
            partite_giocate INTEGER DEFAULT 0,
            partite_vinte INTEGER DEFAULT 0,
            partite_pareggiate INTEGER DEFAULT 0,
            partite_perse INTEGER DEFAULT 0,
            goal_fatti INTEGER DEFAULT 0,
            goal_subiti INTEGER DEFAULT 0,
            differenza_reti INTEGER DEFAULT 0
        )
    ''')
    
    # Tabella Giocatori
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS giocatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            squadra_id INTEGER NOT NULL,
            goal INTEGER DEFAULT 0,
            FOREIGN KEY (squadra_id) REFERENCES squadre(id) ON DELETE CASCADE,
            UNIQUE(nome, squadra_id)
        )
    ''')
    
    # Tabella Partite
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            ora TEXT NOT NULL,
            stadio TEXT NOT NULL,
            squadra_casa_id INTEGER NOT NULL,
            squadra_trasferta_id INTEGER NOT NULL,
            risultato_casa INTEGER,
            risultato_trasferta INTEGER,
            tipo_partita TEXT,
            girone TEXT,
            FOREIGN KEY (squadra_casa_id) REFERENCES squadre(id),
            FOREIGN KEY (squadra_trasferta_id) REFERENCES squadre(id)
        )
    ''')
    
    # Tabella Marcatori (per tracciare chi ha segnato in ogni partita)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marcatori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partita_id INTEGER NOT NULL,
            giocatore_id INTEGER NOT NULL,
            minuto INTEGER,
            squadra_casa BOOLEAN NOT NULL,
            FOREIGN KEY (partita_id) REFERENCES partite(id) ON DELETE CASCADE,
            FOREIGN KEY (giocatore_id) REFERENCES giocatori(id)
        )
    ''')
    
    # Tabella Vincitore Finale
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vincitore_finale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            squadra_id INTEGER NOT NULL,
            FOREIGN KEY (squadra_id) REFERENCES squadre(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database inizializzato con successo in {_db_path or 'default location'}!")


def update_classifica_from_partite():
    """Aggiorna la classifica calcolandola dalle partite giocate"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Resetta tutti i valori
    cursor.execute('UPDATE squadre SET punti=0, partite_giocate=0, partite_vinte=0, partite_pareggiate=0, partite_perse=0, goal_fatti=0, goal_subiti=0, differenza_reti=0')
    
    # Ottieni tutte le partite giocate (con risultato)
    cursor.execute('''
        SELECT * FROM partite 
        WHERE risultato_casa IS NOT NULL AND risultato_trasferta IS NOT NULL
    ''')
    partite = cursor.fetchall()
    
    for partita in partite:
        casa_id = partita['squadra_casa_id']
        trasferta_id = partita['squadra_trasferta_id']
        gol_casa = partita['risultato_casa']
        gol_trasferta = partita['risultato_trasferta']
        
        # Aggiorna squadra casa
        cursor.execute('''
            UPDATE squadre 
            SET partite_giocate = partite_giocate + 1,
                goal_fatti = goal_fatti + ?,
                goal_subiti = goal_subiti + ?
            WHERE id = ?
        ''', (gol_casa, gol_trasferta, casa_id))
        
        # Aggiorna squadra trasferta
        cursor.execute('''
            UPDATE squadre 
            SET partite_giocate = partite_giocate + 1,
                goal_fatti = goal_fatti + ?,
                goal_subiti = goal_subiti + ?
            WHERE id = ?
        ''', (gol_trasferta, gol_casa, trasferta_id))
        
        # Calcola punti e risultati
        if gol_casa > gol_trasferta:
            # Vittoria casa
            cursor.execute('UPDATE squadre SET punti = punti + 3, partite_vinte = partite_vinte + 1 WHERE id = ?', (casa_id,))
            cursor.execute('UPDATE squadre SET partite_perse = partite_perse + 1 WHERE id = ?', (trasferta_id,))
        elif gol_casa < gol_trasferta:
            # Vittoria trasferta
            cursor.execute('UPDATE squadre SET punti = punti + 3, partite_vinte = partite_vinte + 1 WHERE id = ?', (trasferta_id,))
            cursor.execute('UPDATE squadre SET partite_perse = partite_perse + 1 WHERE id = ?', (casa_id,))
        else:
            # Pareggio
            cursor.execute('UPDATE squadre SET punti = punti + 1, partite_pareggiate = partite_pareggiate + 1 WHERE id = ?', (casa_id,))
            cursor.execute('UPDATE squadre SET punti = punti + 1, partite_pareggiate = partite_pareggiate + 1 WHERE id = ?', (trasferta_id,))
    
    # Calcola differenza reti
    cursor.execute('UPDATE squadre SET differenza_reti = goal_fatti - goal_subiti')
    
    conn.commit()
    conn.close()

