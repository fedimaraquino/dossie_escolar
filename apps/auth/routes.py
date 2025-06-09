"""
Aplicação AUTH - Rotas de Autenticação e Segurança
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from .utils import (registrar_tentativa_login, verificar_bloqueio_ip, verificar_bloqueio_usuario,
                   gerar_token_recuperacao, validar_token_recuperacao, validar_forca_senha)
from apps.core.utils import log_acao

# Criar blueprint
auth_bp = Blueprint('auth', __name__)

def verificar_login():
    """Verificar se usuário está logado"""
    # Verificação simples usando apenas sessão do Flask
    if 'user_id' not in session:
        return False

    # Verificar se usuário ainda existe e está ativo
    try:
        from models import Usuario
        usuario = Usuario.query.get(session['user_id'])
        return usuario and usuario.status == 'ativo'
    except:
        return False

def login_page():
    """Página de login"""
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Processar login"""
    
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    email = request.form.get('email', '').strip().lower()
    senha = request.form.get('senha', '')
    
    # Verificar bloqueio por IP
    if verificar_bloqueio_ip(request.remote_addr):
        flash('IP bloqueado por tentativas excessivas. Tente novamente mais tarde.', 'error')
        registrar_tentativa_login(email, False, 'ip_bloqueado')
        return render_template('auth/login.html')
    
    # Verificar bloqueio do usuário
    if verificar_bloqueio_usuario(email):
        flash('Usuário temporariamente bloqueado por tentativas excessivas.', 'error')
        registrar_tentativa_login(email, False, 'usuario_bloqueado')
        return render_template('auth/login.html')
    
    # Buscar usuário
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        flash('Email não encontrado.', 'error')
        registrar_tentativa_login(email, False, 'usuario_inexistente')
        return render_template('auth/login.html')
    
    # Verificar senha
    if not usuario.check_password(senha):
        flash('Senha incorreta.', 'error')
        registrar_tentativa_login(email, False, 'senha_incorreta')
        
        # Incrementar tentativas do usuário
        usuario.tentativas_login += 1
        
        # Bloquear se atingiu o limite
        if usuario.tentativas_login >= 5:
            from .utils import bloquear_usuario
            bloquear_usuario(usuario.id)
            flash('Usuário bloqueado por tentativas excessivas.', 'error')
        
        from models import db
        db.session.commit()
        return render_template('auth/login.html')
    
    # Verificar se usuário está ativo
    if usuario.status != 'ativo':
        flash('Usuário inativo. Contate o administrador.', 'error')
        registrar_tentativa_login(email, False, 'usuario_inativo')
        return render_template('auth/login.html')
    
    # Login bem-sucedido
    usuario.tentativas_login = 0
    usuario.ultimo_acesso = datetime.now()
    usuario.bloqueado_ate = None
    
    from models import db
    db.session.commit()
    
    # Criar sessão
    session['user_id'] = usuario.id
    session['user_nome'] = usuario.nome
    session['user_email'] = usuario.email
    session['user_perfil'] = usuario.perfil_obj.nome
    session['escola_id'] = usuario.escola_id
    
    # Sessão criada automaticamente pelo Flask
    
    # Registrar tentativa bem-sucedida
    registrar_tentativa_login(email, True)
    
    # Log da ação
    log_acao(
        usuario_id=usuario.id,
        acao='LOGIN_SUCESSO',
        item_alterado='Usuario',
        detalhes=f'Login realizado com sucesso',
        ip_address=request.remote_addr
    )
    
    flash('Login realizado com sucesso!', 'success')
    
    # Redirecionar para página solicitada ou dashboard
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    """Processar logout"""
    
    if 'user_id' in session:
        # Log da ação
        log_acao(
            usuario_id=session['user_id'],
            acao='LOGOUT',
            item_alterado='Usuario',
            detalhes='Logout realizado',
            ip_address=request.remote_addr
        )
        
        # Sessão será limpa automaticamente
    
    # Limpar sessão
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    
    return redirect('/')

@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    """Recuperação de senha"""
    
    if request.method == 'GET':
        return render_template('auth/recuperar_senha.html')
    
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Por favor, informe seu email.', 'error')
        return render_template('auth/recuperar_senha.html')
    
    # Verificar se usuário existe
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        # Por segurança, não revelar se email existe ou não
        flash('Se o email estiver cadastrado, você receberá instruções para recuperação.', 'info')
        return render_template('auth/recuperar_senha.html')
    
    # Gerar token de recuperação
    token = gerar_token_recuperacao(email)
    
    if token:
        # Aqui seria enviado o email (implementar conforme necessário)
        # Por enquanto, apenas mostrar o token no log
        print(f"Token de recuperação para {email}: {token.token}")
        
        # Log da ação
        log_acao(
            usuario_id=usuario.id,
            acao='RECUPERACAO_SENHA_SOLICITADA',
            item_alterado='Usuario',
            detalhes=f'Token de recuperação gerado',
            ip_address=request.remote_addr
        )
        
        flash('Instruções de recuperação enviadas para seu email.', 'success')
    else:
        flash('Erro ao gerar token de recuperação.', 'error')
    
    return render_template('auth/recuperar_senha.html')

@auth_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    """Redefinir senha com token"""
    
    # Validar token
    token_obj, erro = validar_token_recuperacao(token)
    
    if not token_obj:
        flash(f'Token inválido: {erro}', 'error')
        return redirect(url_for('auth.recuperar_senha'))
    
    if request.method == 'GET':
        return render_template('auth/redefinir_senha.html', token=token)
    
    nova_senha = request.form.get('nova_senha', '')
    confirmar_senha = request.form.get('confirmar_senha', '')
    
    # Validar senhas
    if nova_senha != confirmar_senha:
        flash('Senhas não conferem.', 'error')
        return render_template('auth/redefinir_senha.html', token=token)
    
    # Validar força da senha
    senha_valida, erros = validar_forca_senha(nova_senha)
    if not senha_valida:
        for erro in erros:
            flash(erro, 'error')
        return render_template('auth/redefinir_senha.html', token=token)
    
    # Atualizar senha
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(token_obj.usuario_id)
    
    if usuario:
        usuario.set_password(nova_senha)
        usuario.tentativas_login = 0
        usuario.bloqueado_ate = None
        
        from models import db
        db.session.commit()
        
        # Marcar token como usado
        token_obj.marcar_como_usado()
        
        # Log da ação
        log_acao(
            usuario_id=usuario.id,
            acao='SENHA_REDEFINIDA',
            item_alterado='Usuario',
            detalhes='Senha redefinida via token de recuperação',
            ip_address=request.remote_addr
        )
        
        flash('Senha redefinida com sucesso! Faça login com a nova senha.', 'success')
        return redirect(url_for('auth.login'))
    
    flash('Erro ao redefinir senha.', 'error')
    return redirect(url_for('auth.recuperar_senha'))

@auth_bp.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    """Alterar senha do usuário logado"""
    
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('auth/alterar_senha.html')
    
    senha_atual = request.form.get('senha_atual', '')
    nova_senha = request.form.get('nova_senha', '')
    confirmar_senha = request.form.get('confirmar_senha', '')
    
    # Buscar usuário
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    # Verificar senha atual
    if not usuario.check_password(senha_atual):
        flash('Senha atual incorreta.', 'error')
        return render_template('auth/alterar_senha.html')
    
    # Validar nova senha
    if nova_senha != confirmar_senha:
        flash('Senhas não conferem.', 'error')
        return render_template('auth/alterar_senha.html')
    
    # Validar força da senha
    senha_valida, erros = validar_forca_senha(nova_senha)
    if not senha_valida:
        for erro in erros:
            flash(erro, 'error')
        return render_template('auth/alterar_senha.html')
    
    # Atualizar senha
    usuario.set_password(nova_senha)
    
    from models import db
    db.session.commit()
    
    # Log da ação
    log_acao(
        usuario_id=usuario.id,
        acao='SENHA_ALTERADA',
        item_alterado='Usuario',
        detalhes='Senha alterada pelo próprio usuário',
        ip_address=request.remote_addr
    )
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect('/')

@auth_bp.route('/api/verificar-sessao')
def api_verificar_sessao():
    """API para verificar se sessão está ativa"""
    
    ativa = verificar_login()
    
    return jsonify({
        'ativa': ativa,
        'user_id': session.get('user_id') if ativa else None,
        'user_nome': session.get('user_nome') if ativa else None
    })
