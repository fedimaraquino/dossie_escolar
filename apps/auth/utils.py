"""
Aplicação AUTH - Utilitários de Autenticação e Segurança
"""

from models import db
from .models import TentativaLogin, TokenRecuperacao, SessaoUsuario, CONFIGURACOES_SEGURANCA
from datetime import datetime, timedelta
from flask import request, session
import re
import secrets
import hashlib

def registrar_tentativa_login(email, sucesso, motivo_falha=None):
    """Registrar tentativa de login"""
    
    tentativa = TentativaLogin(
        email=email,
        ip_address=request.remote_addr,
        sucesso=sucesso,
        user_agent=request.headers.get('User-Agent'),
        motivo_falha=motivo_falha
    )
    
    db.session.add(tentativa)
    db.session.commit()
    
    return tentativa

def verificar_bloqueio_ip(ip_address):
    """Verificar se IP está bloqueado por tentativas excessivas"""
    
    # Verificar tentativas nas últimas 24 horas
    data_limite = datetime.now() - timedelta(hours=24)
    
    tentativas_falhadas = TentativaLogin.query.filter(
        TentativaLogin.ip_address == ip_address,
        TentativaLogin.sucesso == False,
        TentativaLogin.data_tentativa > data_limite
    ).count()
    
    # Bloquear IP se mais de 20 tentativas falhadas em 24h
    return tentativas_falhadas >= 20

def verificar_bloqueio_usuario(email):
    """Verificar se usuário está bloqueado por tentativas excessivas"""
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        return False
    
    # Verificar se está explicitamente bloqueado
    if usuario.bloqueado_ate and usuario.bloqueado_ate > datetime.now():
        return True
    
    # Verificar tentativas recentes
    data_limite = datetime.now() - timedelta(minutes=CONFIGURACOES_SEGURANCA['TEMPO_BLOQUEIO_MINUTOS'])
    
    tentativas_falhadas = TentativaLogin.query.filter(
        TentativaLogin.email == email,
        TentativaLogin.sucesso == False,
        TentativaLogin.data_tentativa > data_limite
    ).count()
    
    return tentativas_falhadas >= CONFIGURACOES_SEGURANCA['MAX_TENTATIVAS_LOGIN']

def bloquear_usuario(usuario_id, motivo='Tentativas excessivas de login'):
    """Bloquear usuário temporariamente"""
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(usuario_id)
    
    if usuario:
        usuario.bloqueado_ate = datetime.now() + timedelta(minutes=CONFIGURACOES_SEGURANCA['TEMPO_BLOQUEIO_MINUTOS'])
        usuario.tentativas_login = 0  # Reset contador
        db.session.commit()
        
        # Log da ação
        from apps.core.utils import log_acao
        log_acao(
            usuario_id=usuario_id,
            acao='USUARIO_BLOQUEADO',
            item_alterado='Usuario',
            detalhes=f'Motivo: {motivo}',
            ip_address=request.remote_addr
        )
        
        return True
    
    return False

def gerar_token_recuperacao(email):
    """Gerar token de recuperação de senha"""
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario:
        return None
    
    # Invalidar tokens anteriores
    TokenRecuperacao.query.filter_by(usuario_id=usuario.id, usado=False).update({'usado': True})
    
    # Criar novo token
    token = TokenRecuperacao(
        usuario_id=usuario.id,
        ip_solicitacao=request.remote_addr
    )
    
    db.session.add(token)
    db.session.commit()
    
    return token

def validar_token_recuperacao(token_string):
    """Validar token de recuperação"""
    
    token = TokenRecuperacao.query.filter_by(token=token_string).first()
    
    if not token:
        return None, 'Token não encontrado'
    
    if not token.is_valido():
        return None, 'Token expirado ou já utilizado'
    
    return token, None

def validar_forca_senha(senha):
    """Validar força da senha conforme políticas"""
    
    erros = []
    
    if len(senha) < CONFIGURACOES_SEGURANCA['SENHA_MIN_CARACTERES']:
        erros.append(f"Senha deve ter pelo menos {CONFIGURACOES_SEGURANCA['SENHA_MIN_CARACTERES']} caracteres")
    
    if CONFIGURACOES_SEGURANCA['SENHA_REQUER_MAIUSCULA'] and not re.search(r'[A-Z]', senha):
        erros.append("Senha deve conter pelo menos uma letra maiúscula")
    
    if CONFIGURACOES_SEGURANCA['SENHA_REQUER_MINUSCULA'] and not re.search(r'[a-z]', senha):
        erros.append("Senha deve conter pelo menos uma letra minúscula")
    
    if CONFIGURACOES_SEGURANCA['SENHA_REQUER_NUMERO'] and not re.search(r'\d', senha):
        erros.append("Senha deve conter pelo menos um número")
    
    if CONFIGURACOES_SEGURANCA['SENHA_REQUER_ESPECIAL'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        erros.append("Senha deve conter pelo menos um caractere especial")
    
    return len(erros) == 0, erros

def criar_sessao_usuario(usuario_id):
    """Criar nova sessão para usuário"""
    
    # Encerrar sessões antigas do mesmo usuário
    SessaoUsuario.query.filter_by(usuario_id=usuario_id, ativa=True).update({'ativa': False})
    
    # Criar nova sessão
    sessao = SessaoUsuario(
        usuario_id=usuario_id,
        session_id=session.get('_id', secrets.token_hex(16)),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    db.session.add(sessao)
    db.session.commit()
    
    return sessao

def verificar_sessao_ativa(usuario_id):
    """Verificar se usuário tem sessão ativa válida"""
    
    if 'user_id' not in session or session['user_id'] != usuario_id:
        return False
    
    sessao = SessaoUsuario.query.filter_by(
        usuario_id=usuario_id,
        session_id=session.get('_id'),
        ativa=True
    ).first()
    
    if not sessao:
        return False
    
    # Verificar se sessão não expirou por inatividade
    tempo_limite = datetime.now() - timedelta(minutes=CONFIGURACOES_SEGURANCA['TEMPO_SESSAO_INATIVA_MINUTOS'])
    
    if sessao.data_ultimo_acesso < tempo_limite:
        sessao.encerrar_sessao()
        return False
    
    # Atualizar último acesso
    sessao.atualizar_ultimo_acesso()
    
    return True

def encerrar_sessao_usuario(usuario_id):
    """Encerrar todas as sessões do usuário"""
    
    SessaoUsuario.query.filter_by(usuario_id=usuario_id, ativa=True).update({'ativa': False})
    db.session.commit()

def gerar_hash_seguro(texto):
    """Gerar hash seguro para dados sensíveis"""
    
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', texto.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + hash_obj.hex()

def verificar_hash_seguro(texto, hash_completo):
    """Verificar hash seguro"""
    
    salt = hash_completo[:32]
    hash_original = hash_completo[32:]
    
    hash_obj = hashlib.pbkdf2_hmac('sha256', texto.encode('utf-8'), salt.encode('utf-8'), 100000)
    
    return hash_obj.hex() == hash_original

def obter_estatisticas_seguranca():
    """Obter estatísticas de segurança"""
    
    from apps.usuarios.models import Usuario
    
    # Últimas 24 horas
    data_limite = datetime.now() - timedelta(hours=24)
    
    stats = {
        'tentativas_login_24h': TentativaLogin.query.filter(TentativaLogin.data_tentativa > data_limite).count(),
        'tentativas_falhadas_24h': TentativaLogin.query.filter(
            TentativaLogin.data_tentativa > data_limite,
            TentativaLogin.sucesso == False
        ).count(),
        'usuarios_bloqueados': Usuario.query.filter(Usuario.bloqueado_ate > datetime.now()).count(),
        'sessoes_ativas': SessaoUsuario.query.filter_by(ativa=True).count(),
        'tokens_recuperacao_ativos': TokenRecuperacao.query.filter(
            TokenRecuperacao.usado == False,
            TokenRecuperacao.data_expiracao > datetime.now()
        ).count()
    }
    
    return stats
