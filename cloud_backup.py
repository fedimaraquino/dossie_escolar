#!/usr/bin/env python3
"""
Script de Backup para Google Drive
Cria backup do banco de dados e envia para Google Drive
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Escopo do Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

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

def get_drive_config():
    """Obter configurações do Google Drive"""
    drive_config = {
        'folder_id': os.getenv('GOOGLE_DRIVE_FOLDER_ID', ''),
        'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30')),
        'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
        'token_file': os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle')
    }
    return drive_config

def authenticate_google_drive(credentials_file, token_file):
    """Autenticar com Google Drive"""
    creds = None
    
    # Carregar token existente
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_backup():
    """Criar backup do banco de dados"""
    try:
        config = get_db_config()
        
        # Criar nome do arquivo de backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_postgres_{timestamp}.sql"
        
        # Comando pg_dump
        cmd = [
            'pg_dump',
            f'--host={config["host"]}',
            f'--port={config["port"]}',
            f'--username={config["user"]}',
            f'--dbname={config["database"]}',
            '--verbose',
            '--clean',
            '--no-owner',
            '--no-privileges',
            f'--file={backup_filename}'
        ]
        
        # Definir variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = config['password']
        
        logger.info(f"Iniciando backup do banco de dados...")
        logger.info(f"Arquivo: {backup_filename}")
        
        # Executar backup
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if result.returncode == 0:
            if os.path.exists(backup_filename):
                file_size = os.path.getsize(backup_filename)
                logger.info(f"Backup criado com sucesso!")
                logger.info(f"Arquivo salvo: {backup_filename}")
                logger.info(f"Tamanho: {file_size / 1024:.2f} KB")
                return backup_filename
            else:
                logger.error(f"Erro: Arquivo de backup nao foi criado")
                return None
        else:
            logger.error(f"Erro ao executar pg_dump: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Erro: Timeout ao executar backup")
        return None
    except FileNotFoundError:
        logger.error("Erro: pg_dump nao encontrado. Verifique se PostgreSQL esta instalado.")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return None

def upload_to_drive(local_file, drive_config):
    """Fazer upload do arquivo para Google Drive"""
    try:
        # Autenticar
        creds = authenticate_google_drive(
            drive_config['credentials_file'], 
            drive_config['token_file']
        )
        
        # Criar serviço do Drive
        service = build('drive', 'v3', credentials=creds)
        
        # Nome do arquivo no Drive
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        drive_filename = f"backup_dossie_{timestamp}_{os.path.basename(local_file)}"
        
        logger.info(f"Fazendo upload para Google Drive...")
        logger.info(f"Arquivo: {drive_filename}")
        
        # Metadata do arquivo
        file_metadata = {
            'name': drive_filename,
            'description': f'Backup do sistema Dossiê Escolar - {datetime.datetime.now().isoformat()}',
            'parents': [drive_config['folder_id']] if drive_config['folder_id'] else []
        }
        
        # Media do arquivo
        media = MediaFileUpload(local_file, resumable=True)
        
        # Upload do arquivo
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,name,size'
        ).execute()
        
        logger.info(f"Upload concluido com sucesso!")
        logger.info(f"ID do arquivo: {file.get('id')}")
        logger.info(f"Nome: {file.get('name')}")
        logger.info(f"Tamanho: {file.get('size')} bytes")
        
        return file.get('id')
        
    except Exception as e:
        logger.error(f"Erro no upload para Drive: {str(e)}")
        return None

def cleanup_old_backups(drive_config):
    """Limpar backups antigos do Google Drive"""
    try:
        # Autenticar
        creds = authenticate_google_drive(
            drive_config['credentials_file'], 
            drive_config['token_file']
        )
        
        service = build('drive', 'v3', credentials=creds)
        
        # Calcular data limite
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=drive_config['retention_days'])
        
        logger.info(f"Limpando backups mais antigos que {cutoff_date.strftime('%Y-%m-%d')}")
        
        # Buscar arquivos de backup
        query = "name contains 'backup_dossie' and trashed=false"
        if drive_config['folder_id']:
            query += f" and '{drive_config['folder_id']}' in parents"
        
        results = service.files().list(
            q=query,
            fields="files(id,name,createdTime)"
        ).execute()
        
        deleted_count = 0
        for file in results.get('files', []):
            # Verificar se o arquivo é mais antigo que o limite
            created_time = datetime.datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00'))
            if created_time.replace(tzinfo=None) < cutoff_date:
                service.files().delete(fileId=file['id']).execute()
                logger.info(f"Deletado: {file['name']}")
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
    logger.info("Sistema de Backup Cloud - Dossie Escolar")
    logger.info("=" * 50)
    
    # Obter configurações
    drive_config = get_drive_config()
    
    # Verificar se credenciais existem
    if not os.path.exists(drive_config['credentials_file']):
        logger.error(f"Arquivo de credenciais nao encontrado: {drive_config['credentials_file']}")
        logger.error("Configure o arquivo credentials.json do Google Drive")
        return 1
    
    # Criar backup
    backup_file = create_backup()
    if not backup_file:
        logger.error("Falha ao criar backup")
        return 1
    
    # Upload para Google Drive
    file_id = upload_to_drive(backup_file, drive_config)
    if file_id:
        logger.info("Backup enviado para Google Drive com sucesso!")
        
        # Limpar arquivo local
        cleanup_local_file(backup_file)
        
        # Limpar backups antigos
        cleanup_old_backups(drive_config)
        
        logger.info("Backup cloud concluido com sucesso!")
        return 0
    else:
        logger.error("Falha no upload para Google Drive")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 