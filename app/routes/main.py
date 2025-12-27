"""
Routes principali dell'applicazione
"""
from flask import Blueprint, render_template
from app.utils.utenti_online import aggiorna_utente_online
from app.models.queries import get_next_match, get_top_scorers, get_winner, get_teams

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Homepage: mostra la prossima partita"""
    aggiorna_utente_online()
    next_match = get_next_match()
    top_scorers = get_top_scorers()
    winner = get_winner()
    return render_template('index.html', next_match=next_match, top_scorers=top_scorers, winner=winner)


@bp.route('/about')
def about():
    """Pagina about: info torneo"""
    return render_template('about.html')


@bp.route('/menu')
def menu():
    """Pagina menu mobile"""
    return render_template('menu.html')


@bp.route('/cerca-giocatore')
def cerca_giocatore():
    """Pagina cerca giocatore: mostra tutte le rose per la ricerca"""
    teams = get_teams()
    return render_template('cerca_giocatore.html', teams=teams)

