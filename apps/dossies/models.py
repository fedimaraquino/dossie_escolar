"""
Aplicação DOSSIÊS - Modelos
Conforme especificação CLAUDE.md - Item 4
"""

from main import db
from datetime import datetime

class Dossie(db.Model):
    """
    Entidade: Dossiê
    Campos: Local, pasta, número do dossiê, ano, nome, CPF, nome do pai, nome da mãe, status, tipo de documento, data de cadastro, data de arquivamento, escola, observações, foto
    """
    __tablename__ = 'dossies'
    
    id = db.Column(db.Integer, primary_key=True)
    local = db.Column(db.String(100))
    pasta = db.Column(db.String(50))
    numero_dossie = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14))
    nome_pai = db.Column(db.String(100))
    nome_mae = db.Column(db.String(100))
    status = db.Column(db.String(20), default='ativo')  # ativo, arquivado, emprestado, extraviado
    tipo_documento = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_arquivamento = db.Column(db.DateTime)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    observacoes = db.Column(db.Text)
    foto_path = db.Column(db.String(255))
    usuario_cadastro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    movimentacoes = db.relationship('Movimentacao', backref='dossie', lazy=True)
    documentos = db.relationship('DocumentoDossie', backref='dossie', lazy=True)
    
    def __repr__(self):
        return f'<Dossie {self.numero_dossie}/{self.ano} - {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'local': self.local,
            'pasta': self.pasta,
            'numero_dossie': self.numero_dossie,
            'ano': self.ano,
            'nome': self.nome,
            'cpf': self.cpf,
            'nome_pai': self.nome_pai,
            'nome_mae': self.nome_mae,
            'status': self.status,
            'tipo_documento': self.tipo_documento,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_arquivamento': self.data_arquivamento.isoformat() if self.data_arquivamento else None,
            'escola_id': self.escola_id,
            'escola_nome': self.escola.nome if self.escola else None,
            'observacoes': self.observacoes,
            'foto_path': self.foto_path,
            'total_documentos': len(self.documentos),
            'total_movimentacoes': len(self.movimentacoes)
        }

class DocumentoDossie(db.Model):
    """
    Entidade: Documento do Dossiê
    """
    __tablename__ = 'documentos_dossie'
    
    id = db.Column(db.Integer, primary_key=True)
    dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_arquivo = db.Column(db.String(50))
    tamanho = db.Column(db.Integer)
    data_upload = db.Column(db.DateTime, default=datetime.now)
    usuario_upload_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    descricao = db.Column(db.Text)
    
    def __repr__(self):
        return f'<DocumentoDossie {self.nome}>'
