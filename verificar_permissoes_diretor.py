#!/usr/bin/env python3
# verificar_permissoes_diretor.py - Verificar se as permissões de diretor foram criadas

def verificar_permissoes():
    print("🔐 VERIFICANDO PERMISSÕES DE DIRETOR")
    print("=" * 50)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Permissao, Perfil, PerfilPermissao
            
            print("✅ Conectado ao banco de dados")
            
            # Verificar permissões de diretor
            print("\n📋 PERMISSÕES DE DIRETOR:")
            print("-" * 30)
            
            permissoes_diretor = Permissao.query.filter_by(modulo='diretor').all()
            
            if not permissoes_diretor:
                print("❌ Nenhuma permissão de diretor encontrada!")
                return False
            
            for perm in permissoes_diretor:
                print(f"✅ {perm.nome} - {perm.descricao}")
            
            print(f"\n📊 Total de permissões de diretor: {len(permissoes_diretor)}")
            
            # Verificar quais perfis têm permissões de diretor
            print("\n👥 PERFIS COM PERMISSÕES DE DIRETOR:")
            print("-" * 40)
            
            perfis = Perfil.query.all()
            
            for perfil in perfis:
                permissoes_perfil = db.session.query(Permissao).join(PerfilPermissao).filter(
                    PerfilPermissao.perfil_id == perfil.id_perfil,
                    Permissao.modulo == 'diretor'
                ).all()
                
                if permissoes_perfil:
                    print(f"\n👤 {perfil.perfil}:")
                    for perm in permissoes_perfil:
                        print(f"   ✓ {perm.acao} - {perm.descricao}")
                else:
                    print(f"\n👤 {perfil.perfil}: Sem permissões de diretor")
            
            # Verificar total de permissões no sistema
            print(f"\n📈 ESTATÍSTICAS GERAIS:")
            print("-" * 25)
            
            total_permissoes = Permissao.query.count()
            print(f"📊 Total de permissões no sistema: {total_permissoes}")
            
            # Permissões por módulo
            from sqlalchemy import func
            modulos = db.session.query(
                Permissao.modulo,
                func.count(Permissao.id)
            ).group_by(Permissao.modulo).all()
            
            print(f"\n📋 PERMISSÕES POR MÓDULO:")
            for modulo, count in modulos:
                print(f"   {modulo}: {count} permissões")
            
            # Verificar se Admin Geral tem todas as permissões
            admin_geral = Perfil.query.filter_by(perfil='Administrador Geral').first()
            if admin_geral:
                admin_permissoes = db.session.query(Permissao).join(PerfilPermissao).filter(
                    PerfilPermissao.perfil_id == admin_geral.id_perfil
                ).count()
                
                print(f"\n🔑 ADMIN GERAL:")
                print(f"   Permissões: {admin_permissoes}/{total_permissoes}")
                
                if admin_permissoes == total_permissoes:
                    print("   ✅ Admin Geral tem TODAS as permissões")
                else:
                    print("   ⚠️  Admin Geral NÃO tem todas as permissões")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_acesso_diretor():
    """Testar se um usuário pode acessar funcionalidades de diretor"""
    print("\n🧪 TESTANDO ACESSO ÀS FUNCIONALIDADES:")
    print("=" * 45)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import Usuario
            from utils.permissions import has_permission
            
            # Testar com admin geral
            admin = Usuario.query.filter_by(email='admin@sistema.com').first()
            
            if admin:
                print(f"\n👤 Testando usuário: {admin.nome}")
                print(f"   Perfil: {admin.perfil_obj.perfil if admin.perfil_obj else 'Sem perfil'}")
                
                # Testar permissões de diretor
                acoes = ['criar', 'editar', 'excluir', 'visualizar']
                
                for acao in acoes:
                    tem_permissao = has_permission(admin, 'diretor', acao)
                    status = "✅" if tem_permissao else "❌"
                    print(f"   {status} diretor_{acao}")
            else:
                print("❌ Usuário admin não encontrado")
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == '__main__':
    if verificar_permissoes():
        testar_acesso_diretor()
        print(f"\n🎉 VERIFICAÇÃO CONCLUÍDA!")
        print(f"💡 Acesse: http://localhost:5000/permissoes/perfis")
        print(f"📁 Para ver a interface de permissões")
    else:
        print(f"\n❌ FALHA NA VERIFICAÇÃO!")
        print(f"💡 Execute: python setup_permissions.py")
