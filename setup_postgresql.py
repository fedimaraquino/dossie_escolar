#!/usr/bin/env python3
# setup_postgresql.py - Configuração automática do PostgreSQL

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def check_postgresql_installed():
    """Verifica se PostgreSQL está instalado"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ PostgreSQL não encontrado")
    return False

def install_postgresql_windows():
    """Instruções para instalar PostgreSQL no Windows"""
    print("\n📋 COMO INSTALAR POSTGRESQL NO WINDOWS:")
    print("=" * 50)
    print("\n🔗 Opção 1 - Download oficial:")
    print("   https://www.postgresql.org/download/windows/")
    print("\n🔗 Opção 2 - Winget (se disponível):")
    print("   winget install PostgreSQL.PostgreSQL")
    print("\n🔗 Opção 3 - Chocolatey (se disponível):")
    print("   choco install postgresql")
    print("\n📝 Durante a instalação:")
    print("   - Defina senha para usuário 'postgres'")
    print("   - Porta padrão: 5432")
    print("   - Locale: Portuguese, Brazil")

def test_connection(url):
    """Testa conexão com banco"""
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def create_database_and_user():
    """Cria banco e usuário para o sistema"""
    print("\n🔧 CONFIGURANDO BANCO DE DADOS...")
    
    # URLs de teste
    admin_urls = [
        'postgresql://postgres:postgres@localhost/postgres',
        'postgresql://postgres:admin@localhost/postgres',
        'postgresql://postgres:123456@localhost/postgres',
    ]
    
    # Tentar conectar como admin
    admin_engine = None
    for url in admin_urls:
        if test_connection(url):
            admin_engine = create_engine(url)
            print(f"✅ Conectado como admin: {url.split('@')[1]}")
            break
    
    if not admin_engine:
        print("❌ Não foi possível conectar como administrador")
        print("\n📋 CONFIGURAÇÃO MANUAL NECESSÁRIA:")
        print("1. Abra pgAdmin ou psql")
        print("2. Conecte como usuário 'postgres'")
        print("3. Execute os comandos:")
        print("   CREATE DATABASE dossie_escolar;")
        print("   CREATE USER dossie_user WITH PASSWORD 'dossie123';")
        print("   GRANT ALL PRIVILEGES ON DATABASE dossie_escolar TO dossie_user;")
        print("   \\q")
        return False
    
    try:
        with admin_engine.connect() as conn:
            # Verificar se banco já existe
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'dossie_escolar'"))
            if not result.fetchone():
                conn.execute(text("CREATE DATABASE dossie_escolar"))
                print("✅ Banco 'dossie_escolar' criado")
            else:
                print("ℹ️  Banco 'dossie_escolar' já existe")
            
            # Verificar se usuário já existe
            result = conn.execute(text("SELECT 1 FROM pg_user WHERE usename = 'dossie_user'"))
            if not result.fetchone():
                conn.execute(text("CREATE USER dossie_user WITH PASSWORD 'dossie123'"))
                print("✅ Usuário 'dossie_user' criado")
            else:
                print("ℹ️  Usuário 'dossie_user' já existe")
            
            # Dar permissões
            conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE dossie_escolar TO dossie_user"))
            conn.commit()
            print("✅ Permissões concedidas")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_application_connection():
    """Testa conexão da aplicação"""
    print("\n🧪 TESTANDO CONEXÃO DA APLICAÇÃO...")
    
    app_url = 'postgresql://dossie_user:dossie123@localhost/dossie_escolar'
    
    if test_connection(app_url):
        print("✅ Aplicação pode conectar ao PostgreSQL")
        return True
    else:
        print("❌ Aplicação não consegue conectar")
        return False

def create_env_file():
    """Cria arquivo .env com configurações"""
    env_content = """# Configurações do Sistema de Dossiê
DATABASE_URL=postgresql://dossie_user:dossie123@localhost/dossie_escolar
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado")

def main():
    print("🐘 CONFIGURAÇÃO POSTGRESQL PARA SISTEMA DE DOSSIÊ")
    print("=" * 60)
    
    # 1. Verificar se PostgreSQL está instalado
    if not check_postgresql_installed():
        install_postgresql_windows()
        print("\n⚠️  Instale o PostgreSQL e execute este script novamente")
        return False
    
    # 2. Criar banco e usuário
    if not create_database_and_user():
        return False
    
    # 3. Testar conexão da aplicação
    if not test_application_connection():
        return False
    
    # 4. Criar arquivo .env
    create_env_file()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 30)
    print("\n📊 Informações da conexão:")
    print("   Host: localhost")
    print("   Porta: 5432")
    print("   Banco: dossie_escolar")
    print("   Usuário: dossie_user")
    print("   Senha: dossie123")
    
    print("\n📋 Próximos passos:")
    print("1. Execute: python migrate_to_postgresql.py")
    print("2. Inicie a aplicação: python app.py")
    print("3. Acesse: http://localhost:5000")
    
    return True

if __name__ == '__main__':
    main()
