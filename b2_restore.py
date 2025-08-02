#!/usr/bin/env python3
"""
Script de Restauração para Backblaze B2
Baixa backup do B2 e restaura no banco de dados
"""

import os
import sys
import subprocess
import datetime
import logging
from b2sdk.v2 import *
import tempfile
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('b2_restore.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_config():
    """Obter configurações do banco de dados"""
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'dossie_escolar'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
    }
    return db_config

def get_b2_config():
    """Obter configurações do B2"""
    b2_config = {
        'application_key_id': os.getenv('B2_APPLICATION_KEY_ID'),
        'application_key': os.getenv('B2_APPLICATION_KEY'),
        'bucket_name': os.getenv('B2_BUCKET_NAME', 'dossie-backups')
    }
    return b2_config

def list_backups(b2_config):
    """Listar backups disponíveis no B2"""
    try:
        # Verificar credenciais
        if not b2_config['application_key_id'] or not b2_config['application_key']:
            logger.error("Credenciais B2 nao configuradas")
            return []
        
        # Criar cliente B2
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        
        # Autenticar
        b2_api.authorize_account("production", b2_config['application_key_id'], b2_config['application_key'])
        
        # Obter bucket
        bucket = b2_api.get_bucket_by_name(b2_config['bucket_name'])
        
        # Listar arquivos de backup
        backups = []
        for file_version, folder_name in bucket.ls(latest_only=True):
            if file_version.file_name.startswith('backups/') and file_version.file_name.endswith('.sql'):
                backups.append({
                    'file_name': file_version.file_name,
                    'file_id': file_version.id_,
                    'size': file_version.size,
                    'upload_timestamp': file_version.upload_timestamp,
                    'date': datetime.datetime.fromtimestamp(file_version.upload_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['upload_timestamp'], reverse=True)
        
        return backups
        
    except Exception as e:
        logger.error(f"Erro ao listar backups: {str(e)}")
        return []

def download_backup(file_id, file_name, b2_config):
    """Baixar backup do B2"""
    try:
        # Criar cliente B2
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        
        # Autenticar
        b2_api.authorize_account("production", b2_config['application_key_id'], b2_config['application_key'])
        
        # Obter bucket
        bucket = b2_api.get_bucket_by_name(b2_config['bucket_name'])
        
        # Nome do arquivo local
        local_filename = f"restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        logger.info(f"Baixando backup: {file_name}")
        logger.info(f"Arquivo local: {local_filename}")
        
        # Download do arquivo
        bucket.download_file_by_id(file_id, local_filename)
        
        if os.path.exists(local_filename):
            file_size = os.path.getsize(local_filename)
            logger.info(f"Download concluido com sucesso!")
            logger.info(f"Tamanho: {file_size / 1024:.2f} KB")
            return local_filename
        else:
            logger.error("Erro: Arquivo nao foi baixado")
            return None
        
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return None

def restore_backup(backup_file, db_config):
    """Restaurar backup no banco de dados"""
    try:
        # Comando psql
        cmd = [
            'psql',
            f'--host={db_config["host"]}',
            f'--port={db_config["port"]}',
            f'--username={db_config["user"]}',
            f'--dbname={db_config["database"]}',
            '--file=' + backup_file
        ]
        
        # Definir variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']
        
        logger.info(f"Iniciando restauracao do banco de dados...")
        logger.info(f"Arquivo: {backup_file}")
        
        # Executar restauração
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos de timeout
        )
        
        if result.returncode == 0:
            logger.info("Restauracao concluida com sucesso!")
            return True
        else:
            logger.error(f"Erro na restauracao: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Erro: Timeout ao executar restauracao")
        return False
    except FileNotFoundError:
        logger.error("Erro: psql nao encontrado. Verifique se PostgreSQL esta instalado.")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return False

def cleanup_local_file(filename):
    """Remover arquivo local após restauração"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            logger.info(f"Arquivo local removido: {filename}")
            return True
        return False
    except Exception as e:
        logger.error(f"Erro ao remover arquivo local: {str(e)}")
        return False

def main():
    """Função principal"""
    logger.info("Sistema de Restauracao B2 - Dossie Escolar")
    logger.info("=" * 50)
    
    # Obter configurações
    b2_config = get_b2_config()
    db_config = get_db_config()
    
    # Verificar se B2 está configurado
    if not b2_config['application_key_id'] or not b2_config['application_key']:
        logger.error("B2 nao configurado. Configure as variaveis de ambiente:")
        logger.error("B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME")
        return 1
    
    # Listar backups disponíveis
    logger.info("Listando backups disponiveis...")
    backups = list_backups(b2_config)
    
    if not backups:
        logger.error("Nenhum backup encontrado no B2")
        return 1
    
    # Mostrar backups disponíveis
    print("\nBackups disponiveis:")
    for i, backup in enumerate(backups[:10]):  # Mostrar apenas os 10 mais recentes
        print(f"{i+1}. {backup['file_name']} - {backup['date']} - {backup['size']/1024:.1f} KB")
    
    # Selecionar backup
    try:
        choice = int(input("\nEscolha o numero do backup para restaurar (0 para sair): ")) - 1
        if choice < 0 or choice >= len(backups):
            logger.info("Operacao cancelada")
            return 0
        
        selected_backup = backups[choice]
        
    except (ValueError, KeyboardInterrupt):
        logger.info("Operacao cancelada")
        return 0
    
    # Confirmar restauração
    print(f"\nVoce selecionou: {selected_backup['file_name']}")
    confirm = input("Tem certeza que deseja restaurar este backup? (s/N): ").lower()
    
    if confirm != 's':
        logger.info("Restauracao cancelada")
        return 0
    
    # Baixar backup
    backup_file = download_backup(selected_backup['file_id'], selected_backup['file_name'], b2_config)
    if not backup_file:
        logger.error("Falha ao baixar backup")
        return 1
    
    # Restaurar backup
    if restore_backup(backup_file, db_config):
        logger.info("Restauracao concluida com sucesso!")
        
        # Limpar arquivo local
        cleanup_local_file(backup_file)
        
        return 0
    else:
        logger.error("Falha na restauracao")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 