"""
Routes per l'area admin
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, current_app
from app.models.database import get_db, update_classifica_from_partite
from app.utils.utenti_online import (
    conta_utenti_online, get_utenti_attivi, browser_accetta_cookie,
    conta_accessi_24h, conta_accessi_totali, filtra_solo_chiave
)

bp = Blueprint('admin', __name__, url_prefix='/admin')


def login_required(f):
    """Decorator per richiedere il login admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/', methods=['GET', 'POST'])
def admin_login():
    """Login admin"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Credenziali da configurazione
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin.html', login=True, message='Credenziali errate')
    
    # Mostra login se non autenticato
    if not session.get('admin_logged_in'):
        return render_template('admin.html', login=True)
    
    return redirect(url_for('admin.dashboard'))


@bp.route('/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard admin principale"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Statistiche rapide
    cursor.execute('SELECT COUNT(*) as totale FROM partite')
    totale_partite = cursor.fetchone()['totale']
    
    cursor.execute('SELECT COUNT(*) as totale FROM partite WHERE risultato_casa IS NOT NULL AND risultato_trasferta IS NOT NULL')
    partite_giocate = cursor.fetchone()['totale']
    
    cursor.execute('SELECT COUNT(*) as totale FROM squadre')
    totale_squadre = cursor.fetchone()['totale']
    
    cursor.execute('SELECT COUNT(*) as totale FROM giocatori')
    totale_giocatori = cursor.fetchone()['totale']
    
    cursor.execute('SELECT SUM(goal) as totale FROM giocatori')
    totale_goal = cursor.fetchone()['totale'] or 0
    
    # Ottieni partite
    cursor.execute('''
        SELECT p.id, p.data, p.ora, p.stadio,
               sc.nome as squadra_casa, sc.logo as logo_casa,
               st.nome as squadra_trasferta, st.logo as logo_trasferta,
               p.risultato_casa, p.risultato_trasferta,
               p.tipo_partita, p.girone
        FROM partite p
        JOIN squadre sc ON p.squadra_casa_id = sc.id
        JOIN squadre st ON p.squadra_trasferta_id = st.id
        ORDER BY p.data DESC, p.ora DESC
        LIMIT 50
    ''')
    partite = [dict(row) for row in cursor.fetchall()]
    
    # Ottieni squadre complete
    cursor.execute('SELECT id, nome, logo, girone, punti FROM squadre ORDER BY nome')
    squadre = [dict(row) for row in cursor.fetchall()]
    
    # Ottieni giocatori con goal
    cursor.execute('''
        SELECT g.id, g.nome, g.goal, s.id as squadra_id, s.nome as squadra
        FROM giocatori g
        JOIN squadre s ON g.squadra_id = s.id
        ORDER BY g.goal DESC, g.nome
    ''')
    giocatori = [dict(row) for row in cursor.fetchall()]
    
    # Vincitore finale
    cursor.execute('''
        SELECT s.id, s.nome, s.logo
        FROM vincitore_finale vf
        JOIN squadre s ON vf.squadra_id = s.id
        LIMIT 1
    ''')
    vincitore_row = cursor.fetchone()
    vincitore = dict(vincitore_row) if vincitore_row else None
    
    conn.close()
    
    stats = {
        'totale_partite': totale_partite,
        'partite_giocate': partite_giocate,
        'partite_da_giocare': totale_partite - partite_giocate,
        'totale_squadre': totale_squadre,
        'totale_giocatori': totale_giocatori,
        'totale_goal': totale_goal
    }
    
    return render_template('admin_dashboard.html', 
                         partite=partite, squadre=squadre, giocatori=giocatori,
                         stats=stats, vincitore=vincitore)


@bp.route('/utenti-online')
@login_required
def utenti_online():
    """Pagina utenti online"""
    n_utenti = conta_utenti_online()
    utenti = get_utenti_attivi(180)
    utenti = filtra_solo_chiave(utenti)
    cookies_ok = browser_accetta_cookie()
    accessi_24h = conta_accessi_24h()
    accessi_totali = conta_accessi_totali()
    return render_template('utenti_online.html', n_utenti=n_utenti, utenti=utenti, cookies_ok=cookies_ok, accessi_24h=accessi_24h, accessi_totali=accessi_totali)


@bp.route('/partita/<int:partita_id>', methods=['GET'])
@login_required
def get_partita(partita_id):
    """API: Ottiene i dettagli di una partita"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, 
               sc.nome as squadra_casa_nome,
               st.nome as squadra_trasferta_nome
        FROM partite p
        JOIN squadre sc ON p.squadra_casa_id = sc.id
        JOIN squadre st ON p.squadra_trasferta_id = st.id
        WHERE p.id = ?
    ''', (partita_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Partita non trovata'}), 404


@bp.route('/partita/update', methods=['POST'])
@login_required
def update_partita():
    """API: Aggiorna il risultato di una partita"""
    try:
        partita_id = request.form.get('partita_id')
        risultato_casa = request.form.get('risultato_casa')
        risultato_trasferta = request.form.get('risultato_trasferta')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Converti risultati
        risultato_casa_int = int(risultato_casa) if risultato_casa and risultato_casa.isdigit() else None
        risultato_trasferta_int = int(risultato_trasferta) if risultato_trasferta and risultato_trasferta.isdigit() else None
        
        cursor.execute('''
            UPDATE partite 
            SET risultato_casa = ?, risultato_trasferta = ?
            WHERE id = ?
        ''', (risultato_casa_int, risultato_trasferta_int, partita_id))
        
        conn.commit()
        conn.close()
        
        # Aggiorna classifica
        update_classifica_from_partite()
        
        return jsonify({'success': True, 'message': 'Risultato aggiornato con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/giocatore/update', methods=['POST'])
@login_required
def update_giocatore():
    """API: Aggiorna i goal di un giocatore"""
    try:
        giocatore_id = request.form.get('giocatore_id')
        goal = int(request.form.get('goal', 0))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE giocatori SET goal = ? WHERE id = ?', (goal, giocatore_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Goal aggiornati con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/partita/add', methods=['POST'])
@login_required
def add_partita():
    """API: Aggiunge una nuova partita"""
    try:
        data = request.form.get('data')
        ora = request.form.get('ora')
        stadio = request.form.get('stadio')
        squadra_casa_id = request.form.get('squadra_casa_id')
        squadra_trasferta_id = request.form.get('squadra_trasferta_id')
        tipo_partita = request.form.get('tipo_partita', '')
        girone = request.form.get('girone', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO partite (data, ora, stadio, squadra_casa_id, squadra_trasferta_id, tipo_partita, girone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data, ora, stadio, squadra_casa_id, squadra_trasferta_id, tipo_partita, girone))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Partita aggiunta con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/partita/<int:partita_id>/delete', methods=['POST'])
@login_required
def delete_partita(partita_id):
    """API: Elimina una partita"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM partite WHERE id = ?', (partita_id,))
        conn.commit()
        
        # Aggiorna classifica
        update_classifica_from_partite()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Partita eliminata con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== GESTIONE SQUADRE ==========

@bp.route('/squadra/add', methods=['POST'])
@login_required
def add_squadra():
    """API: Aggiunge una nuova squadra"""
    try:
        nome = request.form.get('nome')
        logo = request.form.get('logo', '')
        girone = request.form.get('girone', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO squadre (nome, logo, girone)
            VALUES (?, ?, ?)
        ''', (nome, logo, girone))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Squadra aggiunta con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/squadra/<int:squadra_id>/update', methods=['POST'])
@login_required
def update_squadra(squadra_id):
    """API: Aggiorna una squadra"""
    try:
        nome = request.form.get('nome')
        logo = request.form.get('logo', '')
        girone = request.form.get('girone', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE squadre 
            SET nome = ?, logo = ?, girone = ?
            WHERE id = ?
        ''', (nome, logo, girone, squadra_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Squadra aggiornata con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/squadra/<int:squadra_id>/delete', methods=['POST'])
@login_required
def delete_squadra(squadra_id):
    """API: Elimina una squadra"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM squadre WHERE id = ?', (squadra_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Squadra eliminata con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== GESTIONE GIOCATORI ==========

@bp.route('/giocatore/add', methods=['POST'])
@login_required
def add_giocatore():
    """API: Aggiunge un nuovo giocatore"""
    try:
        nome = request.form.get('nome')
        squadra_id = request.form.get('squadra_id')
        goal = int(request.form.get('goal', 0))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO giocatori (nome, squadra_id, goal)
            VALUES (?, ?, ?)
        ''', (nome, squadra_id, goal))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Giocatore aggiunto con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/giocatore/<int:giocatore_id>/update', methods=['POST'])
@login_required
def update_giocatore_complete(giocatore_id):
    """API: Aggiorna completamente un giocatore"""
    try:
        nome = request.form.get('nome')
        squadra_id = request.form.get('squadra_id')
        goal = int(request.form.get('goal', 0))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE giocatori 
            SET nome = ?, squadra_id = ?, goal = ?
            WHERE id = ?
        ''', (nome, squadra_id, goal, giocatore_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Giocatore aggiornato con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/giocatore/<int:giocatore_id>/delete', methods=['POST'])
@login_required
def delete_giocatore(giocatore_id):
    """API: Elimina un giocatore"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM giocatori WHERE id = ?', (giocatore_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Giocatore eliminato con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== GESTIONE VINCITORE FINALE ==========

@bp.route('/vincitore/set', methods=['POST'])
@login_required
def set_vincitore():
    """API: Imposta il vincitore finale"""
    try:
        squadra_id = request.form.get('squadra_id')
        
        conn = get_db()
        cursor = conn.cursor()
        # Rimuovi vecchi vincitori
        cursor.execute('DELETE FROM vincitore_finale')
        # Aggiungi nuovo vincitore
        cursor.execute('INSERT INTO vincitore_finale (squadra_id) VALUES (?)', (squadra_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Vincitore finale impostato con successo'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

