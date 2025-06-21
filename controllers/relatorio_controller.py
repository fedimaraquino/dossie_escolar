"""
Controller para Relatórios - Integração com app.py
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Usuario, Dossie, Movimentacao
from datetime import datetime, timedelta
from app import db

# Criar blueprint
relatorio_bp = Blueprint('relatorio', __name__, url_prefix='/relatorios')

@relatorio_bp.route('/dashboard')
def dashboard():
    """Dashboard de relatórios"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    usuario = db.session.get(Usuario, session['user_id'])
    if not usuario:
        session.clear()
        flash('Sessão inválida. Faça login novamente.', 'error')
        return redirect(url_for('auth.login'))

    # Estatísticas para o dashboard
    stats = {
        'total_dossies': Dossie.query.count(),
        'total_movimentacoes': Movimentacao.query.count(),
        'movimentacoes_pendentes': Movimentacao.query.filter_by(status='pendente').count(),
        'dossies_mes_atual': Dossie.query.filter(
            Dossie.dt_cadastro >= datetime.now().replace(day=1)
        ).count()
    }

    return render_template('relatorios/dashboard.html', stats=stats)

@relatorio_bp.route('/solicitante')
def solicitante():
    """Relatório por solicitante"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    usuario = db.session.get(Usuario, session['user_id'])
    if not usuario:
        session.clear()
        flash('Sessão inválida. Faça login novamente.', 'error')
        return redirect(url_for('auth.login'))

    # Dados para o relatório
    solicitantes = Usuario.query.filter_by(tipo='solicitante').all()
    return render_template('relatorios/solicitante.html', solicitantes=solicitantes)

@relatorio_bp.route('/nao_devolvidos')
def nao_devolvidos():
    """Relatório de dossiês não devolvidos"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    usuario = db.session.get(Usuario, session['user_id'])
    if not usuario:
        session.clear()
        flash('Sessão inválida. Faça login novamente.', 'error')
        return redirect(url_for('auth.login'))

    # Dados para o relatório
    movimentacoes = Movimentacao.query.filter_by(status='emprestado').all()
    return render_template('relatorios/nao_devolvidos.html', movimentacoes=movimentacoes) 