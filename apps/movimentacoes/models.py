"""
Aplicação MOVIMENTAÇÕES - Modelos
Conforme especificação CLAUDE.md - Item 5
"""

from models import db
from datetime import datetime

class Movimentacao(db.Model):
    """
    Entidade: Movimentação
    Campos: Escola, solicitante, descrição, data de solicitação, data de devolução, status, dossiê, responsável, tipo de documentação, observação
    """
    __tablename__ = 'movimentacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('solicitantes.id'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_solicitacao = db.Column(db.DateTime, default=datetime.now)
    data_devolucao = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovada, devolvida, cancelada
    dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_documentacao = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Movimentacao {self.id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'escola_id': self.escola_id,
            'escola_nome': self.escola.nome if self.escola else None,
            'solicitante_id': self.solicitante_id,
            'solicitante_nome': self.solicitante.nome if self.solicitante else None,
            'descricao': self.descricao,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
            'status': self.status,
            'dossie_id': self.dossie_id,
            'dossie_numero': f"{self.dossie.numero_dossie}/{self.dossie.ano}" if self.dossie else None,
            'dossie_nome': self.dossie.nome if self.dossie else None,
            'responsavel_id': self.responsavel_id,
            'responsavel_nome': self.responsavel.nome if self.responsavel else None,
            'tipo_documentacao': self.tipo_documentacao,
            'observacao': self.observacao
        }
