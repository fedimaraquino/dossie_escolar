# models/cidade.py
from . import db

class Cidade(db.Model):
    """
    Modelo para cidades
    Conforme especificação da tabela cidades
    """
    __tablename__ = 'cidades'

    id_cidade = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    pais = db.Column(db.String(50), default='Brasil')

    def __repr__(self):
        return f'<Cidade {self.nome}/{self.uf}>'

    def to_dict(self):
        return {
            'id_cidade': self.id_cidade,
            'nome': self.nome,
            'uf': self.uf,
            'pais': self.pais
        }



    @property
    def id(self):
        """Compatibilidade com código existente"""
        return self.id_cidade
