"""
Aplicação MOVIMENTAÇÕES - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Movimentacao
from apps.auth.routes import verificar_login

# Criar blueprint
movimentacoes_bp = Blueprint('movimentacoes', __name__)

@movimentacoes_bp.route('/')
def listar():
    """Listar movimentações"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    query = Movimentacao.query
    if usuario.perfil_obj.nome != 'Administrador Geral':
        query = query.filter_by(escola_id=usuario.escola_id)
    
    movimentacoes = query.order_by(Movimentacao.data_solicitacao.desc()).all()
    
    return render_template('movimentacoes/listar.html', movimentacoes=movimentacoes)

@movimentacoes_bp.route('/nova')
def nova():
    """Nova movimentação"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    return render_template('movimentacoes/nova.html')
