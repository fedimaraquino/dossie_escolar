# utils/logs.py
"""
Utilitários para sistema de logs e auditoria
"""

from flask import session, request
from datetime import datetime
import traceback
import sys

def log_acao(acao, item_alterado=None, detalhes=None, usuario_id=None):
    """
    Registrar log de auditoria
    
    Args:
        acao (str): Ação realizada (ex: 'LOGIN', 'CRIAR_USUARIO', 'EDITAR_DOSSIE')
        item_alterado (str): Item que foi alterado (ex: 'Usuario', 'Dossie')
        detalhes (str): Detalhes adicionais da ação
        usuario_id (int): ID do usuário (opcional, pega da sessão se não informado)
    """
    try:
        from models import db, LogAuditoria
        
        # Obter ID do usuário da sessão se não informado
        if usuario_id is None:
            usuario_id = session.get('user_id')
        
        # Se não há usuário logado, não registra log
        if not usuario_id:
            return
        
        # Criar log de auditoria
        log = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            item_alterado=item_alterado,
            detalhes=detalhes,
            ip_address=request.remote_addr if request else None,
            navegador=request.headers.get('User-Agent') if request else None,
            data_hora=datetime.now()
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
        
    except Exception as e:
        # Se falhar ao registrar log, não deve quebrar a aplicação
        print(f"Erro ao registrar log: {e}")
        return None

def log_sistema(mensagem, nivel='INFO', modulo=None, funcao=None, usuario_id=None):
    """
    Registrar log do sistema
    
    Args:
        mensagem (str): Mensagem do log
        nivel (str): Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        modulo (str): Módulo onde ocorreu
        funcao (str): Função onde ocorreu
        usuario_id (int): ID do usuário (opcional)
    """
    try:
        from models import db, LogSistema
        
        # Obter informações do frame atual se não informado
        if not modulo or not funcao:
            frame = sys._getframe(1)
            if not modulo:
                modulo = frame.f_globals.get('__name__', 'unknown')
            if not funcao:
                funcao = frame.f_code.co_name
        
        # Obter ID do usuário da sessão se não informado
        if usuario_id is None:
            usuario_id = session.get('user_id')
        
        # Criar log do sistema
        log = LogSistema(
            mensagem_erro=mensagem,
            nivel_erro=nivel,
            modulo=modulo,
            funcao=funcao,
            linha=sys._getframe(1).f_lineno,
            usuario_id=usuario_id,
            data_hora=datetime.now()
        )
        
        db.session.add(log)
        db.session.commit()
        
        return log
        
    except Exception as e:
        # Se falhar ao registrar log, não deve quebrar a aplicação
        print(f"Erro ao registrar log do sistema: {e}")
        return None

def log_erro(erro, modulo=None, funcao=None, usuario_id=None):
    """
    Registrar erro no sistema
    
    Args:
        erro (Exception): Exceção capturada
        modulo (str): Módulo onde ocorreu
        funcao (str): Função onde ocorreu
        usuario_id (int): ID do usuário (opcional)
    """
    try:
        # Obter traceback completo
        tb_str = traceback.format_exc()
        mensagem = f"{str(erro)}\n\nTraceback:\n{tb_str}"
        
        return log_sistema(
            mensagem=mensagem,
            nivel='ERROR',
            modulo=modulo,
            funcao=funcao,
            usuario_id=usuario_id
        )
        
    except Exception as e:
        print(f"Erro ao registrar erro: {e}")
        return None

def obter_logs_auditoria(limite=100, usuario_id=None, acao=None):
    """
    Obter logs de auditoria
    
    Args:
        limite (int): Número máximo de logs
        usuario_id (int): Filtrar por usuário
        acao (str): Filtrar por ação
    
    Returns:
        list: Lista de logs
    """
    try:
        from models import LogAuditoria
        
        query = LogAuditoria.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if acao:
            query = query.filter_by(acao=acao)
        
        logs = query.order_by(LogAuditoria.data_hora.desc()).limit(limite).all()
        
        return logs
        
    except Exception as e:
        print(f"Erro ao obter logs de auditoria: {e}")
        return []

def obter_logs_sistema(limite=100, nivel=None):
    """
    Obter logs do sistema
    
    Args:
        limite (int): Número máximo de logs
        nivel (str): Filtrar por nível
    
    Returns:
        list: Lista de logs
    """
    try:
        from models import LogSistema
        
        query = LogSistema.query
        
        if nivel:
            query = query.filter_by(nivel_erro=nivel)
        
        logs = query.order_by(LogSistema.data_hora.desc()).limit(limite).all()
        
        return logs
        
    except Exception as e:
        print(f"Erro ao obter logs do sistema: {e}")
        return []

# Constantes para ações de auditoria
class AcoesAuditoria:
    # Autenticação
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    LOGIN_FALHOU = 'LOGIN_FALHOU'
    
    # Usuários
    USUARIO_CRIADO = 'USUARIO_CRIADO'
    USUARIO_EDITADO = 'USUARIO_EDITADO'
    USUARIO_EXCLUIDO = 'USUARIO_EXCLUIDO'
    USUARIO_ATIVADO = 'USUARIO_ATIVADO'
    USUARIO_DESATIVADO = 'USUARIO_DESATIVADO'
    USUARIO_VISUALIZADO = 'USUARIO_VISUALIZADO'
    
    # Dossiês
    DOSSIE_CRIADO = 'DOSSIE_CRIADO'
    DOSSIE_EDITADO = 'DOSSIE_EDITADO'
    DOSSIE_EXCLUIDO = 'DOSSIE_EXCLUIDO'
    DOSSIE_VISUALIZADO = 'DOSSIE_VISUALIZADO'
    
    # Movimentações
    MOVIMENTACAO_CRIADA = 'MOVIMENTACAO_CRIADA'
    MOVIMENTACAO_EDITADA = 'MOVIMENTACAO_EDITADA'
    MOVIMENTACAO_EXCLUIDA = 'MOVIMENTACAO_EXCLUIDA'
    MOVIMENTACAO_CONCLUIDA = 'MOVIMENTACAO_CONCLUIDA'
    
    # Solicitantes
    SOLICITANTE_CRIADO = 'SOLICITANTE_CRIADO'
    SOLICITANTE_EDITADO = 'SOLICITANTE_EDITADO'
    SOLICITANTE_EXCLUIDO = 'SOLICITANTE_EXCLUIDO'
    SOLICITANTE_ATIVADO = 'SOLICITANTE_ATIVADO'
    SOLICITANTE_DESATIVADO = 'SOLICITANTE_DESATIVADO'
    
    # Escolas
    ESCOLA_CRIADA = 'ESCOLA_CRIADA'
    ESCOLA_EDITADA = 'ESCOLA_EDITADA'
    ESCOLA_EXCLUIDA = 'ESCOLA_EXCLUIDA'
    
    # Anexos
    ANEXO_ADICIONADO = 'ANEXO_ADICIONADO'
    ANEXO_REMOVIDO = 'ANEXO_REMOVIDO'
    ANEXO_BAIXADO = 'ANEXO_BAIXADO'
    
    # Sistema
    BACKUP_CRIADO = 'BACKUP_CRIADO'
    CONFIGURACAO_ALTERADA = 'CONFIGURACAO_ALTERADA'
    PERMISSAO_ALTERADA = 'PERMISSAO_ALTERADA'
