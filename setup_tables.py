#!/usr/bin/env python3
# setup_tables.py - Criar tabelas no PostgreSQL

def test_and_create_tables():
    """Testa conexão e cria tabelas no PostgreSQL"""
    print("🐘 CONFIGURANDO POSTGRESQL")
    print("=" * 30)
    
    # Suas credenciais
    database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
    
    try:
        print("🔗 Testando conexão PostgreSQL...")
        
        from app import create_app
        
        # Criar app com PostgreSQL
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        with app.app_context():
            from models import db
            
            # Testar conexão
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT current_database(), version()"))
                row = result.fetchone()
                print(f"✅ Conectado ao banco: {row[0]}")
                print(f"📊 Versão PostgreSQL: {row[1].split(',')[0]}")
            
            print("\n🏗️  Criando tabelas...")
            
            # Criar todas as tabelas
            db.create_all()
            
            print("✅ Tabelas criadas!")
            
            # Verificar tabelas
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
            
            print(f"\n📋 Tabelas no banco ({len(tables)}):")
            for table in tables:
                print(f"   ✓ {table}")
            
            # Criar dados iniciais
            print("\n🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            print("\n🎉 POSTGRESQL CONFIGURADO COM SUCESSO!")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\n📋 Verificações:")
        print("1. PostgreSQL está rodando?")
        print("2. Banco 'dossie_escola' existe?")
        print("3. Usuário 'dossie' tem permissões?")
        return False

def create_initial_data(db):
    """Cria dados iniciais"""
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
            perfil_id=1,  # Administrador Geral
            escola_id=escola.id,
            situacao='ativo',
            data_nascimento=datetime(1980, 1, 1).date()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("   ✓ 4 perfis criados")
        print("   ✓ Cidade padrão criada")
        print("   ✓ Escola padrão criada")
        print("   ✓ Admin criado: admin@sistema.com / admin123")
        
    except Exception as e:
        print(f"   ❌ Erro nos dados iniciais: {e}")
        db.session.rollback()

if __name__ == '__main__':
    if test_and_create_tables():
        print("\n📋 Próximos passos:")
        print("1. python app.py")
        print("2. http://localhost:5000")
        print("3. Login: admin@sistema.com / admin123")
    else:
        print("\n⚠️  Configure PostgreSQL primeiro")
