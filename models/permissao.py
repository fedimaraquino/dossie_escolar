# models/permissao.py
from . import db

class Permissao(db.Model):
    """
    Modelo para permissões do sistema
    Define o que cada perfil pode fazer
    """
    __tablename__ = 'permissoes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    modulo = db.Column(db.String(50))  # usuario, escola, dossie, etc.
    acao = db.Column(db.String(50))    # criar, editar, excluir, visualizar
    
    def __repr__(self):
        return f'<Permissao {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'modulo': self.modulo,
            'acao': self.acao
        }

class PerfilPermissao(db.Model):
    """
    Relacionamento entre Perfis e Permissões (Many-to-Many)
    """
    __tablename__ = 'perfil_permissoes'
    
    id = db.Column(db.Integer, primary_key=True)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfil.id_perfil'), nullable=False)
    permissao_id = db.Column(db.Integer, db.ForeignKey('permissoes.id'), nullable=False)
    
    # Relacionamentos
    perfil = db.relationship('Perfil', backref='perfil_permissoes')
    permissao = db.relationship('Permissao', backref='perfil_permissoes')
    
    def __repr__(self):
        return f'<PerfilPermissao {self.perfil_id}-{self.permissao_id}>'
