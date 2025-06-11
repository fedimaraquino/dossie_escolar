# utils/permission_cache.py
"""
Sistema de cache para permissões de usuários
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
import threading

# Cache em memória das permissões por usuário
permissions_cache = {}
cache_timestamps = {}
lock = threading.Lock()

# Configurações do cache
CACHE_TIMEOUT = 3600  # 1 hora em segundos
MAX_CACHE_SIZE = 1000  # Máximo de usuários no cache

def get_user_permissions(user_id):
    """
    Busca permissões do usuário do cache ou banco de dados
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        dict: Permissões do usuário {modulo: [acao1, acao2, ...]}
    """
    with lock:
        # Verificar se está no cache e não expirou
        if user_id in permissions_cache:
            timestamp = cache_timestamps.get(user_id)
            if timestamp and (datetime.now() - timestamp).total_seconds() < CACHE_TIMEOUT:
                return permissions_cache[user_id]
        
        # Buscar do banco de dados
        permissions = _load_permissions_from_db(user_id)
        
        # Armazenar no cache
        _store_in_cache(user_id, permissions)
        
        return permissions

def _load_permissions_from_db(user_id):
    """
    Carrega permissões do banco de dados
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        dict: Permissões do usuário
    """
    try:
        from models import Usuario, Perfil
        
        usuario = Usuario.query.get(user_id)
        if not usuario or not usuario.perfil_obj:
            return {}
        
        permissions = {}
        
        # Admin Geral tem todas as permissões
        if usuario.perfil_obj.perfil == 'Administrador Geral':
            # Definir todas as permissões possíveis
            all_permissions = {
                'usuario': ['criar', 'editar', 'excluir', 'visualizar'],
                'escola': ['criar', 'editar', 'excluir', 'visualizar'],
                'diretor': ['criar', 'editar', 'excluir', 'visualizar'],
                'solicitante': ['criar', 'editar', 'excluir', 'visualizar'],
                'dossie': ['criar', 'editar', 'excluir', 'visualizar'],
                'movimentacao': ['criar', 'editar', 'excluir', 'visualizar'],
                'anexo': ['criar', 'editar', 'excluir', 'visualizar'],
                'relatorio': ['visualizar', 'gerar'],
                'admin': ['total', 'backup', 'logs'],
                'permissao': ['criar', 'editar', 'excluir', 'visualizar'],
                'perfil': ['criar', 'editar', 'excluir', 'visualizar'],
                'cidade': ['criar', 'editar', 'excluir', 'visualizar'],
                'configuracao': ['criar', 'editar', 'excluir', 'visualizar']
            }
            return all_permissions
        
        # Para outros perfis, buscar permissões específicas
        from models import db
        from models.permissao import PerfilPermissao, Permissao

        permissoes_query = db.session.query(Permissao).join(PerfilPermissao).filter(
            PerfilPermissao.perfil_id == usuario.perfil_obj.id_perfil
        ).all()
        
        for perm in permissoes_query:
            if perm.modulo not in permissions:
                permissions[perm.modulo] = []
            permissions[perm.modulo].append(perm.acao)
        
        return permissions
        
    except Exception as e:
        print(f"Erro ao carregar permissões do usuário {user_id}: {e}")
        return {}

def _store_in_cache(user_id, permissions):
    """
    Armazena permissões no cache
    
    Args:
        user_id (int): ID do usuário
        permissions (dict): Permissões do usuário
    """
    # Limpar cache se estiver muito grande
    if len(permissions_cache) >= MAX_CACHE_SIZE:
        _cleanup_old_entries()
    
    permissions_cache[user_id] = permissions
    cache_timestamps[user_id] = datetime.now()

def _cleanup_old_entries():
    """Remove entradas antigas do cache"""
    now = datetime.now()
    expired_users = []
    
    for user_id, timestamp in cache_timestamps.items():
        if (now - timestamp).total_seconds() > CACHE_TIMEOUT:
            expired_users.append(user_id)
    
    for user_id in expired_users:
        if user_id in permissions_cache:
            del permissions_cache[user_id]
        if user_id in cache_timestamps:
            del cache_timestamps[user_id]

def invalidate_user_cache(user_id):
    """
    Invalida cache de um usuário específico
    
    Args:
        user_id (int): ID do usuário
    """
    with lock:
        if user_id in permissions_cache:
            del permissions_cache[user_id]
        if user_id in cache_timestamps:
            del cache_timestamps[user_id]

def invalidate_all_cache():
    """Invalida todo o cache de permissões"""
    with lock:
        permissions_cache.clear()
        cache_timestamps.clear()

def has_permission_cached(user_id, modulo, acao):
    """
    Verifica se usuário tem permissão específica (com cache)
    
    Args:
        user_id (int): ID do usuário
        modulo (str): Módulo (ex: 'usuario', 'dossie')
        acao (str): Ação (ex: 'criar', 'editar')
        
    Returns:
        bool: True se tem permissão
    """
    permissions = get_user_permissions(user_id)
    return acao in permissions.get(modulo, [])

def get_user_modules_cached(user_id):
    """
    Retorna módulos que o usuário tem acesso
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        list: Lista de módulos
    """
    permissions = get_user_permissions(user_id)
    return list(permissions.keys())

def can_access_menu_cached(user_id, menu_tipo):
    """
    Verifica se usuário pode acessar um menu específico
    
    Args:
        user_id (int): ID do usuário
        menu_tipo (str): Tipo do menu
        
    Returns:
        bool: True se pode acessar
    """
    # Mapeamento de menus para módulos
    menu_mapping = {
        'cadastro': ['usuario', 'escola', 'diretor', 'solicitante'],
        'dossie': ['dossie'],
        'movimentacao': ['movimentacao'],
        'relatorio': ['relatorio'],
        'admin': ['admin', 'permissao', 'perfil'],
        'manutencao': ['cidade', 'configuracao']
    }
    
    if menu_tipo not in menu_mapping:
        return False
    
    permissions = get_user_permissions(user_id)
    
    # Verificar se tem acesso a pelo menos um módulo do menu
    for modulo in menu_mapping[menu_tipo]:
        if modulo in permissions and permissions[modulo]:
            return True
    
    return False

def get_cache_stats():
    """
    Retorna estatísticas do cache
    
    Returns:
        dict: Estatísticas do cache
    """
    with lock:
        now = datetime.now()
        
        total_entries = len(permissions_cache)
        expired_entries = 0
        
        for timestamp in cache_timestamps.values():
            if (now - timestamp).total_seconds() > CACHE_TIMEOUT:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'cache_timeout_seconds': CACHE_TIMEOUT,
            'max_cache_size': MAX_CACHE_SIZE,
            'memory_usage_estimate': total_entries * 1024  # Estimativa em bytes
        }

def preload_user_permissions(user_ids):
    """
    Pré-carrega permissões de múltiplos usuários
    
    Args:
        user_ids (list): Lista de IDs de usuários
    """
    for user_id in user_ids:
        get_user_permissions(user_id)

def warm_cache():
    """Aquece o cache com usuários ativos"""
    try:
        from models import Usuario
        
        # Buscar usuários ativos
        usuarios_ativos = Usuario.query.filter_by(situacao='ativo').limit(100).all()
        user_ids = [u.id for u in usuarios_ativos]
        
        # Pré-carregar permissões
        preload_user_permissions(user_ids)
        
        print(f"Cache aquecido com {len(user_ids)} usuários")
        
    except Exception as e:
        print(f"Erro ao aquecer cache: {e}")

# Função para configurar cache
def configure_cache(timeout=3600, max_size=1000):
    """
    Configura parâmetros do cache
    
    Args:
        timeout (int): Timeout em segundos
        max_size (int): Tamanho máximo do cache
    """
    global CACHE_TIMEOUT, MAX_CACHE_SIZE
    CACHE_TIMEOUT = timeout
    MAX_CACHE_SIZE = max_size
