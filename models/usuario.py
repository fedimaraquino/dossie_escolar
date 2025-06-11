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
    foto = db.Column(db.String(255))  # Caminho para a foto do usuário
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

    def get_foto_url(self):
        """Retorna a URL da foto do usuário ou uma foto padrão"""
        if self.foto:
            return f"/static/uploads/fotos/{self.foto}"
        return "/static/img/default-avatar.svg"

    def has_foto(self):
        """Verifica se o usuário tem foto"""
        return bool(self.foto)

    def set_foto(self, filename):
        """Define o nome do arquivo da foto"""
        self.foto = filename

    def remove_foto(self):
        """Remove a foto do usuário"""
        import os
        if self.foto:
            foto_path = f"static/uploads/fotos/{self.foto}"
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                except:
                    pass  # Não falhar se não conseguir remover
        self.foto = None

    def get_escolas_acessiveis(self):
        """Retorna lista de escolas que o usuário pode acessar"""
        from .escola import Escola

        if self.is_admin_geral():
            # Admin Geral pode acessar todas as escolas ativas
            return Escola.query.filter_by(situacao='ativa').all()
        else:
            # Outros perfis só acessam sua escola
            return [self.escola] if self.escola else []

    def can_switch_escola(self):
        """Verifica se o usuário pode trocar de escola"""
        return self.is_admin_geral() and len(self.get_escolas_acessiveis()) > 1

    def get_escola_atual_id(self):
        """Retorna o ID da escola atual de trabalho"""
        from flask import session
        if self.is_admin_geral():
            # Para Admin Geral, usar escola atual da sessão ou escola padrão
            return session.get('escola_atual_id', self.escola_id)
        else:
            # Para outros perfis, sempre usar a escola do usuário
            return self.escola_id
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone,
            'foto': self.foto,
            'foto_url': self.get_foto_url(),
            'escola_id': self.escola_id,
            'perfil_id': self.perfil_id,
            'situacao': self.situacao,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None
        }
