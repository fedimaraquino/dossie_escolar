"""
Aplicação CORE - Modelos das Entidades Auxiliares
Conforme especificação CLAUDE.md - Item 8
"""

from models import db
from datetime import datetime

class Cidade(db.Model):
    """
    Entidade: Cidades
    Campos: Nome, UF, país
    """
    __tablename__ = 'cidades'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    pais = db.Column(db.String(50), default='Brasil')
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    escolas = db.relationship('Escola', backref='cidade', lazy=True)
    solicitantes = db.relationship('Solicitante', backref='cidade', lazy=True)
    
    def __repr__(self):
        return f'<Cidade {self.nome}/{self.uf}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'uf': self.uf,
            'pais': self.pais,
            'ativo': self.ativo
        }

class Perfil(db.Model):
    """
    Entidade: Perfil
    Campos: Nome do perfil
    """
    __tablename__ = 'perfis'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    nivel_acesso = db.Column(db.Integer, default=1)  # 1=baixo, 5=alto
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', backref='perfil_obj', lazy=True)
    
    def __repr__(self):
        return f'<Perfil {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'nivel_acesso': self.nivel_acesso,
            'ativo': self.ativo
        }

class ConfiguracaoEscola(db.Model):
    """
    Entidade: Configurações por Escola
    Conforme especificação CLAUDE.md - Políticas de Configurações
    """
    __tablename__ = 'configuracoes_escola'
    
    id = db.Column(db.Integer, primary_key=True)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    chave = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='string')  # string, boolean, integer, json
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<ConfiguracaoEscola {self.chave}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'escola_id': self.escola_id,
            'chave': self.chave,
            'valor': self.valor,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'ativo': self.ativo
        }
    
    def get_valor_tipado(self):
        """Retorna o valor convertido para o tipo correto"""
        if self.tipo == 'boolean':
            return self.valor.lower() in ['true', '1', 'sim', 'yes']
        elif self.tipo == 'integer':
            try:
                return int(self.valor)
            except (ValueError, TypeError):
                return 0
        elif self.tipo == 'json':
            try:
                import json
                return json.loads(self.valor)
            except (ValueError, TypeError):
                return {}
        else:
            return self.valor

class PermissaoCustomizada(db.Model):
    """
    Entidade: Permissões customizadas
    Campos: Recurso, permissão, usuário relacionado
    """
    __tablename__ = 'permissoes_customizadas'
    
    id = db.Column(db.Integer, primary_key=True)
    recurso = db.Column(db.String(100), nullable=False)
    permissao = db.Column(db.String(50), nullable=False)  # create, read, update, delete
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    concedida = db.Column(db.Boolean, default=True)
    data_concessao = db.Column(db.DateTime, default=datetime.now)
    data_revogacao = db.Column(db.DateTime)
    motivo = db.Column(db.Text)
    
    def __repr__(self):
        return f'<PermissaoCustomizada {self.recurso}:{self.permissao}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'recurso': self.recurso,
            'permissao': self.permissao,
            'usuario_id': self.usuario_id,
            'concedida': self.concedida,
            'data_concessao': self.data_concessao.isoformat() if self.data_concessao else None
        }

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
    },
    'tempo_bloqueio_minutos': {
        'valor': '30',
        'tipo': 'integer',
        'descricao': 'Tempo de bloqueio após tentativas excessivas'
    },
    'backup_automatico': {
        'valor': 'true',
        'tipo': 'boolean',
        'descricao': 'Realizar backup automático'
    },
    'notificar_movimentacoes': {
        'valor': 'true',
        'tipo': 'boolean',
        'descricao': 'Notificar sobre movimentações pendentes'
    },
    'dias_alerta_devolucao': {
        'valor': '7',
        'tipo': 'integer',
        'descricao': 'Dias para alerta de devolução'
    }
}
