# models/log_auditoria.py
from . import db
from datetime import datetime

class LogAuditoria(db.Model):
    """
    Modelo para logs de auditoria do sistema
    Registra todas as ações importantes dos usuários
    """
    __tablename__ = 'logs_auditoria'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)
    item_alterado = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    navegador = db.Column(db.String(200))
    detalhes = db.Column(db.Text)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='logs_auditoria')
    
    def __repr__(self):
        return f'<LogAuditoria {self.acao} - {self.data_hora}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'acao': self.acao,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'item_alterado': self.item_alterado,
            'ip_address': self.ip_address,
            'navegador': self.navegador,
            'detalhes': self.detalhes
        }

class LogSistema(db.Model):
    """
    Modelo para logs do sistema
    Registra erros e eventos importantes do sistema
    """
    __tablename__ = 'logs_sistema'

    id = db.Column(db.Integer, primary_key=True)
    mensagem_erro = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    nivel_erro = db.Column(db.String(20), default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    data_hora = db.Column(db.DateTime, default=datetime.now)
    modulo = db.Column(db.String(50))
    funcao = db.Column(db.String(100))
    linha = db.Column(db.Integer)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='logs_sistema')
    
    def __repr__(self):
        return f'<LogSistema {self.nivel_erro} - {self.data_hora}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'mensagem_erro': self.mensagem_erro,
            'usuario_id': self.usuario_id,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'nivel_erro': self.nivel_erro,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'modulo': self.modulo,
            'funcao': self.funcao,
            'linha': self.linha
        }
