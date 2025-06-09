#!/usr/bin/env python3
# force_postgresql.py - Forçar uso do PostgreSQL

import os
import locale

def setup_environment():
    """Configurar ambiente para PostgreSQL"""
    # Configurar encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    
    # Configurar locale
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except:
            pass

def test_and_create():
    """Testar e criar estrutura"""
    setup_environment()
    
    print("🐘 FORÇANDO POSTGRESQL")
    print("=" * 30)
    
    try:
        from app import create_app
        
        # Forçar PostgreSQL
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        
        with app.app_context():
            from models import db
            
            print("🔗 Testando conexão...")
            
            # Teste simples
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✅ Conexão OK!")
            
            print("🏗️  Criando tabelas...")
            db.create_all()
            print("✅ Tabelas criadas!")
            
            # Verificar tabelas
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
            
            print(f"📋 Tabelas ({len(tables)}):")
            for table in tables:
                print(f"   ✓ {table}")
            
            # Criar dados iniciais
            print("🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            print("\n🎉 POSTGRESQL CONFIGURADO!")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n📋 VERIFIQUE NO PGADMIN4:")
        print("1. Banco 'dossie_escola' existe?")
        print("2. Usuário 'dossie' existe?")
        print("3. Permissões estão OK?")
        return False

def create_initial_data(db):
    """Criar dados iniciais"""
    from models import Perfil, Cidade, Escola, Usuario
    from datetime import datetime
    
    try:
        # Verificar se já existem dados
        if Perfil.query.first():
            print("   ℹ️  Dados já existem")
            return
        
        # Perfis
        perfis = [
            Perfil(perfil='Administrador Geral', descricao='Acesso total'),
            Perfil(perfil='Administrador da Escola', descricao='Admin da escola'),
            Perfil(perfil='Operador', descricao='Operações básicas'),
            Perfil(perfil='Consulta', descricao='Apenas consulta')
        ]
        for perfil in perfis:
            db.session.add(perfil)
        db.session.commit()
        
        # Cidade
        cidade = Cidade(nome='São Paulo', uf='SP', codigo_ibge='3550308')
        db.session.add(cidade)
        db.session.commit()
        
        # Escola
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
        
        # Admin
        admin = Usuario(
            nome='Administrador',
            email='admin@sistema.com',
            cpf='000.000.000-00',
            telefone='(11) 99999-9999',
            perfil_id=1,
            escola_id=escola.id,
            situacao='ativo',
            data_nascimento=datetime(1980, 1, 1).date()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("   ✓ Dados iniciais criados")
        print("   ✓ Login: admin@sistema.com / admin123")
        
    except Exception as e:
        print(f"   ❌ Erro nos dados: {e}")
        db.session.rollback()

if __name__ == '__main__':
    if test_and_create():
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. python app.py")
        print("2. http://localhost:5000")
        print("3. Login: admin@sistema.com / admin123")
    else:
        print("\n⚠️  Configure no pgAdmin4 primeiro")
