#!/usr/bin/env python3
# check_users.py - Verificar usuários no banco

def check_users():
    """Verificar usuários cadastrados"""
    print("👤 VERIFICANDO USUÁRIOS NO BANCO")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario, Perfil, Escola
            
            # Listar todos os usuários
            usuarios = Usuario.query.all()
            
            print(f"📊 Total de usuários: {len(usuarios)}")
            print()
            
            if usuarios:
                for usuario in usuarios:
                    print(f"👤 ID: {usuario.id}")
                    print(f"   Nome: {usuario.nome}")
                    print(f"   Email: {usuario.email}")
                    print(f"   CPF: {usuario.cpf}")
                    print(f"   Situação: {usuario.situacao}")
                    print(f"   Perfil ID: {usuario.perfil_id}")
                    print(f"   Escola ID: {usuario.escola_id}")
                    
                    # Verificar perfil
                    if usuario.perfil_id:
                        perfil = Perfil.query.get(usuario.perfil_id)
                        print(f"   Perfil: {perfil.perfil if perfil else 'Não encontrado'}")
                    
                    # Verificar escola
                    if usuario.escola_id:
                        escola = Escola.query.get(usuario.escola_id)
                        print(f"   Escola: {escola.nome if escola else 'Não encontrada'}")
                    
                    # Testar senha
                    print(f"   Senha hash: {usuario.senha_hash[:20]}..." if usuario.senha_hash else "   Sem senha!")
                    
                    print("-" * 30)
            else:
                print("❌ Nenhum usuário encontrado!")
                print("\n💡 Criando usuário admin...")
                create_admin_user()
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def create_admin_user():
    """Criar usuário administrador"""
    try:
        from app import create_app
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario, Perfil, Escola, Cidade
            
            # Verificar se já existe
            admin_existente = Usuario.query.filter_by(email='admin@sistema.com').first()
            if admin_existente:
                print("ℹ️  Usuário admin já existe")
                return
            
            # Buscar ou criar perfil admin
            perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
            if not perfil_admin:
                print("📝 Criando perfil Administrador Geral...")
                perfil_admin = Perfil(
                    perfil='Administrador Geral',
                    descricao='Acesso total ao sistema'
                )
                db.session.add(perfil_admin)
                db.session.commit()
            
            # Buscar ou criar cidade
            cidade = Cidade.query.first()
            if not cidade:
                print("📝 Criando cidade padrão...")
                cidade = Cidade(nome='São Paulo', uf='SP', pais='Brasil')
                db.session.add(cidade)
                db.session.commit()
            
            # Buscar ou criar escola
            escola = Escola.query.first()
            if not escola:
                print("📝 Criando escola padrão...")
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
            
            # Criar usuário admin
            print("👤 Criando usuário administrador...")
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
            
            # Definir senha
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Usuário admin criado com sucesso!")
            print("📧 Email: admin@sistema.com")
            print("🔑 Senha: admin123")
            
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        db.session.rollback()

def test_login():
    """Testar login do usuário admin"""
    print("\n🔐 TESTANDO LOGIN")
    print("=" * 20)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import Usuario
            
            # Buscar usuário
            usuario = Usuario.query.filter_by(email='admin@sistema.com').first()
            
            if not usuario:
                print("❌ Usuário não encontrado!")
                return False
            
            # Testar senha
            if usuario.check_password('admin123'):
                print("✅ Login funcionando!")
                print(f"👤 Usuário: {usuario.nome}")
                print(f"📧 Email: {usuario.email}")
                print(f"🏷️  Perfil: {usuario.perfil_obj.perfil if usuario.perfil_obj else 'Sem perfil'}")
                return True
            else:
                print("❌ Senha incorreta!")
                
                # Resetar senha
                print("🔧 Resetando senha...")
                usuario.set_password('admin123')
                from models import db
                db.session.commit()
                
                # Testar novamente
                if usuario.check_password('admin123'):
                    print("✅ Senha resetada com sucesso!")
                    return True
                else:
                    print("❌ Falha ao resetar senha!")
                    return False
                
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False

if __name__ == '__main__':
    print("🔍 DIAGNÓSTICO DE USUÁRIOS")
    print("=" * 50)
    
    if check_users():
        test_login()
        
        print("\n📋 CREDENCIAIS PARA LOGIN:")
        print("Email: admin@sistema.com")
        print("Senha: admin123")
        print("URL: http://localhost:5000")
    else:
        print("\n❌ Falha na verificação")
