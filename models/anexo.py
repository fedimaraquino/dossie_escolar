# models/anexo.py
from datetime import datetime
from . import db

class Anexo(db.Model):
    """
    Modelo para anexos dos dossiês
    Armazena múltiplos arquivos por dossiê
    """
    __tablename__ = 'anexo'
    
    id = db.Column(db.Integer, primary_key=True)
    dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id_dossie'), nullable=False)
    nome = db.Column(db.String(255), nullable=False)  # Nome original do arquivo
    nome_personalizado = db.Column(db.String(255))  # Nome/descrição dado pelo usuário
    caminho = db.Column(db.String(500), nullable=False)  # Caminho onde foi salvo
    tamanho = db.Column(db.Integer)  # Tamanho em bytes
    tipo_arquivo = db.Column(db.String(50))  # Extensão do arquivo
    data_upload = db.Column(db.DateTime, default=datetime.now)
    usuario_upload_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    dossie = db.relationship('Dossie', backref='anexos')
    usuario_upload = db.relationship('Usuario', backref='anexos_enviados')
    
    def __repr__(self):
        return f'<Anexo {self.nome} - Dossiê {self.dossie_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'dossie_id': self.dossie_id,
            'nome': self.nome,
            'nome_personalizado': self.nome_personalizado,
            'caminho': self.caminho,
            'tamanho': self.tamanho,
            'tipo_arquivo': self.tipo_arquivo,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'usuario_upload_id': self.usuario_upload_id
        }
    
    @property
    def tamanho_formatado(self):
        """Retorna o tamanho formatado em KB/MB"""
        if not self.tamanho:
            return "Desconhecido"
        
        if self.tamanho < 1024:
            return f"{self.tamanho} bytes"
        elif self.tamanho < 1024 * 1024:
            return f"{self.tamanho / 1024:.1f} KB"
        else:
            return f"{self.tamanho / (1024 * 1024):.1f} MB"
    
    @property
    def icone_arquivo(self):
        """Retorna o ícone FontAwesome baseado no tipo de arquivo"""
        if not self.tipo_arquivo:
            return "fas fa-file"
        
        tipo = self.tipo_arquivo.lower()
        
        if tipo in ['pdf']:
            return "fas fa-file-pdf text-danger"
        elif tipo in ['doc', 'docx']:
            return "fas fa-file-word text-primary"
        elif tipo in ['xls', 'xlsx']:
            return "fas fa-file-excel text-success"
        elif tipo in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return "fas fa-file-image text-warning"
        elif tipo in ['txt']:
            return "fas fa-file-alt text-secondary"
        elif tipo in ['zip', 'rar', '7z']:
            return "fas fa-file-archive text-info"
        else:
            return "fas fa-file text-muted"
