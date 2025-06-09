#!/usr/bin/env python3
# migrate_to_postgresql.py - Migração de SQLite para PostgreSQL

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import sqlite3

def test_postgresql_connection():
    """Testa conexão com PostgreSQL"""
    try:
        # Tentar diferentes URLs de conexão
        urls = [
            os.environ.get('DATABASE_URL'),
            'postgresql://dossie:fep09151@localhost/dossie_escola',
            'postgresql://postgres:postgres@localhost/dossie_escola',
        ]
        
        for url in urls:
            if url:
                try:
                    engine = create_engine(url)
                    with engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    print(f"✅ Conexão PostgreSQL OK: {url.split('@')[1] if '@' in url else url}")
                    return url
                except Exception as e:
                    print(f"❌ Falha na conexão: {url.split('@')[1] if '@' in url else url}")
                    continue
        
        return None
    except Exception as e:
        print(f"❌ Erro ao testar PostgreSQL: {e}")
        return None

def backup_sqlite_data():
    """Faz backup dos dados do SQLite"""
    sqlite_path = 'instance/dossie_escolar.db'
    
    if not os.path.exists(sqlite_path):
        print("❌ Banco SQLite não encontrado!")
        return None
    
    # Criar backup
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'sqlite_backup_{timestamp}.db')
    
    import shutil
    shutil.copy2(sqlite_path, backup_path)
    print(f"✅ Backup SQLite criado: {backup_path}")
    
    return sqlite_path

def export_sqlite_data(sqlite_path):
    """Exporta dados do SQLite"""
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        data = {}
        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue
                
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            data[table_name] = {
                'columns': columns,
                'rows': rows
            }
            print(f"📊 Exportados {len(rows)} registros da tabela '{table_name}'")
        
        conn.close()
        return data
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados SQLite: {e}")
        return None

def create_postgresql_tables(pg_url):
    """Cria tabelas no PostgreSQL"""
    try:
        # Importar modelos para criar tabelas
        from app import create_app
        from models import db
        
        # Configurar app para usar PostgreSQL
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
        
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas PostgreSQL criadas com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas PostgreSQL: {e}")
        return False

def import_data_to_postgresql(pg_url, data):
    """Importa dados para PostgreSQL"""
    try:
        from app import create_app
        from models import db
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
        
        with app.app_context():
            # Importar modelos
            from models import Escola, Usuario, Perfil, Cidade, Dossie, Anexo, Movimentacao
            
            model_map = {
                'escolas': Escola,
                'usuarios': Usuario,
                'perfis': Perfil,
                'cidades': Cidade,
                'dossies': Dossie,
                'anexo': Anexo,
                'movimentacoes': Movimentacao
            }
            
            # Ordem de importação (respeitando foreign keys)
            import_order = ['cidades', 'escolas', 'perfis', 'usuarios', 'dossies', 'anexo', 'movimentacoes']
            
            for table_name in import_order:
                if table_name in data and table_name in model_map:
                    model = model_map[table_name]
                    table_data = data[table_name]
                    
                    print(f"📥 Importando {table_name}...")
                    
                    for row in table_data['rows']:
                        # Criar dicionário com dados da linha
                        row_dict = dict(zip(table_data['columns'], row))
                        
                        # Criar instância do modelo
                        instance = model(**row_dict)
                        db.session.add(instance)
                    
                    try:
                        db.session.commit()
                        print(f"✅ {len(table_data['rows'])} registros importados para {table_name}")
                    except Exception as e:
                        db.session.rollback()
                        print(f"❌ Erro ao importar {table_name}: {e}")
            
            print("✅ Migração concluída!")
            return True
            
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    print("🔄 MIGRAÇÃO SQLITE → POSTGRESQL")
    print("=" * 50)
    
    # 1. Testar conexão PostgreSQL
    print("\n1. Testando conexão PostgreSQL...")
    pg_url = test_postgresql_connection()
    
    if not pg_url:
        print("\n❌ PostgreSQL não está disponível!")
        print("\n📋 INSTRUÇÕES:")
        print("1. Instale PostgreSQL: https://www.postgresql.org/download/")
        print("2. Crie o banco: CREATE DATABASE dossie_escolar;")
        print("3. Crie usuário: CREATE USER dossie_user WITH PASSWORD 'dossie123';")
        print("4. Dê permissões: GRANT ALL PRIVILEGES ON DATABASE dossie_escolar TO dossie_user;")
        print("5. Execute novamente este script")
        return False
    
    # 2. Backup SQLite
    print("\n2. Fazendo backup dos dados SQLite...")
    sqlite_path = backup_sqlite_data()
    
    if not sqlite_path:
        print("❌ Não há dados para migrar")
        return False
    
    # 3. Exportar dados SQLite
    print("\n3. Exportando dados do SQLite...")
    data = export_sqlite_data(sqlite_path)
    
    if not data:
        print("❌ Falha na exportação")
        return False
    
    # 4. Criar tabelas PostgreSQL
    print("\n4. Criando tabelas no PostgreSQL...")
    if not create_postgresql_tables(pg_url):
        return False
    
    # 5. Importar dados
    print("\n5. Importando dados para PostgreSQL...")
    if not import_data_to_postgresql(pg_url, data):
        return False
    
    print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"📊 Banco PostgreSQL configurado: {pg_url.split('@')[1] if '@' in pg_url else pg_url}")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Atualize a variável DATABASE_URL se necessário")
    print("2. Reinicie a aplicação")
    print("3. Teste todas as funcionalidades")
    
    return True

if __name__ == '__main__':
    main()
