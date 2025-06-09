# models/escola.py
from datetime import datetime
from . import db

class Escola(db.Model):
    """
    Modelo para escolas
    Representa as instituições de ensino que utilizam o sistema
    """
    __tablename__ = 'escolas'
    
    # Campos conforme especificação
    id = db.Column(db.Integer, primary_key=True)  # id_escola
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text)
    id_cidade = db.Column(db.Integer, db.ForeignKey('cidades.id_cidade'))
    situacao = db.Column(db.String(20), default='ativa')  # ativa/inativa/suspensa
    inep = db.Column(db.String(20))
    email = db.Column(db.String(120))
    uf = db.Column(db.String(2), nullable=False)
    cnpj = db.Column(db.String(18))
    diretor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_saida = db.Column(db.DateTime)
    
    # Campos extras para compatibilidade
    telefone = db.Column(db.String(20))
    diretor = db.Column(db.String(100))  # Nome do diretor (texto)
    vice_diretor = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    cidade = db.relationship('Cidade', backref='escolas')
    diretor_obj = db.relationship('Usuario', foreign_keys=[diretor_id], 
                                 backref='escolas_dirigidas', post_update=True)
    
    def __repr__(self):
        return f'<Escola {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'id_cidade': self.id_cidade,
            'situacao': self.situacao,
            'inep': self.inep,
            'email': self.email,
            'uf': self.uf,
            'cnpj': self.cnpj,
            'diretor_id': self.diretor_id,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_saida': self.data_saida.isoformat() if self.data_saida else None,
            'telefone': self.telefone,
            'diretor': self.diretor,
            'vice_diretor': self.vice_diretor,
            'observacoes': self.observacoes
        }
    
    @property
    def nome_completo(self):
        """Retorna nome completo com cidade/UF"""
        if self.cidade:
            return f"{self.nome} - {self.cidade.nome}/{self.uf}"
        return f"{self.nome} - {self.uf}"
    
    @property
    def is_ativa(self):
        """Verifica se a escola está ativa"""
        return self.situacao == 'ativa'


class ConfiguracaoEscola(db.Model):
    """
    Entidade: Configurações da Escola
    Campos: Escola, chave, valor, tipo, descrição
    """
    __tablename__ = 'configuracoes_escola'

    id = db.Column(db.Integer, primary_key=True)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=True)  # Permite configurações globais
    chave = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='string')  # string, boolean, integer, json
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<ConfiguracaoEscola {self.chave}>'


# Configurações padrão do sistema
CONFIGURACOES_PADRAO = {
    'permitir_download': {
        'valor': 'true',
        'tipo': 'boolean',
        'descricao': 'Permitir download de documentos'
    },
    'retencao_documentos_dias': {
        'valor': '2555',  # 7 anos
        'tipo': 'integer',
        'descricao': 'Período de retenção de documentos em dias'
    },
    'permitir_exportacao': {
        'valor': 'true',
        'tipo': 'boolean',
        'descricao': 'Permitir exportação de dados'
    },
    'restringir_ip': {
        'valor': 'false',
        'tipo': 'boolean',
        'descricao': 'Restringir acesso por IP'
    },
    'ips_permitidos': {
        'valor': '[]',
        'tipo': 'json',
        'descricao': 'Lista de IPs permitidos'
    },
    'max_tentativas_login': {
        'valor': '5',
        'tipo': 'integer',
        'descricao': 'Máximo de tentativas de login'
    }
}
