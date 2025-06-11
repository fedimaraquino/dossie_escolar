"""
Utilitários para gerenciamento de escola atual
"""

from flask import session

def get_escola_atual_id(usuario):
    """
    Retorna o ID da escola atual de trabalho para o usuário
    
    Args:
        usuario: Objeto Usuario
        
    Returns:
        int: ID da escola atual
    """
    if not usuario:
        return None
        
    if usuario.is_admin_geral():
        # Para Admin Geral, usar escola atual da sessão ou escola padrão
        return session.get('escola_atual_id', usuario.escola_id)
    else:
        # Para outros perfis, sempre usar a escola do usuário
        return usuario.escola_id

def aplicar_filtro_escola(query, model, usuario, campo_escola='escola_id'):
    """
    Aplica filtro de escola na query baseado no usuário
    
    Args:
        query: Query SQLAlchemy
        model: Modelo que contém o campo escola
        usuario: Objeto Usuario
        campo_escola: Nome do campo que contém o ID da escola
        
    Returns:
        Query filtrada
    """
    if not usuario:
        return query
        
    escola_atual_id = get_escola_atual_id(usuario)
    
    if escola_atual_id:
        # Usar getattr para acessar o campo dinamicamente
        campo = getattr(model, campo_escola)
        query = query.filter(campo == escola_atual_id)
    
    return query

def get_escolas_para_filtro(usuario):
    """
    Retorna lista de escolas para filtros baseado no perfil do usuário
    
    Args:
        usuario: Objeto Usuario
        
    Returns:
        list: Lista de escolas
    """
    from models import Escola
    
    if not usuario:
        return []
        
    if usuario.is_admin_geral():
        return Escola.query.filter_by(situacao='ativa').all()
    else:
        return [usuario.escola] if usuario.escola else []

def verificar_acesso_escola(usuario, escola_id):
    """
    Verifica se o usuário tem acesso a uma escola específica
    
    Args:
        usuario: Objeto Usuario
        escola_id: ID da escola
        
    Returns:
        bool: True se tem acesso, False caso contrário
    """
    if not usuario:
        return False
        
    if usuario.is_admin_geral():
        return True
        
    return usuario.escola_id == escola_id
