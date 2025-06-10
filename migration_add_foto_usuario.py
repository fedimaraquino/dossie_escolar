#!/usr/bin/env python3
"""
Migração para adicionar campo 'foto' na tabela de usuários
"""

from app import create_app

def add_foto_field():
    """Adicionar campo foto na tabela usuarios"""
    print("🔄 MIGRAÇÃO: Adicionando campo 'foto' na tabela usuarios")
    print("=" * 60)
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import db
            from sqlalchemy import text
            
            # Verificar se a coluna já existe
            print("🔍 Verificando se a coluna 'foto' já existe...")
            
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND column_name = 'foto'
            """)).fetchone()
            
            if result:
                print("   ℹ️  Coluna 'foto' já existe na tabela usuarios")
                return True
            
            # Adicionar coluna foto
            print("📝 Adicionando coluna 'foto' na tabela usuarios...")
            
            db.session.execute(text("""
                ALTER TABLE usuarios 
                ADD COLUMN foto VARCHAR(255)
            """))
            
            # Commit da alteração
            db.session.commit()
            
            print("   ✅ Coluna 'foto' adicionada com sucesso!")
            
            # Verificar se foi criada corretamente
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' 
                AND column_name = 'foto'
            """)).fetchone()
            
            if result:
                print(f"   📊 Detalhes da coluna:")
                print(f"      Nome: {result[0]}")
                print(f"      Tipo: {result[1]}")
                print(f"      Nullable: {result[2]}")
            
            # Criar diretórios necessários
            print("\n📁 Criando diretórios para fotos...")
            
            import os
            
            directories = [
                'static/uploads',
                'static/uploads/fotos',
                'static/img'
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    print(f"   ✅ Diretório criado: {directory}")
                else:
                    print(f"   ℹ️  Diretório já existe: {directory}")
            
            # Verificar se a imagem padrão existe
            default_avatar_path = 'static/img/default-avatar.svg'
            if os.path.exists(default_avatar_path):
                print(f"   ✅ Imagem padrão encontrada: {default_avatar_path}")
            else:
                print(f"   ⚠️  Imagem padrão não encontrada: {default_avatar_path}")
            
            print(f"\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"\n📋 Resumo das alterações:")
            print(f"   ✅ Campo 'foto' adicionado na tabela usuarios")
            print(f"   ✅ Diretórios criados para upload de fotos")
            print(f"   ✅ Sistema pronto para gerenciar fotos de usuários")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migration():
    """Verificar se a migração foi aplicada corretamente"""
    print("\n🔍 VERIFICAÇÃO DA MIGRAÇÃO")
    print("=" * 40)
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario
            from sqlalchemy import text
            
            # Verificar estrutura da tabela
            print("📊 Verificando estrutura da tabela usuarios...")
            
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'usuarios'
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("\n📋 Colunas da tabela usuarios:")
            for row in result:
                status = "✅" if row[0] == 'foto' else "  "
                print(f"   {status} {row[0]:20s} | {row[1]:15s} | Nullable: {row[2]}")
            
            # Testar modelo Usuario
            print("\n🧪 Testando modelo Usuario...")
            
            # Verificar se o modelo tem os novos métodos
            usuario_test = Usuario()
            
            methods_to_check = ['get_foto_url', 'has_foto', 'set_foto', 'remove_foto']
            
            for method in methods_to_check:
                if hasattr(usuario_test, method):
                    print(f"   ✅ Método {method} disponível")
                else:
                    print(f"   ❌ Método {method} não encontrado")
            
            # Verificar diretórios
            print("\n📁 Verificando diretórios:")
            
            import os
            
            directories = [
                'static/uploads/fotos',
                'static/img'
            ]
            
            for directory in directories:
                if os.path.exists(directory):
                    print(f"   ✅ {directory}")
                else:
                    print(f"   ❌ {directory} não encontrado")
            
            print(f"\n✅ VERIFICAÇÃO CONCLUÍDA!")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == '__main__':
    print("🚀 MIGRAÇÃO: CAMPO FOTO PARA USUÁRIOS")
    print("=" * 70)
    
    try:
        # Executar migração
        if add_foto_field():
            # Verificar migração
            verify_migration()
            
            print(f"\n🎉 MIGRAÇÃO COMPLETA!")
            print(f"\n📋 Próximos passos:")
            print(f"   1. Reinicie o servidor Flask")
            print(f"   2. Acesse o perfil do usuário")
            print(f"   3. Teste o upload de foto")
            print(f"   4. Verifique se a foto aparece na barra de navegação")
            
        else:
            print(f"\n❌ MIGRAÇÃO FALHOU!")
            print(f"   Verifique os erros acima e tente novamente")
            
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
