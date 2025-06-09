# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar todos os modelos para registro
from .perfil import Perfil
from .permissao import Permissao, PerfilPermissao
from .cidade import Cidade
from .escola import Escola
from .usuario import Usuario
from .diretor import Diretor
from .dossie import Dossie
from .movimentacao import Movimentacao
from .anexo import Anexo

__all__ = ['db', 'Perfil', 'Permissao', 'PerfilPermissao', 'Cidade', 'Escola', 
           'Usuario', 'Diretor', 'Dossie', 'Movimentacao', 'Anexo']
