"""
Routes per il torneo (rose, classifica, partite)
"""
from flask import Blueprint, render_template
from app.models.queries import get_teams, get_standings, get_matches

bp = Blueprint('torneo', __name__)


@bp.route('/rose')
def rose():
    """Pagina rose: mostra le rose delle squadre"""
    teams = get_teams()
    return render_template('rose.html', teams=teams)


@bp.route('/classifica')
def classifica():
    """Pagina classifica: mostra la classifica per gironi"""
    standings = get_standings()
    return render_template('classifica.html', standings=standings)


@bp.route('/partite')
def partite():
    """Pagina partite: mostra tutte le partite del calendario"""
    matches = get_matches()
    return render_template('partite.html', matches=matches)

