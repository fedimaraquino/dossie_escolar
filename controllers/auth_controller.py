# controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do sistema"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios!', 'error')
            return render_template('auth/login_novo.html')

        # Buscar usuário
        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            flash('Email ou senha incorretos!', 'error')
            return render_template('auth/login_novo.html')

        # Verificar se está bloqueado
        if usuario.is_bloqueado:
            flash('Usuário bloqueado. Tente novamente mais tarde.', 'error')
            return render_template('auth/login_novo.html')
        
        # Verificar senha
        if usuario.check_password(senha):
            # Login bem-sucedido
            usuario.ultimo_acesso = datetime.now()
            usuario.reset_tentativas_login()
            db.session.commit()
            
            # Criar sessão
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nome
            session['user_email'] = usuario.email
            session['user_perfil'] = usuario.perfil_obj.nome
            session['escola_id'] = usuario.escola_id

            # Registrar log de login
            from utils.logs import log_acao, AcoesAuditoria
            log_acao(AcoesAuditoria.LOGIN, 'Usuario', f'Login realizado: {usuario.nome}', usuario.id)

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Senha incorreta
            usuario.incrementar_tentativas_login()
            db.session.commit()

            # Registrar log de login falhado
            from utils.logs import log_acao, AcoesAuditoria
            log_acao(AcoesAuditoria.LOGIN_FALHOU, 'Usuario', f'Login falhou: {email}')

            flash('Email ou senha incorretos!', 'error')
    
    return render_template('auth/login_novo.html')

@auth_bp.route('/logout')
def logout():
    """Logout do sistema"""
    # Registrar log de logout antes de limpar sessão
    if 'user_id' in session:
        from utils.logs import log_acao, AcoesAuditoria
        log_acao(AcoesAuditoria.LOGOUT, 'Usuario', f'Logout realizado: {session.get("user_name", "Usuário")}')

    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('auth.login'))

def login_required(f):
    """Decorator para verificar se usuário está logado"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para verificar se usuário é administrador"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso negado. Faça login primeiro.', 'error')
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or not usuario.is_admin_geral():
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
