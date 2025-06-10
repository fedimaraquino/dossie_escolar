#!/usr/bin/env python3
"""
Script para listar perfis e suas permissões
"""

from app import create_app

def listar_perfis_permissoes():
    """Lista todos os perfis e suas permissões"""
    print("=" * 80)
    print("📋 PERFIS E PERMISSÕES DO SISTEMA")
    print("=" * 80)
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import db, Perfil, PerfilPermissao, Permissao
            
            # Buscar todos os perfis
            perfis = Perfil.query.all()
            
            if not perfis:
                print("❌ Nenhum perfil encontrado no sistema")
                return
            
            print(f"\n📊 Total de perfis cadastrados: {len(perfis)}")
            
            for perfil in perfis:
                print(f"\n" + "="*60)
                print(f"🔹 PERFIL: {perfil.perfil.upper()}")
                print(f"   ID: {perfil.id_perfil}")
                print(f"   Descrição: {perfil.descricao or perfil.get_descricao_padrao()}")
                
                # Buscar permissões do perfil
                if perfil.perfil == 'Administrador Geral':
                    print(f"   🔓 ACESSO TOTAL - Todas as permissões do sistema")
                else:
                    permissoes = db.session.query(Permissao).join(PerfilPermissao).filter(
                        PerfilPermissao.perfil_id == perfil.id_perfil
                    ).all()
                    
                    if permissoes:
                        print(f"   📋 Permissões ({len(permissoes)} itens):")
                        
                        # Agrupar por módulo
                        modulos = {}
                        for perm in permissoes:
                            if perm.modulo not in modulos:
                                modulos[perm.modulo] = []
                            modulos[perm.modulo].append(perm.acao)
                        
                        for modulo, acoes in modulos.items():
                            acoes_str = ", ".join(sorted(acoes))
                            print(f"      🔸 {modulo}: {acoes_str}")
                    else:
                        print(f"   ❌ Nenhuma permissão específica configurada")
                
                # Verificar usuários com este perfil
                from models import Usuario
                usuarios_count = Usuario.query.filter_by(perfil_id=perfil.id_perfil).count()
                print(f"   👥 Usuários com este perfil: {usuarios_count}")
            
            print(f"\n" + "="*80)
            print("📋 RESUMO DAS PERMISSÕES DISPONÍVEIS:")
            print("="*80)
            
            # Listar todas as permissões disponíveis
            todas_permissoes = Permissao.query.all()
            modulos_sistema = {}
            
            for perm in todas_permissoes:
                if perm.modulo not in modulos_sistema:
                    modulos_sistema[perm.modulo] = []
                if perm.acao not in modulos_sistema[perm.modulo]:
                    modulos_sistema[perm.modulo].append(perm.acao)
            
            for modulo, acoes in sorted(modulos_sistema.items()):
                acoes_str = ", ".join(sorted(acoes))
                print(f"🔸 {modulo}: {acoes_str}")
            
            print(f"\n📊 Total de módulos: {len(modulos_sistema)}")
            print(f"📊 Total de permissões: {len(todas_permissoes)}")
            
    except Exception as e:
        print(f"❌ Erro ao listar perfis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    listar_perfis_permissoes()
