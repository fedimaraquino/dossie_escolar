# utils/rate_limiter.py
"""
Sistema de Rate Limiting manual para controle de tentativas de login
"""

from datetime import datetime, timedelta
from collections import defaultdict
import threading

# Armazenamento em memória das tentativas por IP
tentativas_por_ip = defaultdict(list)
lock = threading.Lock()

# Configurações
MAX_TENTATIVAS = 5  # Máximo de tentativas
JANELA_TEMPO = 300  # 5 minutos em segundos
BLOQUEIO_TEMPO = 900  # 15 minutos de bloqueio

def verificar_rate_limit(ip_address):
    """
    Verifica se o IP atingiu o limite de tentativas
    
    Args:
        ip_address (str): Endereço IP do cliente
        
    Returns:
        bool: True se deve ser bloqueado, False se pode prosseguir
    """
    with lock:
        agora = datetime.now()
        
        # Limpar tentativas antigas
        limpar_tentativas_antigas(ip_address, agora)
        
        # Verificar se está bloqueado
        if esta_bloqueado(ip_address, agora):
            return True
        
        # Verificar número de tentativas na janela de tempo
        tentativas = tentativas_por_ip[ip_address]
        tentativas_recentes = [t for t in tentativas if (agora - t['timestamp']).total_seconds() <= JANELA_TEMPO]
        
        return len(tentativas_recentes) >= MAX_TENTATIVAS

def registrar_tentativa(ip_address, sucesso=False):
    """
    Registra uma tentativa de login
    
    Args:
        ip_address (str): Endereço IP do cliente
        sucesso (bool): Se o login foi bem-sucedido
    """
    with lock:
        agora = datetime.now()
        
        tentativa = {
            'timestamp': agora,
            'sucesso': sucesso
        }
        
        tentativas_por_ip[ip_address].append(tentativa)
        
        # Se foi bem-sucedido, limpar tentativas anteriores
        if sucesso:
            tentativas_por_ip[ip_address] = [tentativa]
        
        # Limpar tentativas antigas
        limpar_tentativas_antigas(ip_address, agora)

def limpar_tentativas_antigas(ip_address, agora):
    """Remove tentativas antigas da memória"""
    if ip_address in tentativas_por_ip:
        # Manter apenas tentativas dos últimos 30 minutos
        limite_tempo = agora - timedelta(minutes=30)
        tentativas_por_ip[ip_address] = [
            t for t in tentativas_por_ip[ip_address] 
            if t['timestamp'] > limite_tempo
        ]
        
        # Se não há tentativas recentes, remover o IP
        if not tentativas_por_ip[ip_address]:
            del tentativas_por_ip[ip_address]

def esta_bloqueado(ip_address, agora):
    """
    Verifica se o IP está atualmente bloqueado
    
    Args:
        ip_address (str): Endereço IP
        agora (datetime): Timestamp atual
        
    Returns:
        bool: True se está bloqueado
    """
    if ip_address not in tentativas_por_ip:
        return False
    
    tentativas = tentativas_por_ip[ip_address]
    if not tentativas:
        return False
    
    # Verificar se há muitas tentativas falhadas recentes
    tentativas_falhadas = [
        t for t in tentativas 
        if not t['sucesso'] and (agora - t['timestamp']).total_seconds() <= JANELA_TEMPO
    ]
    
    if len(tentativas_falhadas) >= MAX_TENTATIVAS:
        # Verificar se ainda está no período de bloqueio
        ultima_tentativa = max(tentativas_falhadas, key=lambda x: x['timestamp'])
        tempo_bloqueio = ultima_tentativa['timestamp'] + timedelta(seconds=BLOQUEIO_TEMPO)
        return agora < tempo_bloqueio
    
    return False

def obter_tempo_restante_bloqueio(ip_address):
    """
    Retorna o tempo restante de bloqueio em segundos
    
    Args:
        ip_address (str): Endereço IP
        
    Returns:
        int: Segundos restantes de bloqueio, 0 se não está bloqueado
    """
    with lock:
        agora = datetime.now()
        
        if not esta_bloqueado(ip_address, agora):
            return 0
        
        tentativas = tentativas_por_ip.get(ip_address, [])
        tentativas_falhadas = [
            t for t in tentativas 
            if not t['sucesso'] and (agora - t['timestamp']).total_seconds() <= JANELA_TEMPO
        ]
        
        if tentativas_falhadas:
            ultima_tentativa = max(tentativas_falhadas, key=lambda x: x['timestamp'])
            tempo_bloqueio = ultima_tentativa['timestamp'] + timedelta(seconds=BLOQUEIO_TEMPO)
            restante = (tempo_bloqueio - agora).total_seconds()
            return max(0, int(restante))
        
        return 0

def obter_estatisticas():
    """
    Retorna estatísticas do rate limiter
    
    Returns:
        dict: Estatísticas de uso
    """
    with lock:
        agora = datetime.now()
        
        total_ips = len(tentativas_por_ip)
        ips_bloqueados = sum(1 for ip in tentativas_por_ip.keys() if esta_bloqueado(ip, agora))
        
        total_tentativas = sum(len(tentativas) for tentativas in tentativas_por_ip.values())
        
        return {
            'total_ips_monitorados': total_ips,
            'ips_bloqueados': ips_bloqueados,
            'total_tentativas': total_tentativas,
            'configuracao': {
                'max_tentativas': MAX_TENTATIVAS,
                'janela_tempo_minutos': JANELA_TEMPO // 60,
                'bloqueio_tempo_minutos': BLOQUEIO_TEMPO // 60
            }
        }

def limpar_cache():
    """Limpa todo o cache de tentativas (para testes)"""
    with lock:
        tentativas_por_ip.clear()

# Função para configurar limites personalizados
def configurar_limites(max_tentativas=5, janela_tempo_min=5, bloqueio_tempo_min=15):
    """
    Configura os limites do rate limiter
    
    Args:
        max_tentativas (int): Máximo de tentativas permitidas
        janela_tempo_min (int): Janela de tempo em minutos
        bloqueio_tempo_min (int): Tempo de bloqueio em minutos
    """
    global MAX_TENTATIVAS, JANELA_TEMPO, BLOQUEIO_TEMPO
    
    MAX_TENTATIVAS = max_tentativas
    JANELA_TEMPO = janela_tempo_min * 60
    BLOQUEIO_TEMPO = bloqueio_tempo_min * 60
