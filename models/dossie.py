# models/dossie.py
from datetime import datetime
from . import db

class Dossie(db.Model):
    """
    Modelo para dossiês conforme especificação da tabela
    """
    __tablename__ = 'dossies'

    # Campos conforme especificação da tabela
    id_dossie = db.Column(db.Integer, primary_key=True)
    local = db.Column(db.String(100))  # Local físico armazenado
    pasta = db.Column(db.String(50))   # Número da pasta física
    n_dossie = db.Column(db.String(50), nullable=False, unique=True)  # Número do dossiê
    ano = db.Column(db.Integer)        # Ano do dossiê
    nome = db.Column(db.String(200), nullable=False)  # Nome do aluno
    dt_cadastro = db.Column(db.DateTime, default=datetime.now)  # Data de cadastro
    cpf = db.Column(db.String(14))     # CPF do aluno
    n_pai = db.Column(db.String(200))  # Nome do pai
    n_mae = db.Column(db.String(200))  # Nome da mãe
    id_escola = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)  # FK - Escola vinculada
    status = db.Column(db.String(20), default='ativo')  # Status do dossiê
    foto = db.Column(db.String(255))   # Caminho da foto digital
    observacao = db.Column(db.Text)    # Campo de observações
    dt_arquivo = db.Column(db.DateTime)  # Data de arquivamento
    tipo_documento = db.Column(db.String(100))  # Tipo de documento contido

    # Campos adicionais para compatibilidade
    usuario_cadastro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    escola = db.relationship('Escola', backref='dossies')
    usuario_cadastro = db.relationship('Usuario', backref='dossies_cadastrados')

    def __repr__(self):
        return f'<Dossie {self.n_dossie} - {self.nome}>'

    def to_dict(self):
        return {
            'id_dossie': self.id_dossie,
            'local': self.local,
            'pasta': self.pasta,
            'n_dossie': self.n_dossie,
            'ano': self.ano,
            'nome': self.nome,
            'dt_cadastro': self.dt_cadastro.isoformat() if self.dt_cadastro else None,
            'cpf': self.cpf,
            'n_pai': self.n_pai,
            'n_mae': self.n_mae,
            'id_escola': self.id_escola,
            'status': self.status,
            'foto': self.foto,
            'foto_url': self.get_foto_url(),
            'observacao': self.observacao,
            'dt_arquivo': self.dt_arquivo.isoformat() if self.dt_arquivo else None,
            'tipo_documento': self.tipo_documento,
            'usuario_cadastro_id': self.usuario_cadastro_id
        }

    @property
    def id(self):
        """Compatibilidade com código existente"""
        return self.id_dossie

    @property
    def numero_dossie(self):
        """Compatibilidade com código existente"""
        return self.n_dossie

    @property
    def nome_aluno(self):
        """Compatibilidade com código existente"""
        return self.nome

    @property
    def situacao(self):
        """Compatibilidade com código existente"""
        return self.status

    @property
    def escola_id(self):
        """Compatibilidade com código existente"""
        return self.id_escola

    @property
    def data_cadastro(self):
        """Compatibilidade com código existente"""
        return self.dt_cadastro

    @property
    def observacoes(self):
        """Compatibilidade com código existente"""
        return self.observacao

    @property
    def is_ativo(self):
        """Verifica se o dossiê está ativo"""
        return self.status == 'ativo'

    def get_foto_url(self):
        """Retorna a URL da foto do aluno ou uma foto padrão"""
        if self.foto:
            return f"/static/uploads/dossies/{self.foto}"
        return "/static/img/default-student.svg"

    def has_foto(self):
        """Verifica se o dossiê tem foto"""
        return bool(self.foto)

    def set_foto(self, filename):
        """Define o nome do arquivo da foto"""
        self.foto = filename

    def remove_foto(self):
        """Remove a foto do dossiê"""
        import os
        if self.foto:
            foto_path = f"static/uploads/dossies/{self.foto}"
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                except:
                    pass
        self.foto = None
