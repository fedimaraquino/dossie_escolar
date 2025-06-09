# models/movimentacao.py
from datetime import datetime
from . import db

class Movimentacao(db.Model):
    """
    Modelo para movimentações de dossiês
    Registra todas as movimentações e alterações nos dossiês
    """
    __tablename__ = 'movimentacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id_dossie'), nullable=False)
    tipo_movimentacao = db.Column(db.String(50), nullable=False)  # consulta/emprestimo/devolucao/transferencia
    data_movimentacao = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    escola_origem_id = db.Column(db.Integer, db.ForeignKey('escolas.id'))
    escola_destino_id = db.Column(db.Integer, db.ForeignKey('escolas.id'))
    solicitante_nome = db.Column(db.String(200))
    solicitante_documento = db.Column(db.String(20))
    solicitante_telefone = db.Column(db.String(20))
    motivo = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    data_prevista_devolucao = db.Column(db.DateTime)
    data_devolucao = db.Column(db.DateTime)
    data_conclusao = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendente')  # pendente/concluido/cancelado
    
    # Relacionamentos
    dossie = db.relationship('Dossie', backref='movimentacoes')
    usuario = db.relationship('Usuario', backref='movimentacoes_realizadas')
    escola_origem = db.relationship('Escola', foreign_keys=[escola_origem_id], backref='movimentacoes_origem')
    escola_destino = db.relationship('Escola', foreign_keys=[escola_destino_id], backref='movimentacoes_destino')
    
    def __repr__(self):
        return f'<Movimentacao {self.tipo_movimentacao} - Dossiê {self.dossie_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dossie_id': self.dossie_id,
            'tipo_movimentacao': self.tipo_movimentacao,
            'data_movimentacao': self.data_movimentacao.isoformat() if self.data_movimentacao else None,
            'usuario_id': self.usuario_id,
            'escola_origem_id': self.escola_origem_id,
            'escola_destino_id': self.escola_destino_id,
            'solicitante_nome': self.solicitante_nome,
            'solicitante_documento': self.solicitante_documento,
            'solicitante_telefone': self.solicitante_telefone,
            'motivo': self.motivo,
            'observacoes': self.observacoes,
            'data_prevista_devolucao': self.data_prevista_devolucao.isoformat() if self.data_prevista_devolucao else None,
            'data_devolucao': self.data_devolucao.isoformat() if self.data_devolucao else None,
            'status': self.status
        }
    
    @property
    def is_pendente(self):
        """Verifica se a movimentação está pendente"""
        return self.status == 'pendente'
    
    @property
    def is_em_atraso(self):
        """Verifica se a movimentação está em atraso"""
        if self.data_prevista_devolucao and not self.data_devolucao:
            return datetime.now() > self.data_prevista_devolucao
        return False
    
    def marcar_como_concluida(self):
        """Marca a movimentação como concluída"""
        self.status = 'concluido'
        self.data_conclusao = datetime.now()
        if self.tipo_movimentacao in ['emprestimo', 'transferencia'] and not self.data_devolucao:
            self.data_devolucao = datetime.now()
