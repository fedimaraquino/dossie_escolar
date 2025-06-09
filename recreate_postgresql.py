#!/usr/bin/env python3
# recreate_postgresql.py - Recriar tabelas no PostgreSQL

import os

def recreate_tables():
    """Recriar tabelas com estrutura corrigida"""
    print("🔄 RECRIANDO TABELAS POSTGRESQL")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dossie:fep09151@localhost/dossie_escola'
        
        with app.app_context():
            from models import db
            
            print("🗑️  Removendo tabelas antigas...")
            db.drop_all()
            print("✅ Tabelas removidas")
            
            print("🏗️  Criando tabelas novas...")
            db.create_all()
            print("✅ Tabelas criadas")
            
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
            
            # Criar dados iniciais
            print("\n🌱 Criando dados iniciais...")
            create_initial_data(db)
            
            print("\n🎉 POSTGRESQL RECONFIGURADO!")
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_initial_data(db):
    """Criar dados iniciais com estrutura corrigida"""
    from models import Perfil, Cidade, Escola, Usuario
    from datetime import datetime
    
    try:
        # Perfis com descrição
        perfis = [
            Perfil(perfil='Administrador Geral', descricao='Acesso total ao sistema'),
            Perfil(perfil='Administrador da Escola', descricao='Administrador de uma escola específica'),
            Perfil(perfil='Operador', descricao='Operações básicas do sistema'),
            Perfil(perfil='Consulta', descricao='Apenas consulta de dados')
        ]
        for perfil in perfis:
            db.session.add(perfil)
        db.session.commit()
        print("   ✓ 4 perfis criados")
        
        # Cidade
        cidade = Cidade(
            nome='São Paulo',
            uf='SP',
            codigo_ibge='3550308'
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
        
        # Usuário administrador
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
        
        # Criar dossiê de exemplo
        from models import Dossie
        dossie_exemplo = Dossie(
            n_dossie='2024001',
            nome='JOÃO DA SILVA SANTOS',
            ano=2024,
            id_escola=escola.id,
            status='ativo',
            cpf='123.456.789-00',
            n_mae='MARIA DA SILVA',
            n_pai='JOSÉ SANTOS',
            local='Arquivo Central',
            pasta='P001',
            tipo_documento='Histórico Escolar',
            observacao='Dossiê de exemplo criado automaticamente'
        )
        db.session.add(dossie_exemplo)
        db.session.commit()
        print("   ✓ Dossiê de exemplo criado")
        
        print("\n📊 DADOS CRIADOS:")
        print(f"   • Perfis: {Perfil.query.count()}")
        print(f"   • Cidades: {Cidade.query.count()}")
        print(f"   • Escolas: {Escola.query.count()}")
        print(f"   • Usuários: {Usuario.query.count()}")
        print(f"   • Dossiês: {Dossie.query.count()}")
        
        print("\n🔑 LOGIN:")
        print("   Email: admin@sistema.com")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    if recreate_tables():
        print("\n📋 SISTEMA PRONTO!")
        print("1. python app.py")
        print("2. http://localhost:5000")
        print("3. Login: admin@sistema.com / admin123")
    else:
        print("\n❌ Falha na reconfiguração")
