#!/usr/bin/env python3
"""
Script de Backup para Backblaze B2
Cria backup do banco de dados e envia para B2
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
        logging.FileHandler('b2_backup.log'),
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
        'bucket_name': os.getenv('B2_BUCKET_NAME', 'dossie-backups'),
        'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    }
    return b2_config

def create_backup():
    """Criar backup do banco de dados"""
    try:
        config = get_db_config()
        
        # Criar nome do arquivo de backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_postgres_{timestamp}.sql"
        
        # Tentar pg_dump primeiro
        try:
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
                
        except FileNotFoundError:
            logger.info("pg_dump nao encontrado, tentando backup simples...")
            return create_simple_backup()
            
    except subprocess.TimeoutExpired:
        logger.error("Erro: Timeout ao executar backup")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return None

def create_simple_backup():
    """Criar backup simples usando Python"""
    try:
        import psycopg2
        
        config = get_db_config()
        
        # Criar nome do arquivo de backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_simple_{timestamp}.sql"
        
        logger.info(f"Criando backup simples...")
        logger.info(f"Arquivo: {backup_filename}")
        
        # Conectar ao banco
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        
        # Obter todas as tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            f.write("-- Backup Simples - Dossie Escolar\n")
            f.write(f"-- Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- Gerado automaticamente\n\n")
            
            for table in tables:
                table_name = table[0]
                logger.info(f"Backup da tabela: {table_name}")
                
                # Obter estrutura da tabela
                cursor.execute(f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position")
                columns = cursor.fetchall()
                
                f.write(f"\n-- Tabela: {table_name}\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                
                column_definitions = []
                for col in columns:
                    col_name, data_type, is_nullable, col_default = col
                    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                    default = f" DEFAULT {col_default}" if col_default else ""
                    column_definitions.append(f"    {col_name} {data_type} {nullable}{default}")
                
                f.write(",\n".join(column_definitions))
                f.write("\n);\n")
                
                # Obter dados da tabela
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"\n-- Dados da tabela {table_name}\n")
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append("NULL")
                            elif isinstance(value, str):
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            else:
                                values.append(str(value))
                        f.write(f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n")
        
        cursor.close()
        conn.close()
        
        if os.path.exists(backup_filename):
            file_size = os.path.getsize(backup_filename)
            logger.info(f"Backup simples criado com sucesso!")
            logger.info(f"Arquivo salvo: {backup_filename}")
            logger.info(f"Tamanho: {file_size / 1024:.2f} KB")
            return backup_filename
        else:
            logger.error("Erro: Arquivo de backup nao foi criado")
            return None
            
    except Exception as e:
        logger.error(f"Erro no backup simples: {str(e)}")
        return None

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
    logger.info("Sistema de Backup B2 - Dossie Escolar")
    logger.info("=" * 50)
    
    # Obter configurações
    b2_config = get_b2_config()
    
    # Verificar se B2 está configurado
    if not b2_config['application_key_id'] or not b2_config['application_key']:
        logger.error("B2 nao configurado. Configure as variaveis de ambiente:")
        logger.error("B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME")
        return 1
    
    # Criar backup
    backup_file = create_backup()
    if not backup_file:
        logger.error("Falha ao criar backup")
        return 1
    
    # Upload para B2
    file_id = upload_to_b2(backup_file, b2_config)
    if file_id:
        logger.info("Backup enviado para B2 com sucesso!")
        
        # Limpar arquivo local
        cleanup_local_file(backup_file)
        
        # Limpar backups antigos
        cleanup_old_backups(b2_config)
        
        logger.info("Backup B2 concluido com sucesso!")
        return 0
    else:
        logger.error("Falha no upload para B2")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 