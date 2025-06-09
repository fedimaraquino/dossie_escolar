#!/usr/bin/env python3
# backup_database.py - Script de backup do banco de dados

import os
import sys
from datetime import datetime
import subprocess

def find_pg_dump():
    """Encontrar pg_dump no Windows"""
    possible_paths = [
        'pg_dump',
        r'C:\Program Files\PostgreSQL\14\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe',
        r'C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe',
        r'C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe',
        r'C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe',
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ pg_dump encontrado: {path}")
                return path
        except FileNotFoundError:
            continue
    
    return None

def backup_postgresql_native():
    """Backup PostgreSQL usando pg_dump"""
    print("🔄 Tentando backup nativo PostgreSQL...")
    
    pg_dump = find_pg_dump()
    if not pg_dump:
        print("❌ pg_dump não encontrado")
        return False
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_postgresql_{timestamp}.sql"
        
        # URL de conexão
        db_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        
        # Executar pg_dump
        print(f"📝 Criando backup: {backup_file}")
        result = subprocess.run([
            pg_dump,
            '--host=localhost',
            '--port=5432',
            '--username=dossie',
            '--dbname=dossie_escola',
            '--file=' + backup_file,
            '--verbose',
            '--no-password'
        ], capture_output=True, text=True, env={**os.environ, 'PGPASSWORD': 'fep09151'})
        
        if result.returncode == 0:
            size = os.path.getsize(backup_file) / 1024 / 1024
            print(f"✅ Backup criado: {backup_file} ({size:.2f} MB)")
            return True
        else:
            print(f"❌ Erro no pg_dump: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def backup_postgresql_python():
    """Backup PostgreSQL usando Python"""
    print("🔄 Criando backup usando Python...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario, Escola, Dossie, Anexo, Perfil, Cidade, Movimentacao, Permissao, PerfilPermissao
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_python_{timestamp}.sql"
            
            print(f"📝 Criando backup: {backup_file}")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- Backup PostgreSQL gerado pelo Python\n")
                f.write(f"-- Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-- Sistema de Dossiê Escolar\n\n")
                
                # Backup de cada tabela
                tables = [
                    ('perfil', Perfil),
                    ('cidades', Cidade), 
                    ('escolas', Escola),
                    ('usuarios', Usuario),
                    ('permissoes', Permissao),
                    ('perfil_permissoes', PerfilPermissao),
                    ('dossies', Dossie),
                    ('anexo', Anexo),
                    ('movimentacoes', Movimentacao),
                ]
                
                total_records = 0
                
                for table_name, Model in tables:
                    try:
                        records = Model.query.all()
                        count = len(records)
                        total_records += count
                        
                        f.write(f"-- Tabela: {table_name} ({count} registros)\n")
                        
                        if records:
                            for record in records:
                                # Usar to_dict se disponível
                                if hasattr(record, 'to_dict'):
                                    data = record.to_dict()
                                else:
                                    # Fallback: pegar atributos do objeto
                                    data = {}
                                    for column in Model.__table__.columns:
                                        value = getattr(record, column.name, None)
                                        data[column.name] = value
                                
                                if data:
                                    columns = ', '.join(data.keys())
                                    values = []
                                    for v in data.values():
                                        if v is None:
                                            values.append('NULL')
                                        elif isinstance(v, str):
                                            # Escapar aspas simples
                                            escaped = v.replace("'", "''")
                                            values.append(f"'{escaped}'")
                                        elif isinstance(v, (int, float)):
                                            values.append(str(v))
                                        elif hasattr(v, 'strftime'):  # datetime
                                            values.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                                        else:
                                            values.append(f"'{str(v)}'")
                                    
                                    values_str = ', '.join(values)
                                    f.write(f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});\n")
                        
                        f.write(f"\n")
                        print(f"   ✓ {table_name}: {count} registros")
                        
                    except Exception as e:
                        f.write(f"-- Erro ao fazer backup da tabela {table_name}: {e}\n\n")
                        print(f"   ❌ {table_name}: Erro - {e}")
                
                f.write(f"-- Backup concluído: {total_records} registros totais\n")
            
            size = os.path.getsize(backup_file) / 1024
            print(f"✅ Backup Python criado: {backup_file} ({size:.2f} KB)")
            print(f"📊 Total de registros: {total_records}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro no backup Python: {e}")
        return False

def backup_sqlite():
    """Backup SQLite"""
    print("🔄 Criando backup SQLite...")
    
    try:
        import shutil
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_sqlite_{timestamp}.db"
        
        # Procurar arquivo SQLite
        sqlite_files = [
            'dossie_escolar.db',
            'instance/dossie_escolar.db',
            'app.db'
        ]
        
        source_file = None
        for file in sqlite_files:
            if os.path.exists(file):
                source_file = file
                break
        
        if not source_file:
            print("❌ Arquivo SQLite não encontrado")
            return False
        
        shutil.copy2(source_file, backup_file)
        
        size = os.path.getsize(backup_file) / 1024
        print(f"✅ Backup SQLite criado: {backup_file} ({size:.2f} KB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no backup SQLite: {e}")
        return False

def main():
    print("💾 SISTEMA DE BACKUP - DOSSIÊ ESCOLAR")
    print("=" * 50)
    
    # Detectar tipo de banco
    try:
        from app import create_app
        app = create_app()
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        if 'postgresql' in db_url:
            print("🐘 Banco detectado: PostgreSQL")
            
            # Tentar backup nativo primeiro
            if not backup_postgresql_native():
                print("\n🔄 Tentando método alternativo...")
                backup_postgresql_python()
                
        elif 'sqlite' in db_url:
            print("💾 Banco detectado: SQLite")
            backup_sqlite()
        else:
            print("❓ Tipo de banco não identificado")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    print("\n📋 Backups disponíveis:")
    backup_files = [f for f in os.listdir('.') if f.startswith('backup_')]
    for i, file in enumerate(backup_files, 1):
        size = os.path.getsize(file) / 1024
        modified = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"   {i}. {file} ({size:.2f} KB) - {modified.strftime('%d/%m/%Y %H:%M')}")

if __name__ == '__main__':
    main()
