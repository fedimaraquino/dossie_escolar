# controllers/__init__.py
"""
Controladores da aplicação organizados por entidade
"""

from .auth_controller import auth_bp
from .escola_controller import escola_bp
from .usuario_controller import usuario_bp
from .dossie_controller import dossie_bp
from .movimentacao_controller import movimentacao_bp
from .cidade_controller import cidade_bp
from .perfil_controller import perfil_bp
from .anexo_controller import anexo_bp

__all__ = ['auth_bp', 'escola_bp', 'usuario_bp', 'dossie_bp', 'movimentacao_bp', 'cidade_bp', 'perfil_bp', 'anexo_bp']
