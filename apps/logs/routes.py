"""
Aplicação LOGS - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import LogAuditoria, LogSistema
from apps.auth.routes import verificar_login

# Criar blueprint
logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/auditoria')
def auditoria():
    """Logs de auditoria"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    # Apenas admins podem ver logs
    if usuario.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect('/')
    
    logs = LogAuditoria.query.order_by(LogAuditoria.data_hora.desc()).limit(100).all()
    
    return render_template('logs/auditoria.html', logs=logs)

@logs_bp.route('/sistema')
def sistema():
    """Logs do sistema"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    # Apenas Admin Geral pode ver logs do sistema
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect('/')
    
    logs = LogSistema.query.order_by(LogSistema.data_hora.desc()).limit(100).all()
    
    return render_template('logs/sistema.html', logs=logs)
