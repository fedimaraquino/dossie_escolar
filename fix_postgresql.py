#!/usr/bin/env python3
# fix_postgresql.py - Corrigir estrutura PostgreSQL

def fix_database():
    """Corrigir estrutura do banco"""
    print("🔧 CORRIGINDO ESTRUTURA POSTGRESQL")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        
        with app.app_context():
            from models import db
            
            print("🗑️  Removendo tabelas manualmente...")
            
            # Remover tabelas na ordem correta (respeitando foreign keys)
            tables_to_drop = [
                'anexo',
                'movimentacoes', 
                'dossies',
                'usuarios',
                'escolas',
                'cidades',
                'perfil'
            ]
            
            with db.engine.connect() as conn:
                # Desabilitar verificação de foreign keys temporariamente
                conn.execute(db.text("SET session_replication_role = replica;"))
                
                for table in tables_to_drop:
                    try:
                        conn.execute(db.text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                        print(f"   ✓ {table} removida")
                    except Exception as e:
                        print(f"   ⚠️  {table}: {e}")
                
                # Reabilitar verificação de foreign keys
                conn.execute(db.text("SET session_replication_role = DEFAULT;"))
                conn.commit()
            
            print("✅ Tabelas removidas")
            
            print("🏗️  Criando tabelas novas...")
            db.create_all()
            print("✅ Tabelas criadas")
            
            # Verificar estrutura
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
            
            # Verificar estrutura da tabela perfil
            print("\n🔍 Verificando estrutura da tabela 'perfil':")
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'perfil' 
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                
                for col in columns:
                    print(f"   • {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Criar dados iniciais
            print("\n🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            print("\n🎉 POSTGRESQL CORRIGIDO!")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_initial_data(db):
    """Criar dados iniciais"""
    from models import Perfil, Cidade, Escola, Usuario
    from datetime import datetime
    
    try:
        # Perfis
        perfis_data = [
            {'perfil': 'Administrador Geral', 'descricao': 'Acesso total ao sistema'},
            {'perfil': 'Administrador da Escola', 'descricao': 'Administrador de uma escola específica'},
            {'perfil': 'Operador', 'descricao': 'Operações básicas do sistema'},
            {'perfil': 'Consulta', 'descricao': 'Apenas consulta de dados'}
        ]
        
        for perfil_data in perfis_data:
            perfil = Perfil(**perfil_data)
            db.session.add(perfil)
        
        db.session.commit()
        print("   ✓ 4 perfis criados")
        
        # Cidade
        cidade = Cidade(
            nome='São Paulo',
            uf='SP',
            pais='Brasil'
        )
        db.session.add(cidade)
        db.session.commit()
        print("   ✓ Cidade padrão criada")
        
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
        print("   ✓ Escola padrão criada")
        
        # Admin
        perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
        
        admin = Usuario(
            nome='Administrador do Sistema',
            email='admin@sistema.com',
            cpf='000.000.000-00',
            telefone='(11) 99999-9999',
            perfil_id=perfil_admin.id_perfil,
            escola_id=escola.id,
            situacao='ativo',
            data_nascimento=datetime(1980, 1, 1).date()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("   ✓ Usuário admin criado")
        
        print("\n🔑 CREDENCIAIS:")
        print("   Email: admin@sistema.com")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    if fix_database():
        print("\n📋 SISTEMA PRONTO!")
        print("1. python app.py")
        print("2. http://localhost:5000")
        print("3. Login: admin@sistema.com / admin123")
    else:
        print("\n❌ Falha na correção")
