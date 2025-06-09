#!/usr/bin/env python3
# verificar_permissoes_completas.py - Verificar todas as permissões do sistema

def verificar_permissoes_completas():
    print("🔐 VERIFICAÇÃO COMPLETA DE PERMISSÕES")
    print("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import db, Permissao, Perfil, PerfilPermissao
            
            print("✅ Conectado ao banco de dados")
            
            # Verificar todas as permissões por módulo
            print("\n📋 PERMISSÕES POR MÓDULO:")
            print("-" * 40)
            
            from sqlalchemy import func
            modulos = db.session.query(
                Permissao.modulo,
                func.count(Permissao.id).label('total')
            ).group_by(Permissao.modulo).order_by(Permissao.modulo).all()
            
            total_permissoes = 0
            for modulo, count in modulos:
                print(f"📁 {modulo.upper()}: {count} permissões")
                
                # Listar permissões do módulo
                permissoes = Permissao.query.filter_by(modulo=modulo).order_by(Permissao.acao).all()
                for perm in permissoes:
                    print(f"   ✓ {perm.acao} - {perm.descricao}")
                
                total_permissoes += count
                print()
            
            print(f"📊 TOTAL: {total_permissoes} permissões no sistema")
            
            # Verificar permissões por perfil
            print("\n👥 PERMISSÕES POR PERFIL:")
            print("-" * 40)
            
            perfis = Perfil.query.order_by(Perfil.perfil).all()
            
            for perfil in perfis:
                permissoes_perfil = db.session.query(Permissao).join(PerfilPermissao).filter(
                    PerfilPermissao.perfil_id == perfil.id_perfil
                ).order_by(Permissao.modulo, Permissao.acao).all()
                
                print(f"\n🔑 {perfil.perfil.upper()}:")
                print(f"   📊 Total: {len(permissoes_perfil)} permissões")
                
                # Agrupar por módulo
                modulos_perfil = {}
                for perm in permissoes_perfil:
                    if perm.modulo not in modulos_perfil:
                        modulos_perfil[perm.modulo] = []
                    modulos_perfil[perm.modulo].append(perm.acao)
                
                for modulo, acoes in sorted(modulos_perfil.items()):
                    print(f"   📁 {modulo}: {', '.join(sorted(acoes))}")
            
            # Verificar cobertura de permissões
            print(f"\n📈 ANÁLISE DE COBERTURA:")
            print("-" * 30)
            
            admin_geral = Perfil.query.filter_by(perfil='Administrador Geral').first()
            if admin_geral:
                admin_permissoes = db.session.query(Permissao).join(PerfilPermissao).filter(
                    PerfilPermissao.perfil_id == admin_geral.id_perfil
                ).count()
                
                cobertura = (admin_permissoes / total_permissoes * 100) if total_permissoes > 0 else 0
                print(f"🔑 Admin Geral: {admin_permissoes}/{total_permissoes} ({cobertura:.1f}%)")
                
                if cobertura == 100:
                    print("   ✅ Admin Geral tem TODAS as permissões")
                else:
                    print("   ⚠️  Admin Geral NÃO tem todas as permissões")
                    
                    # Mostrar permissões faltantes
                    todas_permissoes = set(p.nome for p in Permissao.query.all())
                    admin_permissoes_nomes = set(p.nome for p in db.session.query(Permissao).join(PerfilPermissao).filter(
                        PerfilPermissao.perfil_id == admin_geral.id_perfil
                    ).all())
                    
                    faltantes = todas_permissoes - admin_permissoes_nomes
                    if faltantes:
                        print("   ❌ Permissões faltantes:")
                        for perm in sorted(faltantes):
                            print(f"      - {perm}")
            
            # Verificar módulos de menu
            print(f"\n🎯 PERMISSÕES DE MENU:")
            print("-" * 25)
            
            menu_permissoes = Permissao.query.filter_by(modulo='menu').all()
            if menu_permissoes:
                for perm in menu_permissoes:
                    print(f"🎛️  {perm.nome} - {perm.descricao}")
                    
                    # Ver quais perfis têm esta permissão
                    perfis_com_permissao = db.session.query(Perfil).join(PerfilPermissao).join(Permissao).filter(
                        Permissao.id == perm.id
                    ).all()
                    
                    if perfis_com_permissao:
                        perfis_nomes = [p.perfil for p in perfis_com_permissao]
                        print(f"   👥 Perfis: {', '.join(perfis_nomes)}")
                    else:
                        print(f"   ❌ Nenhum perfil tem esta permissão")
                    print()
            else:
                print("❌ Nenhuma permissão de menu encontrada")
            
            # Verificar novos módulos
            print(f"\n🆕 NOVOS MÓDULOS ADICIONADOS:")
            print("-" * 35)
            
            novos_modulos = ['cidade', 'permissao', 'menu']
            for modulo in novos_modulos:
                permissoes_modulo = Permissao.query.filter_by(modulo=modulo).count()
                if permissoes_modulo > 0:
                    print(f"✅ {modulo.upper()}: {permissoes_modulo} permissões")
                else:
                    print(f"❌ {modulo.upper()}: Não encontrado")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_funcoes_template():
    """Testar se as funções de template estão funcionando"""
    print("\n🧪 TESTANDO FUNÇÕES DE TEMPLATE:")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            from models import Usuario
            from utils.permissions import has_permission, can_access_menu
            
            # Testar com admin geral
            admin = Usuario.query.filter_by(email='admin@sistema.com').first()
            
            if admin:
                print(f"👤 Testando usuário: {admin.nome}")
                print(f"   Perfil: {admin.perfil_obj.perfil if admin.perfil_obj else 'Sem perfil'}")
                
                # Testar permissões de módulos
                modulos = ['usuario', 'escola', 'diretor', 'cidade', 'dossie', 'movimentacao']
                acoes = ['visualizar', 'criar', 'editar', 'excluir']
                
                print(f"\n📋 TESTE DE PERMISSÕES:")
                for modulo in modulos:
                    print(f"   📁 {modulo.upper()}:")
                    for acao in acoes:
                        tem_permissao = has_permission(admin, modulo, acao)
                        status = "✅" if tem_permissao else "❌"
                        print(f"      {status} {acao}")
                
                # Testar permissões de menu
                print(f"\n🎛️  TESTE DE MENUS:")
                menus = ['manutencao', 'dossie', 'movimentacao', 'relatorio', 'admin']
                for menu in menus:
                    tem_acesso = can_access_menu(admin, menu)
                    status = "✅" if tem_acesso else "❌"
                    print(f"   {status} menu_{menu}")
                
                return True
            else:
                print("❌ Usuário admin não encontrado")
                return False
                
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = verificar_permissoes_completas()
    
    if sucesso:
        testar_funcoes_template()
        print(f"\n🎉 VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"💡 Acesse: http://localhost:5000/permissoes/perfis")
        print(f"🔧 Para configurar permissões via interface")
        print(f"📊 Acesse: http://localhost:5000/admin/models")
        print(f"🗄️  Para ver todos os modelos no admin")
    else:
        print(f"\n❌ FALHA NA VERIFICAÇÃO!")
        print(f"💡 Execute: python setup_permissions.py")
