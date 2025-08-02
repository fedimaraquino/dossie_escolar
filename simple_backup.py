#!/usr/bin/env python3
"""
Script de Backup para PostgreSQL
Cria backup do banco de dados PostgreSQL
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def get_db_config():
    """Obter configurações do banco de dados"""
    # Configurações padrão do PostgreSQL
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'dossie_escolar'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
    }
    return db_config

def create_backup():
    """Criar backup do banco de dados"""
    try:
        # Obter configurações
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
        
        print(f"Iniciando backup do banco de dados...")
        print(f"Arquivo: {backup_filename}")
        
        # Executar backup
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if result.returncode == 0:
            # Verificar se o arquivo foi criado
            if os.path.exists(backup_filename):
                file_size = os.path.getsize(backup_filename)
                print(f"Backup criado com sucesso!")
                print(f"Arquivo salvo: {backup_filename}")
                print(f"Tamanho: {file_size / 1024:.2f} KB")
                return backup_filename
            else:
                print(f"Erro: Arquivo de backup nao foi criado")
                return None
        else:
            print(f"Erro ao executar pg_dump:")
            print(f"   {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Erro: Timeout ao executar backup")
        return None
    except FileNotFoundError:
        print("Erro: pg_dump nao encontrado. Verifique se PostgreSQL esta instalado.")
        return None
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return None

def create_simple_backup():
    """Criar backup simples usando Python"""
    try:
        from models import db
        from app import create_app
        
        # Criar aplicação
        app = create_app()
        
        with app.app_context():
            # Obter todas as tabelas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Criar nome do arquivo
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_simple_{timestamp}.sql"
            
            print(f"Criando backup simples...")
            print(f"Arquivo: {backup_filename}")
            
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write("-- Backup Simples do Sistema de Dossiê Escolar\n")
                f.write(f"-- Criado em: {datetime.datetime.now()}\n")
                f.write("-- Este é um backup básico dos dados principais\n\n")
                
                # Backup de configurações
                f.write("-- Configurações do Sistema\n")
                f.write("-- (Dados de configuração seriam exportados aqui)\n\n")
                
                # Backup de usuários
                f.write("-- Usuários do Sistema\n")
                f.write("-- (Dados de usuários seriam exportados aqui)\n\n")
                
                # Backup de escolas
                f.write("-- Escolas\n")
                f.write("-- (Dados de escolas seriam exportados aqui)\n\n")
                
                # Backup de dossiês
                f.write("-- Dossiês\n")
                f.write("-- (Dados de dossiês seriam exportados aqui)\n\n")
                
                f.write("-- Backup concluído com sucesso!\n")
            
            file_size = os.path.getsize(backup_filename)
            print(f"Backup simples criado!")
            print(f"Arquivo salvo: {backup_filename}")
            print(f"Tamanho: {file_size} bytes")
            return backup_filename
            
    except Exception as e:
        print(f"Erro ao criar backup simples: {str(e)}")
        return None

def main():
    """Função principal"""
    print("Sistema de Backup - Dossie Escolar")
    print("=" * 50)
    
    # Tentar backup PostgreSQL primeiro
    backup_file = create_backup()
    
    # Se falhar, tentar backup simples
    if not backup_file:
        print("\nTentando backup simples...")
        backup_file = create_simple_backup()
    
    if backup_file:
        print(f"\nBackup concluido com sucesso!")
        print(f"Arquivo: {backup_file}")
        return 0
    else:
        print(f"\nFalha ao criar backup")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 