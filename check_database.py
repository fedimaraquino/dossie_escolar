#!/usr/bin/env python3
# check_database.py - Verificar status do banco de dados

import os
import psycopg2
from sqlalchemy import create_engine

def check_postgresql_service():
    """Verifica se o serviço PostgreSQL está rodando"""
    try:
        import subprocess
        result = subprocess.run(['sc', 'query', 'postgresql-x64-14'], 
                              capture_output=True, text=True, shell=True)
        if 'RUNNING' in result.stdout:
            return True, "Serviço rodando"
        else:
            return False, "Serviço parado"
    except:
        return False, "Não foi possível verificar o serviço"

def check_postgresql_connection():
    """Verifica conexão direta com PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dossie_escola",
            user="dossie",
            password="fep09151",
            port="5432"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database();")
        database = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Conectado ao banco '{database}'"
        
    except psycopg2.OperationalError as e:
        return False, f"Erro de conexão: {e}"
    except Exception as e:
        return False, f"Erro: {e}"

def check_database_exists():
    """Verifica se o banco existe"""
    try:
        # Conectar ao postgres para verificar se dossie_escola existe
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="dossie",
            password="fep09151",
            port="5432"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'dossie_escola';")
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return exists, "Banco existe" if exists else "Banco não existe"
        
    except Exception as e:
        return False, f"Erro ao verificar: {e}"

def check_user_permissions():
    """Verifica permissões do usuário"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dossie_escola",
            user="dossie",
            password="fep09151",
            port="5432"
        )
        
        cursor = conn.cursor()
        
        # Verificar se pode criar tabela
        cursor.execute("CREATE TABLE IF NOT EXISTS test_permissions (id INTEGER);")
        cursor.execute("DROP TABLE IF EXISTS test_permissions;")
        
        cursor.close()
        conn.close()
        
        return True, "Usuário tem permissões adequadas"
        
    except Exception as e:
        return False, f"Erro de permissão: {e}"

def main():
    print("🔍 DIAGNÓSTICO DO POSTGRESQL")
    print("=" * 40)
    
    print("\n1. Verificando serviço PostgreSQL...")
    service_ok, service_msg = check_postgresql_service()
    print(f"   {'✅' if service_ok else '❌'} {service_msg}")
    
    print("\n2. Verificando se banco existe...")
    db_exists, db_msg = check_database_exists()
    print(f"   {'✅' if db_exists else '❌'} {db_msg}")
    
    print("\n3. Testando conexão...")
    conn_ok, conn_msg = check_postgresql_connection()
    print(f"   {'✅' if conn_ok else '❌'} {conn_msg}")
    
    if conn_ok:
        print("\n4. Verificando permissões...")
        perm_ok, perm_msg = check_user_permissions()
        print(f"   {'✅' if perm_ok else '❌'} {perm_msg}")
    
    print("\n" + "=" * 40)
    
    if conn_ok:
        print("🎉 POSTGRESQL ESTÁ FUNCIONANDO!")
        print("\n📋 Próximos passos:")
        print("1. python setup_tables.py  # Criar tabelas")
        print("2. python app.py           # Iniciar sistema")
        
        # Tentar criar tabelas automaticamente
        print("\n🔧 Tentando criar tabelas automaticamente...")
        try:
            from app import create_app
            app = create_app()
            app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dossie:fep09151@localhost/dossie_escola'
            
            with app.app_context():
                from models import db
                db.create_all()
                print("✅ Tabelas criadas com sucesso!")
                
                # Verificar tabelas
                with db.engine.connect() as conn:
                    result = conn.execute(db.text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result]
                
                print(f"📋 Tabelas criadas ({len(tables)}):")
                for table in tables:
                    print(f"   ✓ {table}")
                    
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
    
    else:
        print("❌ POSTGRESQL NÃO ESTÁ FUNCIONANDO")
        print("\n📋 Possíveis soluções:")
        
        if not service_ok:
            print("• Iniciar serviço PostgreSQL")
            print("  - Windows: services.msc → PostgreSQL")
            print("  - Ou: net start postgresql-x64-14")
        
        if not db_exists:
            print("• Criar banco de dados:")
            print("  psql -U postgres")
            print("  CREATE DATABASE dossie_escola;")
            print("  CREATE USER dossie WITH PASSWORD 'fep09151';")
            print("  GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;")
        
        print("\n💡 Alternativa: usar SQLite")
        print("  python app.py  # Sistema funciona com SQLite")

if __name__ == '__main__':
    main()
