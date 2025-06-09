#!/usr/bin/env python3
# test_postgresql.py - Teste de conexão PostgreSQL

import os
from sqlalchemy import create_engine, text

def test_connection():
    """Testa conexão com PostgreSQL"""
    print("🧪 TESTANDO CONEXÃO POSTGRESQL")
    print("=" * 40)
    
    # Suas credenciais
    database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
    
    try:
        print(f"🔗 Tentando conectar: dossie@localhost/dossie_escola")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Teste básico
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Conexão bem-sucedida!")
            print(f"📊 Versão PostgreSQL: {version}")
            
            # Verificar se banco existe
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"📁 Banco atual: {db_name}")
            
            # Listar tabelas existentes
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"📋 Tabelas encontradas ({len(tables)}):")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("📋 Nenhuma tabela encontrada (banco vazio)")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n📋 VERIFICAÇÕES:")
        print("1. PostgreSQL está rodando?")
        print("2. Banco 'dossie_escola' existe?")
        print("3. Usuário 'dossie' existe?")
        print("4. Senha 'fep09151' está correta?")
        print("5. Permissões estão configuradas?")
        
        print("\n🔧 COMANDOS PARA CONFIGURAR:")
        print("-- Conecte como postgres:")
        print("psql -U postgres")
        print("")
        print("-- Crie o banco:")
        print("CREATE DATABASE dossie_escola;")
        print("")
        print("-- Crie o usuário:")
        print("CREATE USER dossie WITH PASSWORD 'fep09151';")
        print("")
        print("-- Dê permissões:")
        print("GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;")
        print("GRANT ALL ON SCHEMA public TO dossie;")
        print("")
        print("-- Saia:")
        print("\\q")
        
        return False

def test_with_app():
    """Testa conexão usando a aplicação"""
    print("\n🚀 TESTANDO COM A APLICAÇÃO")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db
            
            # Tentar conectar
            db.engine.execute(text("SELECT 1"))
            print("✅ Aplicação conectou com sucesso!")
            
            # Verificar se tabelas existem
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"📋 Tabelas da aplicação ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("📋 Tabelas da aplicação não criadas ainda")
                print("💡 Execute: python migrate_to_postgresql.py")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na aplicação: {e}")
        return False

if __name__ == '__main__':
    # Teste direto
    connection_ok = test_connection()
    
    if connection_ok:
        # Teste com aplicação
        test_with_app()
        
        print("\n🎉 POSTGRESQL CONFIGURADO!")
        print("📋 Próximos passos:")
        print("1. python migrate_to_postgresql.py  # Migrar dados")
        print("2. python app.py                    # Iniciar aplicação")
    else:
        print("\n⚠️  Configure o PostgreSQL primeiro")
