"""
Aplicação RELATÓRIOS - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from apps.auth.routes import verificar_login

# Criar blueprint
relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/')
def index():
    """Página principal de relatórios"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/index.html')

@relatorios_bp.route('/movimentacoes-solicitante')
def movimentacoes_solicitante():
    """Relatório de movimentações por solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/movimentacoes_solicitante.html')

@relatorios_bp.route('/documentos-nao-devolvidos')
def documentos_nao_devolvidos():
    """Relatório de documentos não devolvidos"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/documentos_nao_devolvidos.html')

@relatorios_bp.route('/historico-acessos')
def historico_acessos():
    """Relatório de histórico de acessos"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/historico_acessos.html')

@relatorios_bp.route('/dossies-escola')
def dossies_escola():
    """Relatório de dossiês por escola"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('relatorios/dossies_escola.html')
