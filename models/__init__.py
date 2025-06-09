# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar todos os modelos para registro
from .perfil import Perfil
from .permissao import Permissao, PerfilPermissao
from .cidade import Cidade
from .escola import Escola, ConfiguracaoEscola, CONFIGURACOES_PADRAO
from .usuario import Usuario
from .diretor import Diretor
from .dossie import Dossie
from .movimentacao import Movimentacao
from .anexo import Anexo
from .solicitante import Solicitante
from .log_auditoria import LogAuditoria, LogSistema

__all__ = ['db', 'Perfil', 'Permissao', 'PerfilPermissao', 'Cidade', 'Escola', 'ConfiguracaoEscola', 'CONFIGURACOES_PADRAO',
           'Usuario', 'Diretor', 'Dossie', 'Movimentacao', 'Anexo', 'Solicitante', 'LogAuditoria', 'LogSistema']
