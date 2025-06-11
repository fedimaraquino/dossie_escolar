# utils/permissions.py - Utilitários para verificação de permissões

from functools import wraps
from flask import session, flash, redirect, url_for, abort
from models import Usuario

def require_permission(modulo, acao):
    """
    Decorator para verificar se o usuário tem uma permissão específica
    
    Uso:
    @require_permission('dossie', 'criar')
    def criar_dossie():
        # código aqui
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar se usuário está logado
            if 'user_id' not in session:
                flash('Acesso negado. Faça login.', 'error')
                return redirect(url_for('auth.login'))
            
            # Buscar usuário
            usuario = Usuario.query.get(session['user_id'])
            if not usuario:
                flash('Usuário não encontrado.', 'error')
                return redirect(url_for('auth.login'))
            
            # Verificar permissão
            tem_permissao = has_permission(usuario, modulo, acao)

            # Log detalhado da verificação de permissão
            from utils.logs import log_acao, AcoesAuditoria
            from flask import request, current_app
            import json

            detalhes_log = {
                'usuario_id': usuario.id,
                'usuario_nome': usuario.nome,
                'modulo': modulo,
                'acao': acao,
                'resultado': 'PERMITIDO' if tem_permissao else 'NEGADO',
                'ip_origem': request.remote_addr if request else 'N/A',
                'url_solicitada': request.url if request else 'N/A',
                'metodo_http': request.method if request else 'N/A',
                'user_agent': request.headers.get('User-Agent') if request else 'N/A',
                'funcao': f.__name__
            }

            if not tem_permissao:
                # Log específico para acessos negados
                log_acao(AcoesAuditoria.ACESSO_NEGADO, 'Permissao',
                        f'Acesso negado: {usuario.nome} tentou {acao} em {modulo}',
                        detalhes=json.dumps(detalhes_log))

                flash(f'Acesso negado. Você não tem permissão para {acao} {modulo}.', 'error')
                return abort(403)
            else:
                # Log para acessos permitidos (apenas em debug)
                if current_app.debug:
                    log_acao(AcoesAuditoria.ACESSO_PERMITIDO, 'Permissao',
                            f'Acesso permitido: {usuario.nome} executou {acao} em {modulo}',
                            detalhes=json.dumps(detalhes_log))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_permission(usuario, modulo, acao):
    """
    Verifica se um usuário tem uma permissão específica
    
    Args:
        usuario: Objeto Usuario
        modulo: string (ex: 'dossie', 'usuario', 'escola')
        acao: string (ex: 'criar', 'editar', 'excluir', 'visualizar')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not usuario or not usuario.perfil_obj:
        return False
    
    # Administrador Geral tem todas as permissões
    if usuario.perfil_obj.perfil == 'Administrador Geral':
        return True

    # Usar cache para verificação de permissões
    from utils.permission_cache import has_permission_cached
    return has_permission_cached(usuario.id, modulo, acao)

def can_create(usuario, modulo):
    """Verifica se pode criar registros no módulo"""
    return has_permission(usuario, modulo, 'criar')

def can_edit(usuario, modulo):
    """Verifica se pode editar registros no módulo"""
    return has_permission(usuario, modulo, 'editar')

def can_delete(usuario, modulo):
    """Verifica se pode excluir registros no módulo"""
    return has_permission(usuario, modulo, 'excluir')

def can_view(usuario, modulo):
    """Verifica se pode visualizar registros no módulo"""
    return has_permission(usuario, modulo, 'visualizar')

def get_user_permissions(usuario):
    """
    Retorna todas as permissões de um usuário
    
    Returns:
        dict: {modulo: [acao1, acao2, ...]}
    """
    if not usuario or not usuario.perfil_obj:
        return {}
    
    permissoes = usuario.perfil_obj.get_permissoes()
    
    # Agrupar por módulo
    modulos = {}
    for perm in permissoes:
        if perm.modulo not in modulos:
            modulos[perm.modulo] = []
        modulos[perm.modulo].append(perm.acao)
    
    return modulos

def check_escola_access(usuario, escola_id):
    """
    Verifica se usuário pode acessar dados de uma escola específica

    Args:
        usuario: Objeto Usuario
        escola_id: ID da escola

    Returns:
        bool: True se pode acessar, False caso contrário
    """
    if not usuario:
        return False

    # Admin Geral acessa todas as escolas
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        return True

    # Usuários só acessam sua própria escola
    return usuario.escola_id == escola_id

def can_access_menu(usuario, menu_tipo):
    """
    Verifica se usuário pode acessar um menu específico

    Args:
        usuario: Objeto Usuario
        menu_tipo: string ('manutencao', 'dossie', 'movimentacao', 'relatorio', 'admin')

    Returns:
        bool: True se pode acessar, False caso contrário
    """
    if not usuario:
        return False

    # Admin Geral acessa todos os menus
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        return True

    # Verificar permissão específica do menu
    return has_permission(usuario, 'menu', menu_tipo)

# Constantes para facilitar o uso
class Modulos:
    USUARIO = 'usuario'
    ESCOLA = 'escola'
    DIRETOR = 'diretor'
    CIDADE = 'cidade'
    DOSSIE = 'dossie'
    ANEXO = 'anexo'
    MOVIMENTACAO = 'movimentacao'
    RELATORIO = 'relatorio'
    ADMIN = 'admin'
    PERFIL = 'perfil'
    PERMISSAO = 'permissao'
    MENU = 'menu'
    SOLICITANTE = 'solicitante'

class Acoes:
    CRIAR = 'criar'
    EDITAR = 'editar'
    EXCLUIR = 'excluir'
    VISUALIZAR = 'visualizar'
    TOTAL = 'total'
    BACKUP = 'backup'
    LOGS = 'logs'
    MANUTENCAO = 'manutencao'
    DOSSIE = 'dossie'
    MOVIMENTACAO = 'movimentacao'
    RELATORIO = 'relatorio'
    ADMIN = 'admin'

# Exemplos de uso:
# @require_permission(Modulos.DOSSIE, Acoes.CRIAR)
# @require_permission('dossie', 'editar')
# if has_permission(usuario, 'usuario', 'criar'):
#     # código aqui
