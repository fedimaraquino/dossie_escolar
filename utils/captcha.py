# utils/captcha.py
"""
Sistema de CAPTCHA matemático simples para proteção contra bots
"""

import random
import hashlib
from datetime import datetime, timedelta

# Cache de captchas por sessão
captcha_cache = {}

def gerar_captcha():
    """
    Gera um CAPTCHA matemático simples
    
    Returns:
        tuple: (pergunta, resposta_hash, token)
    """
    # Gerar operação matemática simples
    operacoes = [
        lambda: (random.randint(1, 10), random.randint(1, 10), '+'),
        lambda: (random.randint(5, 15), random.randint(1, 5), '-'),
        lambda: (random.randint(1, 5), random.randint(1, 5), '*'),
    ]
    
    operacao = random.choice(operacoes)
    num1, num2, op = operacao()
    
    # Calcular resposta
    if op == '+':
        resposta = num1 + num2
        pergunta = f"Quanto é {num1} + {num2}?"
    elif op == '-':
        resposta = num1 - num2
        pergunta = f"Quanto é {num1} - {num2}?"
    elif op == '*':
        resposta = num1 * num2
        pergunta = f"Quanto é {num1} × {num2}?"
    
    # Gerar token único
    token = hashlib.md5(f"{datetime.now().isoformat()}{random.random()}".encode()).hexdigest()
    
    # Hash da resposta para segurança
    resposta_hash = hashlib.sha256(f"{resposta}{token}".encode()).hexdigest()
    
    # Armazenar no cache com expiração
    captcha_cache[token] = {
        'resposta_hash': resposta_hash,
        'criado_em': datetime.now(),
        'usado': False
    }
    
    # Limpar captchas expirados
    limpar_captchas_expirados()
    
    return pergunta, resposta_hash, token

def verificar_captcha(token, resposta_usuario):
    """
    Verifica se a resposta do CAPTCHA está correta
    
    Args:
        token (str): Token do CAPTCHA
        resposta_usuario (str): Resposta fornecida pelo usuário
        
    Returns:
        bool: True se a resposta está correta
    """
    if not token or token not in captcha_cache:
        return False
    
    captcha_data = captcha_cache[token]
    
    # Verificar se já foi usado
    if captcha_data['usado']:
        return False
    
    # Verificar se expirou (5 minutos)
    if datetime.now() - captcha_data['criado_em'] > timedelta(minutes=5):
        del captcha_cache[token]
        return False
    
    try:
        resposta_int = int(resposta_usuario.strip())
        resposta_hash = hashlib.sha256(f"{resposta_int}{token}".encode()).hexdigest()
        
        if resposta_hash == captcha_data['resposta_hash']:
            # Marcar como usado
            captcha_cache[token]['usado'] = True
            return True
    except (ValueError, TypeError):
        pass
    
    return False

def invalidar_captcha(token):
    """Remove um CAPTCHA do cache"""
    if token in captcha_cache:
        del captcha_cache[token]

def limpar_captchas_expirados():
    """Remove CAPTCHAs expirados do cache"""
    agora = datetime.now()
    tokens_expirados = []
    
    for token, data in captcha_cache.items():
        if agora - data['criado_em'] > timedelta(minutes=10):
            tokens_expirados.append(token)
    
    for token in tokens_expirados:
        del captcha_cache[token]

def deve_mostrar_captcha(ip_address):
    """
    Determina se deve mostrar CAPTCHA baseado no histórico de tentativas
    
    Args:
        ip_address (str): Endereço IP do cliente
        
    Returns:
        bool: True se deve mostrar CAPTCHA
    """
    from utils.rate_limiter import tentativas_por_ip
    
    if ip_address not in tentativas_por_ip:
        return False
    
    tentativas = tentativas_por_ip[ip_address]
    agora = datetime.now()
    
    # Contar tentativas falhadas nas últimas 2 tentativas
    tentativas_recentes = [
        t for t in tentativas 
        if not t['sucesso'] and (agora - t['timestamp']).total_seconds() <= 600  # 10 minutos
    ]
    
    # Mostrar CAPTCHA após 2 tentativas falhadas
    return len(tentativas_recentes) >= 2

def gerar_captcha_visual():
    """
    Gera um CAPTCHA visual simples com caracteres
    
    Returns:
        tuple: (codigo, token)
    """
    # Gerar código de 4 caracteres
    caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    codigo = ''.join(random.choice(caracteres) for _ in range(4))
    
    # Gerar token
    token = hashlib.md5(f"{datetime.now().isoformat()}{random.random()}".encode()).hexdigest()
    
    # Hash do código
    codigo_hash = hashlib.sha256(f"{codigo.upper()}{token}".encode()).hexdigest()
    
    # Armazenar no cache
    captcha_cache[token] = {
        'resposta_hash': codigo_hash,
        'criado_em': datetime.now(),
        'usado': False,
        'tipo': 'visual'
    }
    
    return codigo, token

def verificar_captcha_visual(token, codigo_usuario):
    """
    Verifica CAPTCHA visual
    
    Args:
        token (str): Token do CAPTCHA
        codigo_usuario (str): Código fornecido pelo usuário
        
    Returns:
        bool: True se correto
    """
    if not token or token not in captcha_cache:
        return False
    
    captcha_data = captcha_cache[token]
    
    if captcha_data.get('tipo') != 'visual':
        return False
    
    if captcha_data['usado']:
        return False
    
    if datetime.now() - captcha_data['criado_em'] > timedelta(minutes=5):
        del captcha_cache[token]
        return False
    
    try:
        codigo_hash = hashlib.sha256(f"{codigo_usuario.upper().strip()}{token}".encode()).hexdigest()
        
        if codigo_hash == captcha_data['resposta_hash']:
            captcha_cache[token]['usado'] = True
            return True
    except (ValueError, TypeError):
        pass
    
    return False

def obter_estatisticas_captcha():
    """
    Retorna estatísticas do sistema de CAPTCHA
    
    Returns:
        dict: Estatísticas
    """
    agora = datetime.now()
    
    total_captchas = len(captcha_cache)
    captchas_usados = sum(1 for data in captcha_cache.values() if data['usado'])
    captchas_expirados = sum(
        1 for data in captcha_cache.values() 
        if agora - data['criado_em'] > timedelta(minutes=5)
    )
    
    return {
        'total_captchas_ativos': total_captchas,
        'captchas_usados': captchas_usados,
        'captchas_expirados': captchas_expirados,
        'captchas_pendentes': total_captchas - captchas_usados - captchas_expirados
    }

def limpar_cache_captcha():
    """Limpa todo o cache de CAPTCHAs (para testes)"""
    global captcha_cache
    captcha_cache = {}
