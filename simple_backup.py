#!/usr/bin/env python3
# simple_backup.py - Backup simples e funcional

def create_backup():
    """Criar backup do banco de dados"""
    print("💾 BACKUP DO SISTEMA DE DOSSIÊ")
    print("=" * 40)
    
    try:
        from app import create_app
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            from models import db, Usuario, Escola, Dossie, Anexo, Perfil, Cidade, Movimentacao, Permissao, PerfilPermissao
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_sistema_{timestamp}.sql"
            
            print(f"📝 Criando backup: {backup_file}")
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("-- ========================================\n")
                f.write("-- BACKUP SISTEMA DE DOSSIÊ ESCOLAR\n")
                f.write(f"-- Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("-- ========================================\n\n")
                
                # Estatísticas
                stats = {
                    'perfis': Perfil.query.count(),
                    'cidades': Cidade.query.count(),
                    'escolas': Escola.query.count(),
                    'usuarios': Usuario.query.count(),
                    'permissoes': Permissao.query.count(),
                    'perfil_permissoes': PerfilPermissao.query.count(),
                    'dossies': Dossie.query.count(),
                    'anexos': Anexo.query.count(),
                    'movimentacoes': Movimentacao.query.count(),
                }
                
                f.write("-- ESTATÍSTICAS DO BACKUP\n")
                total_records = 0
                for table, count in stats.items():
                    f.write(f"-- {table}: {count} registros\n")
                    total_records += count
                f.write(f"-- TOTAL: {total_records} registros\n\n")
                
                # Backup dos dados principais
                f.write("-- ========================================\n")
                f.write("-- DADOS PRINCIPAIS\n")
                f.write("-- ========================================\n\n")
                
                # Perfis
                f.write("-- PERFIS\n")
                perfis = Perfil.query.all()
                for perfil in perfis:
                    f.write(f"-- ID: {perfil.id_perfil}, Nome: {perfil.perfil}, Desc: {perfil.descricao}\n")
                f.write(f"-- Total de perfis: {len(perfis)}\n\n")
                
                # Usuários
                f.write("-- USUÁRIOS\n")
                usuarios = Usuario.query.all()
                for usuario in usuarios:
                    perfil_nome = usuario.perfil_obj.perfil if usuario.perfil_obj else 'Sem perfil'
                    escola_nome = usuario.escola.nome if usuario.escola else 'Sem escola'
                    f.write(f"-- ID: {usuario.id}, Nome: {usuario.nome}, Email: {usuario.email}, Perfil: {perfil_nome}, Escola: {escola_nome}\n")
                f.write(f"-- Total de usuários: {len(usuarios)}\n\n")
                
                # Escolas
                f.write("-- ESCOLAS\n")
                escolas = Escola.query.all()
                for escola in escolas:
                    f.write(f"-- ID: {escola.id}, Nome: {escola.nome}, CNPJ: {escola.cnpj}, Diretor: {escola.diretor}\n")
                f.write(f"-- Total de escolas: {len(escolas)}\n\n")
                
                # Dossiês
                f.write("-- DOSSIÊS\n")
                dossies = Dossie.query.all()
                for dossie in dossies:
                    escola_nome = dossie.escola.nome if dossie.escola else 'Sem escola'
                    f.write(f"-- ID: {dossie.id}, Número: {dossie.n_dossie}, Nome: {dossie.nome}, Escola: {escola_nome}, Ano: {dossie.ano}\n")
                f.write(f"-- Total de dossiês: {len(dossies)}\n\n")
                
                # Permissões
                f.write("-- PERMISSÕES\n")
                permissoes = Permissao.query.all()
                for perm in permissoes:
                    f.write(f"-- ID: {perm.id}, Nome: {perm.nome}, Módulo: {perm.modulo}, Ação: {perm.acao}\n")
                f.write(f"-- Total de permissões: {len(permissoes)}\n\n")
                
                # Configurações do sistema
                f.write("-- ========================================\n")
                f.write("-- CONFIGURAÇÕES DO SISTEMA\n")
                f.write("-- ========================================\n\n")
                
                f.write(f"-- Banco de dados: {app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'SQLite'}\n")
                f.write(f"-- Debug mode: {app.config.get('DEBUG', False)}\n")
                f.write(f"-- Secret key configurado: {'Sim' if app.config.get('SECRET_KEY') else 'Não'}\n")
                
                f.write("\n-- ========================================\n")
                f.write("-- FIM DO BACKUP\n")
                f.write("-- ========================================\n")
            
            # Informações do backup
            import os
            size = os.path.getsize(backup_file) / 1024
            
            print(f"✅ Backup criado com sucesso!")
            print(f"📁 Arquivo: {backup_file}")
            print(f"📊 Tamanho: {size:.2f} KB")
            print(f"📈 Registros: {total_records}")
            
            # Mostrar estatísticas
            print(f"\n📋 ESTATÍSTICAS:")
            for table, count in stats.items():
                if count > 0:
                    print(f"   ✓ {table}: {count}")
            
            return backup_file
            
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    backup_file = create_backup()
    
    if backup_file:
        print(f"\n🎉 BACKUP CONCLUÍDO!")
        print(f"📁 Arquivo salvo: {backup_file}")
        print(f"💡 Para restaurar, use este arquivo como referência")
    else:
        print(f"\n❌ FALHA NO BACKUP!")
        print(f"💡 Verifique os logs de erro acima")
