# models/configuracao_avancada.py
"""
Sistema de Configurações Avançado
Suporte a configurações hierárquicas e tipadas
"""

from . import db
from datetime import datetime
import json
from enum import Enum
from sqlalchemy.ext.hybrid import hybrid_property

class ConfigScope(Enum):
    """Escopo das configurações"""
    GLOBAL = 'global'
    ESCOLA = 'escola'
    USUARIO = 'usuario'
    MODULO = 'modulo'

class ConfigType(Enum):
    """Tipos de configuração"""
    STRING = 'string'
    INTEGER = 'integer'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    JSON = 'json'
    EMAIL = 'email'
    URL = 'url'
    COLOR = 'color'
    FILE_PATH = 'file_path'

class ConfigCategory(Enum):
    """Categorias de configuração"""
    SECURITY = 'security'
    DOSSIE = 'dossie'
    ESCOLA = 'escola'
    USER_INTERFACE = 'user_interface'
    SYSTEM = 'system'
    INTEGRATION = 'integration'
    NOTIFICATION = 'notification'
    BACKUP = 'backup'

class ConfiguracaoSistema(db.Model):
    """
    Modelo avançado para configurações do sistema
    Suporte a hierarquia, validação e versionamento
    """
    __tablename__ = 'configuracoes_sistema'

    id = db.Column(db.Integer, primary_key=True)
    
    # Identificação
    chave = db.Column(db.String(100), nullable=False, index=True)
    nome_exibicao = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    
    # Hierarquia
    escopo = db.Column(db.Enum(ConfigScope), nullable=False, default=ConfigScope.GLOBAL)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    modulo = db.Column(db.String(50), nullable=True)
    
    # Categorização
    categoria = db.Column(db.Enum(ConfigCategory), nullable=False)
    subcategoria = db.Column(db.String(50))
    
    # Valor e tipo
    valor = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.Enum(ConfigType), nullable=False, default=ConfigType.STRING)
    valor_padrao = db.Column(db.Text)
    
    # Validação
    validacao_regex = db.Column(db.String(500))
    valor_minimo = db.Column(db.Float)
    valor_maximo = db.Column(db.Float)
    opcoes_validas = db.Column(db.Text)  # JSON array
    
    # Metadados
    obrigatoria = db.Column(db.Boolean, default=False)
    editavel = db.Column(db.Boolean, default=True)
    visivel_interface = db.Column(db.Boolean, default=True)
    requer_reinicializacao = db.Column(db.Boolean, default=False)
    
    # Versionamento
    versao = db.Column(db.Integer, default=1)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    data_modificacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    modificado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    escola = db.relationship('Escola', backref='configuracoes_especificas')
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='configuracoes_pessoais')
    criador = db.relationship('Usuario', foreign_keys=[criado_por])
    modificador = db.relationship('Usuario', foreign_keys=[modificado_por])
    
    # Índices compostos
    __table_args__ = (
        db.Index('idx_config_escopo_chave', 'escopo', 'chave'),
        db.Index('idx_config_escola_chave', 'escola_id', 'chave'),
        db.Index('idx_config_usuario_chave', 'usuario_id', 'chave'),
        db.Index('idx_config_categoria', 'categoria', 'subcategoria'),
        db.UniqueConstraint('chave', 'escopo', 'escola_id', 'usuario_id', 'modulo', 
                          name='uq_config_hierarquia')
    )
    
    @hybrid_property
    def valor_tipado(self):
        """Retorna o valor convertido para o tipo correto"""
        if self.tipo == ConfigType.BOOLEAN:
            return self.valor.lower() in ('true', '1', 'yes', 'on')
        elif self.tipo == ConfigType.INTEGER:
            return int(self.valor)
        elif self.tipo == ConfigType.FLOAT:
            return float(self.valor)
        elif self.tipo == ConfigType.JSON:
            return json.loads(self.valor)
        else:
            return self.valor
    
    @valor_tipado.setter
    def valor_tipado(self, value):
        """Define o valor convertendo para string"""
        if self.tipo == ConfigType.JSON:
            self.valor = json.dumps(value)
        else:
            self.valor = str(value)
    
    def validar_valor(self, valor):
        """Valida o valor conforme as regras definidas"""
        # Validação por regex
        if self.validacao_regex:
            import re
            if not re.match(self.validacao_regex, str(valor)):
                return False, f"Valor não atende ao padrão: {self.validacao_regex}"
        
        # Validação de range numérico
        if self.tipo in [ConfigType.INTEGER, ConfigType.FLOAT]:
            num_valor = float(valor)
            if self.valor_minimo is not None and num_valor < self.valor_minimo:
                return False, f"Valor deve ser maior que {self.valor_minimo}"
            if self.valor_maximo is not None and num_valor > self.valor_maximo:
                return False, f"Valor deve ser menor que {self.valor_maximo}"
        
        # Validação de opções válidas
        if self.opcoes_validas:
            opcoes = json.loads(self.opcoes_validas)
            if valor not in opcoes:
                return False, f"Valor deve ser uma das opções: {', '.join(opcoes)}"
        
        return True, "Válido"
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'chave': self.chave,
            'nome_exibicao': self.nome_exibicao,
            'descricao': self.descricao,
            'escopo': self.escopo.value,
            'categoria': self.categoria.value,
            'subcategoria': self.subcategoria,
            'valor': self.valor_tipado,
            'tipo': self.tipo.value,
            'valor_padrao': self.valor_padrao,
            'obrigatoria': self.obrigatoria,
            'editavel': self.editavel,
            'visivel_interface': self.visivel_interface,
            'data_modificacao': self.data_modificacao.isoformat() if self.data_modificacao else None
        }
    
    def __repr__(self):
        return f'<ConfiguracaoSistema {self.chave}={self.valor}>'

class HistoricoConfiguracao(db.Model):
    """
    Histórico de mudanças nas configurações
    Para auditoria e rollback
    """
    __tablename__ = 'historico_configuracoes'

    id = db.Column(db.Integer, primary_key=True)
    configuracao_id = db.Column(db.Integer, db.ForeignKey('configuracoes_sistema.id'), nullable=False)
    
    # Valores anteriores
    valor_anterior = db.Column(db.Text)
    valor_novo = db.Column(db.Text)
    
    # Metadados da mudança
    data_mudanca = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    motivo = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    
    # Relacionamentos
    configuracao = db.relationship('ConfiguracaoSistema', backref='historico')
    usuario = db.relationship('Usuario', backref='mudancas_configuracao')
    
    def __repr__(self):
        return f'<HistoricoConfiguracao {self.configuracao_id}: {self.valor_anterior} -> {self.valor_novo}>'
