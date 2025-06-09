# models/usuario.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Usuario(db.Model):
    """
    Modelo para usuários do sistema
    Representa os usuários que acessam o sistema
    """
    __tablename__ = 'usuarios'
    
    # Campos conforme especificação
    id = db.Column(db.Integer, primary_key=True)  # id_usuario
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil'), nullable=False)
    situacao = db.Column(db.String(20), default='ativo')  # ativo/inativo/bloqueado
    ultimo_acesso = db.Column(db.DateTime)
    data_nascimento = db.Column(db.Date)
    data_registro = db.Column(db.DateTime, default=datetime.now)
    
    # Campos de segurança
    senha_hash = db.Column(db.String(255), nullable=False)
    tentativas_login = db.Column(db.Integer, default=0)
    bloqueado_ate = db.Column(db.DateTime)
    
    # Campos extras para compatibilidade
    status = db.Column(db.String(20), default='ativo')
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    perfil_obj = db.relationship('Perfil', backref='usuarios')
    escola = db.relationship('Escola', foreign_keys=[escola_id],
                           backref='usuarios', post_update=True)
    
    def set_password(self, password):
        """Define a senha do usuário com hash"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, password)
    
    def is_admin_geral(self):
        """Verifica se é administrador geral"""
        return self.perfil_obj and self.perfil_obj.perfil == 'Administrador Geral'

    def is_admin_escola(self):
        """Verifica se é administrador da escola"""
        return self.perfil_obj and 'Administrador' in self.perfil_obj.perfil
    
    def can_access_escola(self, escola_id):
        """Verifica se pode acessar dados de uma escola específica"""
        if self.is_admin_geral():
            return True
        return self.escola_id == escola_id
    
    def reset_tentativas_login(self):
        """Reseta contador de tentativas de login"""
        self.tentativas_login = 0
        self.bloqueado_ate = None
    
    def incrementar_tentativas_login(self):
        """Incrementa tentativas de login falhadas"""
        self.tentativas_login += 1
        if self.tentativas_login >= 5:
            # Bloquear por 30 minutos após 5 tentativas
            from datetime import timedelta
            self.bloqueado_ate = datetime.now() + timedelta(minutes=30)
    
    @property
    def is_bloqueado(self):
        """Verifica se o usuário está bloqueado"""
        if self.situacao == 'bloqueado':
            return True
        if self.bloqueado_ate and datetime.now() < self.bloqueado_ate:
            return True
        return False
    
    @property
    def is_ativo(self):
        """Verifica se o usuário está ativo"""
        return self.situacao == 'ativo' and not self.is_bloqueado
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone,
            'escola_id': self.escola_id,
            'perfil_id': self.perfil_id,
            'situacao': self.situacao,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None
        }
