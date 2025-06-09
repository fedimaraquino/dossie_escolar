#!/usr/bin/env python3
# create_tables_postgresql.py - Criar tabelas no PostgreSQL

import os
from sqlalchemy import create_engine, text

def create_tables():
    """Cria todas as tabelas no PostgreSQL"""
    print("🔧 CRIANDO TABELAS NO POSTGRESQL")
    print("=" * 40)
    
    # Suas credenciais
    database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
    
    try:
        print(f"🔗 Conectando ao PostgreSQL...")
        
        # Testar conexão primeiro
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Conectado ao banco: {db_name}")
        
        # Usar a aplicação para criar tabelas
        from app import create_app
        
        # Forçar uso do PostgreSQL
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
        with app.app_context():
            from models import db
            
            print("🏗️  Criando todas as tabelas...")
            
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
            
            # Criar dados iniciais se não existirem
            print("\n🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        print("\n📋 VERIFICAÇÕES:")
        print("1. PostgreSQL está rodando?")
        print("2. Banco 'dossie_escola' existe?")
        print("3. Usuário 'dossie' tem permissões?")
        print("4. Execute: python test_postgresql.py")
        return False

def create_initial_data(db):
    """Cria dados iniciais no banco"""
    from models import Perfil, Cidade, Escola, Usuario
    from datetime import datetime
    
    try:
        # Criar perfis padrão
        if not Perfil.query.first():
            perfis = [
                Perfil(perfil='Administrador Geral', descricao='Acesso total ao sistema'),
                Perfil(perfil='Administrador da Escola', descricao='Administrador de uma escola específica'),
                Perfil(perfil='Operador', descricao='Operações básicas do sistema'),
                Perfil(perfil='Consulta', descricao='Apenas consulta de dados')
            ]
            for perfil in perfis:
                db.session.add(perfil)
            db.session.commit()
            print("   ✓ Perfis criados")
        else:
            print("   ℹ️  Perfis já existem")
        
        # Criar cidade padrão
        if not Cidade.query.first():
            cidade = Cidade(
                nome='São Paulo',
                uf='SP',
                codigo_ibge='3550308'
            )
            db.session.add(cidade)
            db.session.commit()
            print("   ✓ Cidade padrão criada")
        else:
            print("   ℹ️  Cidade já existe")
        
        # Criar escola padrão
        if not Escola.query.first():
            cidade_padrao = Cidade.query.first()
            escola = Escola(
                nome='Escola Municipal Exemplo',
                endereco='Rua das Flores, 123',
                uf='SP',
                cnpj='12.345.678/0001-90',
                inep='12345678',
                email='escola@exemplo.gov.br',
                diretor='João Silva',
                situacao='ativa',
                id_cidade=cidade_padrao.id if cidade_padrao else None
            )
            db.session.add(escola)
            db.session.commit()
            print("   ✓ Escola padrão criada")
        else:
            print("   ℹ️  Escola já existe")
        
        # Criar usuário administrador
        if not Usuario.query.filter_by(email='admin@sistema.com').first():
            perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
            escola_padrao = Escola.query.first()
            
            admin = Usuario(
                nome='Administrador do Sistema',
                email='admin@sistema.com',
                cpf='000.000.000-00',
                telefone='(11) 99999-9999',
                perfil_id=perfil_admin.id,
                escola_id=escola_padrao.id,
                situacao='ativo',
                data_nascimento=datetime(1980, 1, 1).date()
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("   ✓ Usuário admin criado: admin@sistema.com / admin123")
        else:
            print("   ℹ️  Usuário admin já existe")
            
        print("✅ Dados iniciais configurados!")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        db.session.rollback()

def verify_tables():
    """Verifica se as tabelas foram criadas corretamente"""
    print("\n🔍 VERIFICANDO ESTRUTURA DAS TABELAS")
    print("=" * 40)
    
    database_url = 'postgresql://dossie:fep09151@localhost/dossie_escola'
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar cada tabela esperada
            expected_tables = [
                'perfis', 'cidades', 'escolas', 'usuarios', 
                'dossies', 'anexo', 'movimentacoes'
            ]
            
            for table in expected_tables:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{table}' 
                    AND table_schema = 'public'
                """))
                
                exists = result.fetchone()[0] > 0
                status = "✅" if exists else "❌"
                print(f"   {status} {table}")
                
                if exists:
                    # Contar registros
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"      📊 {count} registro(s)")
            
            print("\n🎯 Verificação concluída!")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == '__main__':
    print("🐘 CONFIGURAÇÃO DE TABELAS POSTGRESQL")
    print("=" * 50)
    
    # Criar tabelas
    if create_tables():
        # Verificar estrutura
        verify_tables()
        
        print("\n🎉 POSTGRESQL CONFIGURADO COM SUCESSO!")
        print("📋 Próximos passos:")
        print("1. python test_postgresql.py     # Testar conexão")
        print("2. python app.py                 # Iniciar aplicação")
        print("3. http://localhost:5000         # Acessar sistema")
        print("4. Login: admin@sistema.com / admin123")
    else:
        print("\n⚠️  Corrija os problemas e execute novamente")
