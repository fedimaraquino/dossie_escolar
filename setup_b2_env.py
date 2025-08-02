#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente B2
"""

import os

def setup_b2_env():
    """Configurar variáveis de ambiente B2"""
    print("🔧 Configurando Variáveis de Ambiente B2")
    print("=" * 50)
    
    # Configurações B2
    b2_config = {
        'B2_APPLICATION_KEY_ID': '005be81810e36920000000005',
        'B2_APPLICATION_KEY': 'K005XwOmArA3gy7RYaaokuIGPK45Uk0',
        'B2_BUCKET_NAME': 'dossie-backups',
        'BACKUP_RETENTION_DAYS': '30'
    }
    
    # Configurar variáveis de ambiente
    for key, value in b2_config.items():
        os.environ[key] = value
        print(f"✅ {key} = {value[:10]}..." if len(value) > 10 else f"✅ {key} = {value}")
    
    print("\n🎉 Variáveis de ambiente configuradas!")
    print("\nAgora você pode:")
    print("1. Acessar a interface de backup em http://localhost:5000/admin/backup")
    print("2. Executar backups manuais")
    print("3. Configurar backup automático")
    print("4. Fazer upload para B2")

if __name__ == "__main__":
    setup_b2_env() 