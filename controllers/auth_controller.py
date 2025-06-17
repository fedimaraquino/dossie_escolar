# controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, Usuario
from utils.constantes import AcoesAuditoria

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do sistema com rate limiting e CAPTCHA"""
    from utils.rate_limiter import verificar_rate_limit, registrar_tentativa, obter_tempo_restante_bloqueio
    from utils.captcha import deve_mostrar_captcha, gerar_captcha, verificar_captcha

    # Rate limiting por IP
    if request.method == 'POST':
        ip_address = request.remote_addr

        # Verificar se IP está bloqueado
        if verificar_rate_limit(ip_address):
            tempo_restante = obter_tempo_restante_bloqueio(ip_address)
            minutos = tempo_restante // 60
            flash(f'Muitas tentativas de login. Tente novamente em {minutos} minutos.', 'error')
            return render_template('auth/login_novo.html')
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        if not email or not senha:
            flash('Email e senha são obrigatórios!', 'error')
            return render_template('auth/login_novo.html')

        # Verificar CAPTCHA se necessário
        ip_address = request.remote_addr
        if deve_mostrar_captcha(ip_address):
            captcha_token = request.form.get('captcha_token', '')
            captcha_resposta = request.form.get('captcha_resposta', '')

            if not captcha_token or not captcha_resposta:
                flash('CAPTCHA é obrigatório após múltiplas tentativas.', 'error')
                pergunta, _, token = gerar_captcha()
                return render_template('auth/login_novo.html',
                                     mostrar_captcha=True,
                                     captcha_pergunta=pergunta,
                                     captcha_token=token)

            if not verificar_captcha(captcha_token, captcha_resposta):
                flash('CAPTCHA incorreto. Tente novamente.', 'error')
                pergunta, _, token = gerar_captcha()
                return render_template('auth/login_novo.html',
                                     mostrar_captcha=True,
                                     captcha_pergunta=pergunta,
                                     captcha_token=token)

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

            # Registrar tentativa bem-sucedida no rate limiter
            registrar_tentativa(request.remote_addr, sucesso=True)

            # Criar sessão
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nome
            session['user_nome'] = usuario.nome  # Para compatibilidade
            session['user_email'] = usuario.email
            session['user_perfil'] = usuario.perfil_obj.nome
            session['user_foto_url'] = usuario.get_foto_url()
            session['escola_id'] = usuario.escola_id

            # Adicionar nome da escola na sessão
            if usuario.escola:
                session['escola_nome'] = usuario.escola.nome
            else:
                session['escola_nome'] = 'Escola não definida'

            # Configurar "Lembrar-me" se solicitado
            lembrar_me = request.form.get('lembrar_me')
            if lembrar_me:
                from datetime import timedelta
                from flask import current_app
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)

                # Log da ação de lembrar-me
                from utils.logs import log_acao
                log_acao(AcoesAuditoria.LOGIN_SUCESSO, 'Usuario',
                        f'Login com "Lembrar-me": {usuario.nome} ({request.remote_addr})')
            else:
                session.permanent = False

            # Para Administradores Gerais, definir escola atual de trabalho
            if usuario.is_admin_geral():
                session['escola_atual_id'] = usuario.escola_id
                session['escola_atual_nome'] = usuario.escola.nome
                session['can_switch_escola'] = usuario.can_switch_escola()
            else:
                session['escola_atual_id'] = usuario.escola_id
                session['escola_atual_nome'] = usuario.escola.nome
                session['can_switch_escola'] = False

            # Registrar log de login
            from utils.logs import log_acao
            log_acao(AcoesAuditoria.LOGIN_SUCESSO, 'Usuario', f'Login realizado: {usuario.nome}', usuario.id)

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Senha incorreta
            usuario.incrementar_tentativas_login()
            db.session.commit()

            # Registrar tentativa falhada no rate limiter
            registrar_tentativa(request.remote_addr, sucesso=False)

            # Registrar log de login falhado
            from utils.logs import log_acao
            log_acao(AcoesAuditoria.LOGIN_FALHA, 'Usuario', f'Login falhou: {email}')

            flash('Email ou senha incorretos!', 'error')

    # Para GET request, verificar se deve mostrar CAPTCHA
    ip_address = request.remote_addr
    mostrar_captcha = deve_mostrar_captcha(ip_address)
    captcha_pergunta = None
    captcha_token = None

    if mostrar_captcha:
        captcha_pergunta, _, captcha_token = gerar_captcha()

    return render_template('auth/login_novo.html',
                         mostrar_captcha=mostrar_captcha,
                         captcha_pergunta=captcha_pergunta,
                         captcha_token=captcha_token)


@auth_bp.route('/logout')
def logout():
    """Logout do sistema"""
    # Registrar log de logout antes de limpar sessão
    if 'user_id' in session:
        from utils.logs import log_acao
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
