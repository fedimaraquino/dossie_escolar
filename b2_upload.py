#!/usr/bin/env python3
"""
Script para fazer upload de backup para B2
Usa o backup simples existente e adiciona upload B2
"""

import os
import sys
import datetime
import logging
from b2sdk.v2 import *

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('b2_upload.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_b2_config():
    """Obter configurações do B2"""
    b2_config = {
        'application_key_id': os.getenv('B2_APPLICATION_KEY_ID'),
        'application_key': os.getenv('B2_APPLICATION_KEY'),
        'bucket_name': os.getenv('B2_BUCKET_NAME', 'dossie-backups'),
        'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    }
    return b2_config

def upload_to_b2(local_file, b2_config):
    """Fazer upload do arquivo para B2"""
    try:
        # Verificar credenciais
        if not b2_config['application_key_id'] or not b2_config['application_key']:
            logger.error("Credenciais B2 nao configuradas")
            return False
        
        # Criar cliente B2
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        
        # Autenticar
        b2_api.authorize_account("production", b2_config['application_key_id'], b2_config['application_key'])
        
        # Obter bucket
        bucket = b2_api.get_bucket_by_name(b2_config['bucket_name'])
        
        # Nome do arquivo no B2
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d')
        b2_filename = f"backups/{timestamp}/{os.path.basename(local_file)}"
        
        logger.info(f"Fazendo upload para B2...")
        logger.info(f"Bucket: {b2_config['bucket_name']}")
        logger.info(f"Arquivo: {b2_filename}")
        
        # Upload do arquivo
        uploaded_file = bucket.upload_local_file(
            local_file=local_file,
            file_name=b2_filename,
            file_infos={
                'backup-date': datetime.datetime.now().isoformat(),
                'database': 'dossie_escolar',
                'type': 'postgresql'
            }
        )
        
        logger.info(f"Upload concluido com sucesso!")
        logger.info(f"ID do arquivo: {uploaded_file.id_}")
        logger.info(f"Nome: {uploaded_file.file_name}")
        logger.info(f"Tamanho: {uploaded_file.size} bytes")
        
        return uploaded_file.id_
        
    except Exception as e:
        logger.error(f"Erro no upload para B2: {str(e)}")
        return None

def cleanup_old_backups(b2_config):
    """Limpar backups antigos do B2"""
    try:
        # Verificar credenciais
        if not b2_config['application_key_id'] or not b2_config['application_key']:
            logger.error("Credenciais B2 nao configuradas para limpeza")
            return False
        
        # Criar cliente B2
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        
        # Autenticar
        b2_api.authorize_account("production", b2_config['application_key_id'], b2_config['application_key'])
        
        # Obter bucket
        bucket = b2_api.get_bucket_by_name(b2_config['bucket_name'])
        
        # Calcular data limite
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=b2_config['retention_days'])
        
        logger.info(f"Limpando backups mais antigos que {cutoff_date.strftime('%Y-%m-%d')}")
        
        # Listar arquivos
        deleted_count = 0
        for file_version, folder_name in bucket.ls(latest_only=True):
            # Verificar se é um arquivo de backup
            if file_version.file_name.startswith('backups/'):
                # Verificar se é mais antigo que o limite
                if file_version.upload_timestamp < int(cutoff_date.timestamp() * 1000):
                    bucket.delete_file_version(file_version.id_, file_version.file_name)
                    logger.info(f"Deletado: {file_version.file_name}")
                    deleted_count += 1
        
        logger.info(f"Limpeza concluida: {deleted_count} arquivos deletados")
        return True
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {str(e)}")
        return False

def cleanup_local_file(filename):
    """Remover arquivo local após upload"""
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
    logger.info("Sistema de Upload B2 - Dossie Escolar")
    logger.info("=" * 50)
    
    # Verificar se foi passado um arquivo como argumento
    if len(sys.argv) < 2:
        logger.error("Uso: python b2_upload.py <arquivo_backup>")
        return 1
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        logger.error(f"Arquivo nao encontrado: {backup_file}")
        return 1
    
    # Obter configurações
    b2_config = get_b2_config()
    
    # Verificar se B2 está configurado
    if not b2_config['application_key_id'] or not b2_config['application_key']:
        logger.error("B2 nao configurado. Configure as variaveis de ambiente:")
        logger.error("B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME")
        return 1
    
    # Upload para B2
    file_id = upload_to_b2(backup_file, b2_config)
    if file_id:
        logger.info("Backup enviado para B2 com sucesso!")
        
        # Limpar arquivo local
        cleanup_local_file(backup_file)
        
        # Limpar backups antigos
        cleanup_old_backups(b2_config)
        
        logger.info("Upload B2 concluido com sucesso!")
        return 0
    else:
        logger.error("Falha no upload para B2")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 