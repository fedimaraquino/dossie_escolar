#!/usr/bin/env python3
# test_connection_simple.py - Teste simples de conexão PostgreSQL

import psycopg2
import os

def test_connection():
    """Teste simples de conexão"""
    print("🔗 TESTANDO CONEXÃO POSTGRESQL")
    print("=" * 40)
    
    try:
        # Configurar encoding
        os.environ['PGCLIENTENCODING'] = 'UTF8'
        
        # Conectar
        conn = psycopg2.connect(
            host="localhost",
            database="dossie_escola",
            user="dossie",
            password="fep09151",
            port="5432",
            client_encoding='UTF8'
        )
        
        cursor = conn.cursor()
        
        # Teste básico
        cursor.execute("SELECT current_database(), version()")
        result = cursor.fetchone()
        
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Banco: {result[0]}")
        print(f"📊 Versão: {result[1].split(',')[0]}")
        
        # Verificar encoding
        cursor.execute("SHOW client_encoding")
        encoding = cursor.fetchone()[0]
        print(f"📊 Encoding: {encoding}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Erro de conexão: {error_msg}")
        
        if "database" in error_msg and "does not exist" in error_msg:
            print("\n💡 SOLUÇÃO: Criar banco no pgAdmin4")
            print("1. Clique direito em 'Databases' → 'Create' → 'Database'")
            print("2. Nome: dossie_escola")
            print("3. Encoding: UTF8")
        
        elif "role" in error_msg and "does not exist" in error_msg:
            print("\n💡 SOLUÇÃO: Criar usuário no pgAdmin4")
            print("1. Clique direito em 'Login/Group Roles' → 'Create' → 'Login/Group Role'")
            print("2. Nome: dossie")
            print("3. Senha: fep09151")
        
        elif "authentication failed" in error_msg:
            print("\n💡 SOLUÇÃO: Verificar senha")
            print("Senha configurada: fep09151")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_tables_if_connected():
    """Cria tabelas se conexão estiver OK"""
    print("\n🏗️  CRIANDO TABELAS...")
    
    try:
        from app import create_app
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        
        with app.app_context():
            from models import db
            
            # Criar tabelas
            db.create_all()
            print("✅ Tabelas criadas!")
            
            # Listar tabelas
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Tabelas criadas ({len(tables)}):")
                for table in tables:
                    print(f"   ✓ {table}")
            else:
                print("⚠️  Nenhuma tabela encontrada")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == '__main__':
    if test_connection():
        print("\n🎉 POSTGRESQL FUNCIONANDO!")
        
        # Tentar criar tabelas
        if create_tables_if_connected():
            print("\n📋 SISTEMA PRONTO!")
            print("1. python app.py")
            print("2. http://localhost:5000")
        else:
            print("\n⚠️  Execute: python setup_tables.py")
    else:
        print("\n❌ Configure PostgreSQL no pgAdmin4 primeiro")
        print("\n📋 CHECKLIST:")
        print("□ Banco 'dossie_escola' criado")
        print("□ Usuário 'dossie' criado")
        print("□ Senha 'fep09151' configurada")
        print("□ Permissões concedidas")
