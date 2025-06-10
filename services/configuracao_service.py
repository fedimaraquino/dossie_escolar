# services/configuracao_service.py
"""
Serviço para gerenciamento de configurações
Implementa cache, validação e hierarquia
"""

from flask import session, request
from models import db
from models.configuracao_avancada import (
    ConfiguracaoSistema, HistoricoConfiguracao, 
    ConfigScope, ConfigType, ConfigCategory
)
from utils.logs import log_acao, AcoesAuditoria
import json
from datetime import datetime, timedelta
from functools import lru_cache
import redis

class ConfiguracaoService:
    """Serviço centralizado para gerenciamento de configurações"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = timedelta(minutes=30)
        self.last_cache_update = {}
        
        # Redis para cache distribuído (opcional)
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        except:
            self.redis_client = None
    
    def obter_configuracao(self, chave, escola_id=None, usuario_id=None, modulo=None, default=None):
        """
        Obtém configuração seguindo hierarquia:
        1. Usuário específico
        2. Escola específica
        3. Módulo específico
        4. Global
        """
        cache_key = f"{chave}_{escola_id}_{usuario_id}_{modulo}"
        
        # Verificar cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        # Buscar na hierarquia
        config = None
        
        # 1. Configuração do usuário
        if usuario_id:
            config = ConfiguracaoSistema.query.filter_by(
                chave=chave,
                escopo=ConfigScope.USUARIO,
                usuario_id=usuario_id
            ).first()
        
        # 2. Configuração da escola
        if not config and escola_id:
            config = ConfiguracaoSistema.query.filter_by(
                chave=chave,
                escopo=ConfigScope.ESCOLA,
                escola_id=escola_id
            ).first()
        
        # 3. Configuração do módulo
        if not config and modulo:
            config = ConfiguracaoSistema.query.filter_by(
                chave=chave,
                escopo=ConfigScope.MODULO,
                modulo=modulo
            ).first()
        
        # 4. Configuração global
        if not config:
            config = ConfiguracaoSistema.query.filter_by(
                chave=chave,
                escopo=ConfigScope.GLOBAL
            ).first()
        
        # Retornar valor ou padrão
        valor = config.valor_tipado if config else default
        
        # Atualizar cache
        self._update_cache(cache_key, valor)
        
        return valor
    
    def definir_configuracao(self, chave, valor, escopo=ConfigScope.GLOBAL, 
                           escola_id=None, usuario_id=None, modulo=None, 
                           motivo=None):
        """Define uma configuração com validação e histórico"""
        
        # Buscar configuração existente
        filters = {
            'chave': chave,
            'escopo': escopo
        }
        
        if escopo == ConfigScope.ESCOLA:
            filters['escola_id'] = escola_id
        elif escopo == ConfigScope.USUARIO:
            filters['usuario_id'] = usuario_id
        elif escopo == ConfigScope.MODULO:
            filters['modulo'] = modulo
        
        config = ConfiguracaoSistema.query.filter_by(**filters).first()
        
        if config:
            # Validar novo valor
            valido, mensagem = config.validar_valor(valor)
            if not valido:
                raise ValueError(f"Valor inválido para {chave}: {mensagem}")
            
            # Salvar histórico
            self._salvar_historico(config, config.valor, str(valor), motivo)
            
            # Atualizar valor
            valor_anterior = config.valor
            config.valor_tipado = valor
            config.data_modificacao = datetime.now()
            try:
                config.modificado_por = session.get('user_id')
            except RuntimeError:
                config.modificado_por = None
            
        else:
            # Criar nova configuração
            config = ConfiguracaoSistema(
                chave=chave,
                nome_exibicao=chave.replace('_', ' ').title(),
                escopo=escopo,
                escola_id=escola_id,
                usuario_id=usuario_id,
                modulo=modulo,
                valor=str(valor),
                tipo=self._detectar_tipo(valor),
                categoria=ConfigCategory.SYSTEM,
                criado_por=session.get('user_id') if session else None
            )
            db.session.add(config)
        
        db.session.commit()
        
        # Limpar cache
        self._invalidate_cache(chave)
        
        # Log da ação
        log_acao(
            AcoesAuditoria.CONFIGURACAO_ALTERADA,
            'ConfiguracaoSistema',
            f'Configuração {chave} alterada: {valor}'
        )
        
        return config
    
    def obter_configuracoes_categoria(self, categoria, escola_id=None, usuario_id=None):
        """Obtém todas as configurações de uma categoria"""
        configs = ConfiguracaoSistema.query.filter_by(
            categoria=categoria,
            visivel_interface=True
        ).all()
        
        resultado = {}
        for config in configs:
            valor = self.obter_configuracao(
                config.chave, 
                escola_id=escola_id, 
                usuario_id=usuario_id
            )
            resultado[config.chave] = {
                'valor': valor,
                'config': config.to_dict()
            }
        
        return resultado
    
    def exportar_configuracoes(self, escola_id=None):
        """Exporta configurações para backup/migração"""
        query = ConfiguracaoSistema.query
        
        if escola_id:
            query = query.filter(
                (ConfiguracaoSistema.escola_id == escola_id) |
                (ConfiguracaoSistema.escopo == ConfigScope.GLOBAL)
            )
        
        configs = query.all()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'escola_id': escola_id,
            'configuracoes': [config.to_dict() for config in configs]
        }
    
    def importar_configuracoes(self, dados, sobrescrever=False):
        """Importa configurações de backup"""
        importadas = 0
        erros = []
        
        for config_data in dados.get('configuracoes', []):
            try:
                chave = config_data['chave']
                valor = config_data['valor']
                escopo = ConfigScope(config_data['escopo'])
                
                # Verificar se já existe
                existing = ConfiguracaoSistema.query.filter_by(
                    chave=chave,
                    escopo=escopo
                ).first()
                
                if existing and not sobrescrever:
                    continue
                
                self.definir_configuracao(
                    chave=chave,
                    valor=valor,
                    escopo=escopo,
                    motivo="Importação de backup"
                )
                
                importadas += 1
                
            except Exception as e:
                erros.append(f"Erro ao importar {config_data.get('chave', 'unknown')}: {str(e)}")
        
        return {
            'importadas': importadas,
            'erros': erros
        }
    
    def _is_cache_valid(self, cache_key):
        """Verifica se o cache ainda é válido"""
        if cache_key not in self.cache:
            return False
        
        if cache_key not in self.last_cache_update:
            return False
        
        return datetime.now() - self.last_cache_update[cache_key] < self.cache_timeout
    
    def _update_cache(self, cache_key, valor):
        """Atualiza o cache local"""
        self.cache[cache_key] = valor
        self.last_cache_update[cache_key] = datetime.now()
        
        # Atualizar Redis se disponível
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"config:{cache_key}", 
                    int(self.cache_timeout.total_seconds()), 
                    json.dumps(valor)
                )
            except:
                pass
    
    def _invalidate_cache(self, chave):
        """Invalida cache relacionado a uma chave"""
        keys_to_remove = [k for k in self.cache.keys() if k.startswith(chave)]
        for key in keys_to_remove:
            del self.cache[key]
            if key in self.last_cache_update:
                del self.last_cache_update[key]
        
        # Invalidar Redis
        if self.redis_client:
            try:
                pattern = f"config:{chave}*"
                for key in self.redis_client.scan_iter(match=pattern):
                    self.redis_client.delete(key)
            except:
                pass
    
    def _salvar_historico(self, config, valor_anterior, valor_novo, motivo):
        """Salva histórico de mudanças"""
        historico = HistoricoConfiguracao(
            configuracao_id=config.id,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
            usuario_id=session.get('user_id') if session else None,
            motivo=motivo,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(historico)
    
    def _detectar_tipo(self, valor):
        """Detecta automaticamente o tipo do valor"""
        if isinstance(valor, bool):
            return ConfigType.BOOLEAN
        elif isinstance(valor, int):
            return ConfigType.INTEGER
        elif isinstance(valor, float):
            return ConfigType.FLOAT
        elif isinstance(valor, (dict, list)):
            return ConfigType.JSON
        else:
            return ConfigType.STRING

# Instância global do serviço
config_service = ConfiguracaoService()
