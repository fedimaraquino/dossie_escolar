#!/usr/bin/env python3
# init_database.py - Inicializar banco de dados (PostgreSQL ou SQLite)

import os
from sqlalchemy import create_engine, text

def test_postgresql():
    """Testa se PostgreSQL está disponível"""
    try:
        database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, database_url
    except Exception as e:
        return False, str(e)

def init_database():
    """Inicializa banco de dados"""
    print("🗄️  INICIALIZANDO BANCO DE DADOS")
    print("=" * 40)
    
    # Testar PostgreSQL primeiro
    pg_available, pg_result = test_postgresql()
    
    if pg_available:
        print("✅ PostgreSQL disponível - usando PostgreSQL")
        database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        db_type = "PostgreSQL"
    else:
        print(f"⚠️  PostgreSQL indisponível: {pg_result}")
        print("🔄 Usando SQLite como fallback")
        database_url = 'sqlite:///dossie_escolar.db'
        db_type = "SQLite"
    
    try:
        # Usar a aplicação para criar tabelas
        from app import create_app
        
        app = create_app()
        # Forçar URL específica
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        with app.app_context():
            from models import db
            
            print(f"🏗️  Criando tabelas no {db_type}...")
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar tabelas criadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📋 Tabelas criadas ({len(tables)}):")
            for table in sorted(tables):
                print(f"   ✓ {table}")
            
            # Criar dados iniciais
            print("\n🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            print(f"\n🎉 {db_type.upper()} CONFIGURADO COM SUCESSO!")
            print(f"📊 Banco: {database_url.split('@')[-1] if '@' in database_url else database_url}")
            
            return True, db_type
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False, None

def create_initial_data(db):
    """Cria dados iniciais no banco"""
    from models import Perfil, Cidade, Escola, Usuario
    from datetime import datetime
    
    try:
        # Verificar se já existem dados
        if Perfil.query.first():
            print("   ℹ️  Dados iniciais já existem")
            return
        
        # Criar perfis padrão
        perfis = [
            Perfil(perfil='Administrador Geral', descricao='Acesso total ao sistema'),
            Perfil(perfil='Administrador da Escola', descricao='Administrador de uma escola específica'),
            Perfil(perfil='Operador', descricao='Operações básicas do sistema'),
            Perfil(perfil='Consulta', descricao='Apenas consulta de dados')
        ]
        for perfil in perfis:
            db.session.add(perfil)
        
        # Criar cidade padrão
        cidade = Cidade(
            nome='São Paulo',
            uf='SP',
            codigo_ibge='3550308'
        )
        db.session.add(cidade)
        
        # Commit perfis e cidade primeiro
        db.session.commit()
        
        # Criar escola padrão
        escola = Escola(
            nome='Escola Municipal Exemplo',
            endereco='Rua das Flores, 123',
            uf='SP',
            cnpj='12.345.678/0001-90',
            inep='12345678',
            email='escola@exemplo.gov.br',
            diretor='João Silva',
            situacao='ativa',
            id_cidade=cidade.id
        )
        db.session.add(escola)
        db.session.commit()
        
        # Criar usuário administrador
        perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
        
        admin = Usuario(
            nome='Administrador do Sistema',
            email='admin@sistema.com',
            cpf='000.000.000-00',
            telefone='(11) 99999-9999',
            perfil_id=perfil_admin.id,
            escola_id=escola.id,
            situacao='ativo',
            data_nascimento=datetime(1980, 1, 1).date()
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("   ✓ Perfis criados (4)")
        print("   ✓ Cidade padrão criada")
        print("   ✓ Escola padrão criada")
        print("   ✓ Usuário admin criado: admin@sistema.com / admin123")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        db.session.rollback()
        raise

def show_connection_info():
    """Mostra informações de conexão"""
    print("\n📋 INFORMAÇÕES DE CONEXÃO:")
    print("=" * 30)
    
    pg_available, _ = test_postgresql()
    
    if pg_available:
        print("🐘 PostgreSQL:")
        print("   Host: localhost:5432")
        print("   Banco: dossie_escola")
        print("   Usuário: dossie")
        print("   Senha: fep09151")
        print("   Status: ✅ Conectado")
    else:
        print("🐘 PostgreSQL:")
        print("   Status: ❌ Não disponível")
        print("   Configurar: python test_postgresql.py")
    
    print("\n💾 SQLite:")
    print("   Arquivo: dossie_escolar.db")
    print("   Status: ✅ Sempre disponível")

if __name__ == '__main__':
    print("🚀 INICIALIZAÇÃO DO SISTEMA DE DOSSIÊ")
    print("=" * 50)
    
    success, db_type = init_database()
    
    if success:
        show_connection_info()
        
        print("\n🎯 SISTEMA PRONTO!")
        print("📋 Próximos passos:")
        print("1. python app.py                 # Iniciar aplicação")
        print("2. http://localhost:5000         # Acessar sistema")
        print("3. Login: admin@sistema.com / admin123")
        
        if db_type == "SQLite":
            print("\n💡 Para usar PostgreSQL:")
            print("1. Configure PostgreSQL conforme CONFIGURAR_POSTGRESQL.md")
            print("2. Execute: python init_database.py")
    else:
        print("\n❌ Falha na inicialização")
        print("📋 Verifique os logs de erro acima")
