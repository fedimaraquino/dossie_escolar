#!/usr/bin/env python3
# test_app.py - Testar se app funciona

try:
    print("🔍 Testando imports...")
    
    from app import create_app
    print("✅ App importado")
    
    app = create_app()
    print("✅ App criado")
    
    with app.app_context():
        from models import db, Usuario, Perfil, Permissao
        print("✅ Models importados")
        
        # Testar conexão
        usuarios = Usuario.query.count()
        print(f"✅ Banco conectado - {usuarios} usuários")
    
    print("🎉 Tudo funcionando!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
