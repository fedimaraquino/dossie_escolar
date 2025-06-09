#!/usr/bin/env python3
# check_permissions_tables.py - Verificar tabelas de permissões

def check_tables():
    """Verificar se as tabelas de permissões foram criadas"""
    print("🔍 VERIFICANDO TABELAS DE PERMISSÕES")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db
            
            # Verificar tabelas no banco
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
            
            print(f"📋 Tabelas no banco ({len(tables)}):")
            for table in tables:
                print(f"   ✓ {table}")
            
            # Verificar se tabelas de permissões existem
            required_tables = ['permissoes', 'perfil_permissoes']
            missing_tables = []
            
            for table in required_tables:
                if table in tables:
                    print(f"✅ {table} - OK")
                else:
                    print(f"❌ {table} - FALTANDO")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n⚠️  Tabelas faltando: {missing_tables}")
                print("💡 Criando tabelas manualmente...")
                create_tables_manually()
            else:
                print("\n✅ Todas as tabelas de permissões existem!")
                setup_permissions()
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_tables_manually():
    """Criar tabelas de permissões manualmente"""
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db
            
            print("🏗️  Criando tabelas...")
            db.create_all()
            print("✅ Tabelas criadas!")
            
            # Verificar novamente
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name IN ('permissoes', 'perfil_permissoes')
                    AND table_schema = 'public'
                """))
                tables = [row[0] for row in result]
            
            print(f"📊 Tabelas de permissões: {tables}")
            
            if len(tables) >= 2:
                setup_permissions()
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

def setup_permissions():
    """Configurar permissões básicas"""
    print("\n🔐 CONFIGURANDO PERMISSÕES BÁSICAS")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Permissao, PerfilPermissao, Perfil
            
            # Permissões básicas
            permissoes_basicas = [
                {'nome': 'admin_total', 'descricao': 'Administração total', 'modulo': 'admin', 'acao': 'total'},
                {'nome': 'dossie_criar', 'descricao': 'Criar dossiês', 'modulo': 'dossie', 'acao': 'criar'},
                {'nome': 'dossie_editar', 'descricao': 'Editar dossiês', 'modulo': 'dossie', 'acao': 'editar'},
                {'nome': 'dossie_visualizar', 'descricao': 'Visualizar dossiês', 'modulo': 'dossie', 'acao': 'visualizar'},
                {'nome': 'usuario_criar', 'descricao': 'Criar usuários', 'modulo': 'usuario', 'acao': 'criar'},
                {'nome': 'usuario_editar', 'descricao': 'Editar usuários', 'modulo': 'usuario', 'acao': 'editar'},
                {'nome': 'usuario_visualizar', 'descricao': 'Visualizar usuários', 'modulo': 'usuario', 'acao': 'visualizar'},
            ]
            
            # Criar permissões
            for perm_data in permissoes_basicas:
                existing = Permissao.query.filter_by(nome=perm_data['nome']).first()
                if not existing:
                    permissao = Permissao(**perm_data)
                    db.session.add(permissao)
                    print(f"✅ Criada: {perm_data['nome']}")
            
            db.session.commit()
            
            # Atribuir permissão total ao Admin Geral
            admin_perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
            if admin_perfil:
                admin_perm = Permissao.query.filter_by(nome='admin_total').first()
                if admin_perm:
                    existing_pp = PerfilPermissao.query.filter_by(
                        perfil_id=admin_perfil.id_perfil,
                        permissao_id=admin_perm.id
                    ).first()
                    
                    if not existing_pp:
                        pp = PerfilPermissao(
                            perfil_id=admin_perfil.id_perfil,
                            permissao_id=admin_perm.id
                        )
                        db.session.add(pp)
                        db.session.commit()
                        print("✅ Admin Geral configurado com permissão total")
            
            print("\n📊 Resumo:")
            print(f"   Permissões: {Permissao.query.count()}")
            print(f"   Perfil-Permissões: {PerfilPermissao.query.count()}")
            
    except Exception as e:
        print(f"❌ Erro ao configurar permissões: {e}")

if __name__ == '__main__':
    check_tables()
