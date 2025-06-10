#!/usr/bin/env python3
"""
Setup simples de configurações
"""

from app import create_app

def setup_configs():
    """Setup das configurações"""
    print("🔧 SETUP DE CONFIGURAÇÕES")
    print("=" * 40)
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import db
            from models.configuracao_avancada import ConfiguracaoSistema, ConfigScope, ConfigType, ConfigCategory
            
            # Configurações básicas
            configs = [
                {
                    'chave': 'security.session.timeout_minutes',
                    'nome_exibicao': 'Timeout de Sessão (minutos)',
                    'descricao': 'Tempo limite para sessões inativas',
                    'categoria': ConfigCategory.SECURITY,
                    'tipo': ConfigType.INTEGER,
                    'valor': '30',
                    'valor_padrao': '30'
                },
                {
                    'chave': 'dossie.files.max_size_mb',
                    'nome_exibicao': 'Tamanho Máximo de Arquivo (MB)',
                    'descricao': 'Tamanho máximo permitido para arquivos',
                    'categoria': ConfigCategory.DOSSIE,
                    'tipo': ConfigType.INTEGER,
                    'valor': '10',
                    'valor_padrao': '10'
                },
                {
                    'chave': 'system.cache.enabled',
                    'nome_exibicao': 'Cache Habilitado',
                    'descricao': 'Habilitar sistema de cache',
                    'categoria': ConfigCategory.SYSTEM,
                    'tipo': ConfigType.BOOLEAN,
                    'valor': 'true',
                    'valor_padrao': 'true'
                }
            ]
            
            criadas = 0
            for config_data in configs:
                # Verificar se já existe
                existing = ConfiguracaoSistema.query.filter_by(
                    chave=config_data['chave']
                ).first()
                
                if existing:
                    print(f"   ℹ️  {config_data['chave']} já existe")
                    continue
                
                # Criar nova configuração
                config = ConfiguracaoSistema(
                    chave=config_data['chave'],
                    nome_exibicao=config_data['nome_exibicao'],
                    descricao=config_data['descricao'],
                    categoria=config_data['categoria'],
                    escopo=ConfigScope.GLOBAL,
                    tipo=config_data['tipo'],
                    valor=config_data['valor'],
                    valor_padrao=config_data['valor_padrao']
                )
                
                db.session.add(config)
                print(f"   ✅ {config_data['chave']}")
                criadas += 1
            
            db.session.commit()
            
            print(f"\n📊 Resultado: {criadas} configurações criadas")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    setup_configs()
