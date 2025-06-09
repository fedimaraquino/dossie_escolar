"""
Aplicação AUTH - Modelos de Autenticação e Segurança
Conforme especificação CLAUDE.md - Item 1
"""

from main import db
from datetime import datetime, timedelta
import uuid

class TokenRecuperacao(db.Model):
    """
    Modelo para tokens de recuperação de senha
    """
    __tablename__ = 'tokens_recuperacao'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    data_expiracao = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    ip_solicitacao = db.Column(db.String(45))
    
    def __init__(self, usuario_id, ip_solicitacao=None):
        self.usuario_id = usuario_id
        self.token = str(uuid.uuid4())
        self.data_expiracao = datetime.now() + timedelta(hours=24)
        self.ip_solicitacao = ip_solicitacao
    
    def is_valido(self):
        """Verificar se o token ainda é válido"""
        return not self.usado and datetime.now() < self.data_expiracao
    
    def marcar_como_usado(self):
        """Marcar token como usado"""
        self.usado = True
        db.session.commit()
    
    def __repr__(self):
        return f'<TokenRecuperacao {self.token[:8]}...>'

class SessaoUsuario(db.Model):
    """
    Modelo para controle de sessões ativas
    """
    __tablename__ = 'sessoes_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    data_inicio = db.Column(db.DateTime, default=datetime.now)
    data_ultimo_acesso = db.Column(db.DateTime, default=datetime.now)
    ativa = db.Column(db.Boolean, default=True)
    
    def atualizar_ultimo_acesso(self):
        """Atualizar timestamp do último acesso"""
        self.data_ultimo_acesso = datetime.now()
        db.session.commit()
    
    def encerrar_sessao(self):
        """Encerrar sessão"""
        self.ativa = False
        db.session.commit()
    
    def __repr__(self):
        return f'<SessaoUsuario {self.session_id[:8]}...>'

class TentativaLogin(db.Model):
    """
    Modelo para rastrear tentativas de login
    """
    __tablename__ = 'tentativas_login'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    sucesso = db.Column(db.Boolean, default=False)
    data_tentativa = db.Column(db.DateTime, default=datetime.now)
    user_agent = db.Column(db.Text)
    motivo_falha = db.Column(db.String(100))  # senha_incorreta, usuario_inexistente, usuario_bloqueado
    
    def __repr__(self):
        return f'<TentativaLogin {self.email} - {self.sucesso}>'

# Configurações de segurança
CONFIGURACOES_SEGURANCA = {
    'MAX_TENTATIVAS_LOGIN': 5,
    'TEMPO_BLOQUEIO_MINUTOS': 30,
    'TEMPO_EXPIRACAO_TOKEN_HORAS': 24,
    'TEMPO_SESSAO_INATIVA_MINUTOS': 120,
    'FORCAR_HTTPS': False,
    'SENHA_MIN_CARACTERES': 8,
    'SENHA_REQUER_MAIUSCULA': True,
    'SENHA_REQUER_MINUSCULA': True,
    'SENHA_REQUER_NUMERO': True,
    'SENHA_REQUER_ESPECIAL': False
}
