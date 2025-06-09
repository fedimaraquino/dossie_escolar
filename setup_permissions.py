#!/usr/bin/env python3
# setup_permissions.py - Configurar permissões do sistema
from models import db, Perfil, Permissao, PerfilPermissao
from app import create_app




def create_permissions():
    """Criar todas as permissões do sistema"""
    print("🔐 CRIANDO PERMISSÕES DO SISTEMA")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            
            
            # Definir todas as permissões do sistema
            permissoes_sistema = [
                # USUÁRIOS
                {'nome': 'usuario_criar', 'descricao': 'Criar usuários', 'modulo': 'usuario', 'acao': 'criar'},
                {'nome': 'usuario_editar', 'descricao': 'Editar usuários', 'modulo': 'usuario', 'acao': 'editar'},
                {'nome': 'usuario_excluir', 'descricao': 'Excluir usuários', 'modulo': 'usuario', 'acao': 'excluir'},
                {'nome': 'usuario_visualizar', 'descricao': 'Visualizar usuários', 'modulo': 'usuario', 'acao': 'visualizar'},
                
                # ESCOLAS
                {'nome': 'escola_criar', 'descricao': 'Criar escolas', 'modulo': 'escola', 'acao': 'criar'},
                {'nome': 'escola_editar', 'descricao': 'Editar escolas', 'modulo': 'escola', 'acao': 'editar'},
                {'nome': 'escola_excluir', 'descricao': 'Excluir escolas', 'modulo': 'escola', 'acao': 'excluir'},
                {'nome': 'escola_visualizar', 'descricao': 'Visualizar escolas', 'modulo': 'escola', 'acao': 'visualizar'},

                # DIRETORES
                {'nome': 'diretor_criar', 'descricao': 'Criar diretores', 'modulo': 'diretor', 'acao': 'criar'},
                {'nome': 'diretor_editar', 'descricao': 'Editar diretores', 'modulo': 'diretor', 'acao': 'editar'},
                {'nome': 'diretor_excluir', 'descricao': 'Excluir diretores', 'modulo': 'diretor', 'acao': 'excluir'},
                {'nome': 'diretor_visualizar', 'descricao': 'Visualizar diretores', 'modulo': 'diretor', 'acao': 'visualizar'},
                
                # DOSSIÊS
                {'nome': 'dossie_criar', 'descricao': 'Criar dossiês', 'modulo': 'dossie', 'acao': 'criar'},
                {'nome': 'dossie_editar', 'descricao': 'Editar dossiês', 'modulo': 'dossie', 'acao': 'editar'},
                {'nome': 'dossie_excluir', 'descricao': 'Excluir dossiês', 'modulo': 'dossie', 'acao': 'excluir'},
                {'nome': 'dossie_visualizar', 'descricao': 'Visualizar dossiês', 'modulo': 'dossie', 'acao': 'visualizar'},
                
                # ANEXOS
                {'nome': 'anexo_criar', 'descricao': 'Adicionar anexos', 'modulo': 'anexo', 'acao': 'criar'},
                {'nome': 'anexo_editar', 'descricao': 'Editar anexos', 'modulo': 'anexo', 'acao': 'editar'},
                {'nome': 'anexo_excluir', 'descricao': 'Excluir anexos', 'modulo': 'anexo', 'acao': 'excluir'},
                {'nome': 'anexo_visualizar', 'descricao': 'Visualizar anexos', 'modulo': 'anexo', 'acao': 'visualizar'},
                
                # MOVIMENTAÇÕES
                {'nome': 'movimentacao_criar', 'descricao': 'Criar movimentações', 'modulo': 'movimentacao', 'acao': 'criar'},
                {'nome': 'movimentacao_editar', 'descricao': 'Editar movimentações', 'modulo': 'movimentacao', 'acao': 'editar'},
                {'nome': 'movimentacao_excluir', 'descricao': 'Excluir movimentações', 'modulo': 'movimentacao', 'acao': 'excluir'},
                {'nome': 'movimentacao_visualizar', 'descricao': 'Visualizar movimentações', 'modulo': 'movimentacao', 'acao': 'visualizar'},
                
                # RELATÓRIOS
                {'nome': 'relatorio_geral', 'descricao': 'Relatórios gerais', 'modulo': 'relatorio', 'acao': 'visualizar'},
                {'nome': 'relatorio_escola', 'descricao': 'Relatórios da escola', 'modulo': 'relatorio', 'acao': 'escola'},
                
                # ADMINISTRAÇÃO
                {'nome': 'admin_sistema', 'descricao': 'Administração do sistema', 'modulo': 'admin', 'acao': 'total'},
                {'nome': 'admin_backup', 'descricao': 'Fazer backup', 'modulo': 'admin', 'acao': 'backup'},
                {'nome': 'admin_logs', 'descricao': 'Visualizar logs', 'modulo': 'admin', 'acao': 'logs'},
                
                # PERFIS E PERMISSÕES
                {'nome': 'perfil_criar', 'descricao': 'Criar perfis', 'modulo': 'perfil', 'acao': 'criar'},
                {'nome': 'perfil_editar', 'descricao': 'Editar perfis', 'modulo': 'perfil', 'acao': 'editar'},
                {'nome': 'perfil_excluir', 'descricao': 'Excluir perfis', 'modulo': 'perfil', 'acao': 'excluir'},
                {'nome': 'perfil_visualizar', 'descricao': 'Visualizar perfis', 'modulo': 'perfil', 'acao': 'visualizar'},

                # CIDADES
                {'nome': 'cidade_criar', 'descricao': 'Criar cidades', 'modulo': 'cidade', 'acao': 'criar'},
                {'nome': 'cidade_editar', 'descricao': 'Editar cidades', 'modulo': 'cidade', 'acao': 'editar'},
                {'nome': 'cidade_excluir', 'descricao': 'Excluir cidades', 'modulo': 'cidade', 'acao': 'excluir'},
                {'nome': 'cidade_visualizar', 'descricao': 'Visualizar cidades', 'modulo': 'cidade', 'acao': 'visualizar'},

                # PERMISSÕES
                {'nome': 'permissao_visualizar', 'descricao': 'Visualizar permissões', 'modulo': 'permissao', 'acao': 'visualizar'},
                {'nome': 'permissao_editar', 'descricao': 'Editar permissões', 'modulo': 'permissao', 'acao': 'editar'},

                # MENUS DE NAVEGAÇÃO
                {'nome': 'menu_manutencao', 'descricao': 'Acessar menu Manutenção', 'modulo': 'menu', 'acao': 'manutencao'},
                {'nome': 'menu_dossie', 'descricao': 'Acessar menu Dossiês', 'modulo': 'menu', 'acao': 'dossie'},
                {'nome': 'menu_movimentacao', 'descricao': 'Acessar menu Movimentações', 'modulo': 'menu', 'acao': 'movimentacao'},
                {'nome': 'menu_relatorio', 'descricao': 'Acessar menu Relatórios', 'modulo': 'menu', 'acao': 'relatorio'},
                {'nome': 'menu_admin', 'descricao': 'Acessar menu Administração', 'modulo': 'menu', 'acao': 'admin'},
            ]
            
            # Criar permissões
            for perm_data in permissoes_sistema:
                # Verificar se já existe
                existing = Permissao.query.filter_by(nome=perm_data['nome']).first()
                if not existing:
                    permissao = Permissao(**perm_data)
                    db.session.add(permissao)
                    print(f"✅ Criada: {perm_data['nome']}")
                else:
                    print(f"ℹ️  Já existe: {perm_data['nome']}")
            
            db.session.commit()
            
            total = Permissao.query.count()
            print(f"\n📊 Total de permissões: {total}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def assign_permissions_to_profiles():
    """Atribuir permissões aos perfis"""
    print("\n🎯 ATRIBUINDO PERMISSÕES AOS PERFIS")
    print("=" * 40)
    
    try:
        
        
        app = create_app()
        
        with app.app_context():
            
            
            # Configurações de permissões por perfil
            perfil_configs = {
                'Administrador Geral': 'ALL',  # Todas as permissões
                
                'Administrador da Escola': [
                    # Usuários da escola
                    'usuario_criar', 'usuario_editar', 'usuario_visualizar',
                    # Diretores
                    'diretor_criar', 'diretor_editar', 'diretor_excluir', 'diretor_visualizar',
                    # Dossiês
                    'dossie_criar', 'dossie_editar', 'dossie_excluir', 'dossie_visualizar',
                    # Anexos
                    'anexo_criar', 'anexo_editar', 'anexo_excluir', 'anexo_visualizar',
                    # Movimentações
                    'movimentacao_criar', 'movimentacao_editar', 'movimentacao_visualizar',
                    # Relatórios da escola
                    'relatorio_escola',
                    # Visualizar escola e cidades
                    'escola_visualizar', 'cidade_visualizar',
                    # Perfis
                    'perfil_visualizar',
                    # Permissões
                    'permissao_visualizar',
                    # Menus
                    'menu_manutencao', 'menu_dossie', 'menu_movimentacao', 'menu_relatorio'
                ],
                
                'Operador': [
                    # Dossiês
                    'dossie_criar', 'dossie_editar', 'dossie_visualizar',
                    # Anexos
                    'anexo_criar', 'anexo_editar', 'anexo_visualizar',
                    # Movimentações
                    'movimentacao_criar', 'movimentacao_visualizar',
                    # Visualizar usuários, diretores, escola e cidades
                    'usuario_visualizar', 'diretor_visualizar', 'escola_visualizar', 'cidade_visualizar',
                    # Menus básicos
                    'menu_dossie', 'menu_movimentacao'
                ],
                
                'Consulta': [
                    # Apenas visualização
                    'dossie_visualizar',
                    'anexo_visualizar',
                    'movimentacao_visualizar',
                    'usuario_visualizar',
                    'diretor_visualizar',
                    'escola_visualizar',
                    'cidade_visualizar',
                    # Menus básicos
                    'menu_dossie', 'menu_movimentacao'
                ]
            }
            
            # Processar cada perfil
            for perfil_nome, permissoes in perfil_configs.items():
                perfil = Perfil.query.filter_by(perfil=perfil_nome).first()
                if not perfil:
                    print(f"⚠️  Perfil '{perfil_nome}' não encontrado")
                    continue
                
                print(f"\n👤 Configurando: {perfil_nome}")
                
                # Limpar permissões existentes
                PerfilPermissao.query.filter_by(perfil_id=perfil.id_perfil).delete()
                
                if permissoes == 'ALL':
                    # Administrador Geral tem todas as permissões
                    todas_permissoes = Permissao.query.all()
                    for permissao in todas_permissoes:
                        pp = PerfilPermissao(perfil_id=perfil.id_perfil, permissao_id=permissao.id)
                        db.session.add(pp)
                    print(f"   ✅ Todas as permissões ({len(todas_permissoes)})")
                else:
                    # Atribuir permissões específicas
                    for perm_nome in permissoes:
                        permissao = Permissao.query.filter_by(nome=perm_nome).first()
                        if permissao:
                            pp = PerfilPermissao(perfil_id=perfil.id_perfil, permissao_id=permissao.id)
                            db.session.add(pp)
                            print(f"   ✅ {perm_nome}")
                        else:
                            print(f"   ❌ Permissão '{perm_nome}' não encontrada")
            
            db.session.commit()
            print("\n✅ Permissões atribuídas com sucesso!")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def show_permissions_summary():
    """Mostrar resumo das permissões"""
    print("\n📋 RESUMO DAS PERMISSÕES")
    print("=" * 40)
    
    try:
       
        
        app = create_app()
        
        with app.app_context():
            from models import Perfil, Permissao, PerfilPermissao
            
            perfis = Perfil.query.all()
            
            for perfil in perfis:
                print(f"\n👤 {perfil.perfil}")
                print("-" * 30)
                
                # Buscar permissões do perfil
                permissoes = db.session.query(Permissao).join(PerfilPermissao).filter(
                    PerfilPermissao.perfil_id == perfil.id_perfil
                ).all()
                
                if permissoes:
                    # Agrupar por módulo
                    modulos = {}
                    for perm in permissoes:
                        if perm.modulo not in modulos:
                            modulos[perm.modulo] = []
                        modulos[perm.modulo].append(perm.acao)
                    
                    for modulo, acoes in modulos.items():
                        print(f"   📁 {modulo.upper()}: {', '.join(acoes)}")
                else:
                    print("   ❌ Nenhuma permissão")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("🔐 CONFIGURAÇÃO DE PERMISSÕES")
    print("=" * 50)
    
    # 1. Criar permissões
    if create_permissions():
        # 2. Atribuir aos perfis
        if assign_permissions_to_profiles():
            # 3. Mostrar resumo
            show_permissions_summary()
            
            print("\n🎉 SISTEMA DE PERMISSÕES CONFIGURADO!")
            print("\n📋 PRÓXIMOS PASSOS:")
            print("1. python manage.py makemigrations")
            print("2. python manage.py migrate-db")
            print("3. Testar permissões no sistema")
    else:
        print("\n❌ Falha na configuração")
