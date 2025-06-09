#!/usr/bin/env python3
# create_test_user.py - Criar usuário de teste

def create_test_users():
    """Criar usuários de teste"""
    print("👤 CRIANDO USUÁRIOS DE TESTE")
    print("=" * 40)
    
    try:
        from app import create_app
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario, Perfil, Escola
            
            # Buscar perfil e escola
            perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
            escola = Escola.query.first()
            
            if not perfil_admin or not escola:
                print("❌ Perfil ou escola não encontrados!")
                return False
            
            # Lista de usuários para criar
            usuarios_teste = [
                {
                    'nome': 'Admin Sistema',
                    'email': 'admin@escola.com',
                    'senha': '123456',
                    'cpf': '111.111.111-11'
                },
                {
                    'nome': 'Teste Admin',
                    'email': 'teste@admin.com', 
                    'senha': 'teste123',
                    'cpf': '222.222.222-22'
                },
                {
                    'nome': 'Super Admin',
                    'email': 'super@admin.com',
                    'senha': 'super123',
                    'cpf': '333.333.333-33'
                }
            ]
            
            for user_data in usuarios_teste:
                # Verificar se já existe
                existing = Usuario.query.filter_by(email=user_data['email']).first()
                if existing:
                    print(f"ℹ️  Usuário {user_data['email']} já existe")
                    continue
                
                # Criar usuário
                usuario = Usuario(
                    nome=user_data['nome'],
                    email=user_data['email'],
                    cpf=user_data['cpf'],
                    telefone='(11) 99999-9999',
                    perfil_id=perfil_admin.id_perfil,
                    escola_id=escola.id,
                    situacao='ativo',
                    data_nascimento=datetime(1980, 1, 1).date()
                )
                
                usuario.set_password(user_data['senha'])
                db.session.add(usuario)
                
                print(f"✅ Criado: {user_data['email']} / {user_data['senha']}")
            
            db.session.commit()
            
            # Listar todos os usuários
            print("\n📋 USUÁRIOS DISPONÍVEIS:")
            print("-" * 40)
            
            usuarios = Usuario.query.all()
            for usuario in usuarios:
                print(f"📧 Email: {usuario.email}")
                print(f"👤 Nome: {usuario.nome}")
                print(f"🏷️  Perfil: {usuario.perfil.perfil if usuario.perfil else 'Sem perfil'}")
                print(f"🏫 Escola: {usuario.escola.nome if usuario.escola else 'Sem escola'}")
                print("-" * 30)
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def reset_admin_password():
    """Resetar senha do admin principal"""
    print("\n🔧 RESETANDO SENHA DO ADMIN PRINCIPAL")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario
            
            # Buscar admin principal
            admin = Usuario.query.filter_by(email='admin@sistema.com').first()
            
            if admin:
                # Resetar senha
                admin.set_password('admin123')
                db.session.commit()
                
                print("✅ Senha resetada!")
                print("📧 Email: admin@sistema.com")
                print("🔑 Senha: admin123")
                
                # Testar login
                if admin.check_password('admin123'):
                    print("✅ Login testado e funcionando!")
                else:
                    print("❌ Erro no teste de login!")
                
                return True
            else:
                print("❌ Admin não encontrado!")
                return False
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("🔐 CONFIGURAÇÃO DE USUÁRIOS")
    print("=" * 50)
    
    # Resetar senha do admin principal
    reset_admin_password()
    
    # Criar usuários de teste
    create_test_users()
    
    print("\n🎯 CREDENCIAIS PARA TESTE:")
    print("=" * 30)
    print("1️⃣  admin@sistema.com / admin123")
    print("2️⃣  admin@escola.com / 123456") 
    print("3️⃣  teste@admin.com / teste123")
    print("4️⃣  super@admin.com / super123")
    print()
    print("🌐 URL: http://localhost:5000")
    print("🎛️  Admin: http://localhost:5000/admin")
