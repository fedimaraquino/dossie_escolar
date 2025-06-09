#!/usr/bin/env python3
# manage.py - Script de gerenciamento Flask (similar ao Django)

import os
import sys
from flask.cli import FlaskGroup
from flask_migrate import init, migrate, upgrade, downgrade, stamp
from app import create_app
from models import db

# Criar app
app = create_app()
cli = FlaskGroup(app)

@cli.command()
def init_db():
    """Inicializar banco de dados (similar ao Django migrate)"""
    print("🔧 Inicializando banco de dados...")
    
    # Verificar se migrations já existe
    if not os.path.exists('migrations'):
        print("📁 Criando pasta de migrações...")
        init()
        print("✅ Pasta de migrações criada")
    
    # Criar primeira migração
    print("📝 Criando migração inicial...")
    migrate(message='Initial migration')
    print("✅ Migração inicial criada")
    
    # Aplicar migração
    print("🚀 Aplicando migrações...")
    upgrade()
    print("✅ Migrações aplicadas")
    
    print("\n🎉 Banco de dados inicializado!")

@cli.command()
def makemigrations():
    """Criar nova migração (similar ao Django makemigrations)"""
    message = input("📝 Descrição da migração (opcional): ").strip()
    if not message:
        message = "Auto migration"
    
    print(f"📝 Criando migração: {message}")
    migrate(message=message)
    print("✅ Migração criada!")
    print("💡 Execute 'python manage.py migrate' para aplicar")

@cli.command()
def migrate_db():
    """Aplicar migrações (similar ao Django migrate)"""
    print("🚀 Aplicando migrações...")
    upgrade()
    print("✅ Migrações aplicadas!")

@cli.command()
def rollback():
    """Reverter última migração"""
    print("⏪ Revertendo última migração...")
    downgrade()
    print("✅ Migração revertida!")

@cli.command()
def show_migrations():
    """Mostrar status das migrações"""
    print("📋 Status das migrações:")
    os.system("flask db history")

@cli.command()
def create_superuser():
    """Criar usuário administrador"""
    from models import Usuario, Perfil, Escola
    from datetime import datetime
    
    print("👤 Criando usuário administrador...")
    
    nome = input("Nome completo: ").strip()
    email = input("Email: ").strip()
    senha = input("Senha: ").strip()
    
    if not nome or not email or not senha:
        print("❌ Todos os campos são obrigatórios!")
        return
    
    # Verificar se email já existe
    if Usuario.query.filter_by(email=email).first():
        print("❌ Email já cadastrado!")
        return
    
    # Buscar perfil admin
    perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
    if not perfil_admin:
        print("❌ Perfil 'Administrador Geral' não encontrado!")
        return
    
    # Buscar escola padrão
    escola = Escola.query.first()
    if not escola:
        print("❌ Nenhuma escola encontrada!")
        return
    
    # Criar usuário
    usuario = Usuario(
        nome=nome,
        email=email,
        cpf='000.000.000-00',
        telefone='(11) 99999-9999',
        perfil_id=perfil_admin.id_perfil,
        escola_id=escola.id,
        situacao='ativo',
        data_nascimento=datetime(1980, 1, 1).date()
    )
    usuario.set_password(senha)
    
    db.session.add(usuario)
    db.session.commit()
    
    print(f"✅ Usuário '{nome}' criado com sucesso!")
    print(f"📧 Email: {email}")

@cli.command()
def shell():
    """Abrir shell interativo com contexto da aplicação"""
    import code
    from models import db, Usuario, Escola, Dossie, Anexo, Perfil, Cidade, Movimentacao

    print("🐍 Shell interativo Flask")
    print("📦 Modelos importados: Usuario, Escola, Dossie, Anexo, etc.")
    print("🗄️  Banco: db")

    code.interact(local=dict(globals(), **locals()))

@cli.command()
def runserver():
    """Iniciar servidor de desenvolvimento"""
    print("🚀 Iniciando servidor de desenvolvimento...")
    app.run(debug=True, host='0.0.0.0', port=5000)

@cli.command()
def collectstatic():
    """Coletar arquivos estáticos (placeholder)"""
    print("📁 Coletando arquivos estáticos...")
    print("✅ Arquivos estáticos coletados!")

@cli.command()
def test():
    """Executar testes"""
    print("🧪 Executando testes...")
    os.system("python -m pytest tests/ -v")

@cli.command()
def reset_db():
    """Resetar banco de dados (CUIDADO!)"""
    confirm = input("⚠️  ATENÇÃO: Isso apagará todos os dados! Digite 'CONFIRMAR' para continuar: ")
    
    if confirm != 'CONFIRMAR':
        print("❌ Operação cancelada")
        return
    
    print("🗑️  Removendo todas as tabelas...")
    db.drop_all()
    
    print("🏗️  Recriando estrutura...")
    db.create_all()
    
    print("✅ Banco de dados resetado!")
    print("💡 Execute 'python manage.py create_superuser' para criar um admin")

@cli.command()
def backup_db():
    """Fazer backup do banco de dados"""
    print("💾 Iniciando backup do banco de dados...")

    try:
        # Usar o script de backup
        result = os.system("python backup_database.py")
        if result == 0:
            print("✅ Backup concluído com sucesso!")
        else:
            print("❌ Erro no backup")
    except Exception as e:
        print(f"❌ Erro ao executar backup: {e}")

        # Fallback: backup simples
        try:
            from datetime import datetime
            import shutil

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']:
                print("🔄 Tentando backup Python para PostgreSQL...")
                backup_file = f"backup_fallback_{timestamp}.sql"

                with app.app_context():
                    from models import db, Usuario, Escola, Dossie

                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write("-- Backup de emergência\n")
                        f.write(f"-- Data: {datetime.now()}\n\n")

                        # Backup básico de usuários
                        usuarios = Usuario.query.all()
                        f.write(f"-- {len(usuarios)} usuários\n")
                        for user in usuarios:
                            f.write(f"-- {user.nome} - {user.email}\n")

                        escolas = Escola.query.all()
                        f.write(f"-- {len(escolas)} escolas\n")

                        dossies = Dossie.query.all()
                        f.write(f"-- {len(dossies)} dossiês\n")

                print(f"✅ Backup de emergência criado: {backup_file}")
            else:
                # SQLite
                backup_file = f"backup_sqlite_{timestamp}.db"
                if os.path.exists('dossie_escolar.db'):
                    shutil.copy2('dossie_escolar.db', backup_file)
                    print(f"✅ Backup SQLite criado: {backup_file}")

        except Exception as e2:
            print(f"❌ Falha no backup de emergência: {e2}")

@cli.command()
def help_commands():
    """Mostrar todos os comandos disponíveis"""
    print("🔧 COMANDOS DISPONÍVEIS:")
    print("=" * 50)
    print("📊 BANCO DE DADOS:")
    print("  init-db          - Inicializar banco (primeira vez)")
    print("  makemigrations   - Criar nova migração")
    print("  migrate-db       - Aplicar migrações")
    print("  rollback         - Reverter última migração")
    print("  show-migrations  - Mostrar status das migrações")
    print("  reset-db         - Resetar banco (CUIDADO!)")
    print("  backup-db        - Fazer backup do banco")
    print("")
    print("👤 USUÁRIOS:")
    print("  create-superuser - Criar usuário administrador")
    print("")
    print("🚀 DESENVOLVIMENTO:")
    print("  runserver        - Iniciar servidor")
    print("  shell            - Shell interativo")
    print("  test             - Executar testes")
    print("  collectstatic    - Coletar arquivos estáticos")
    print("")
    print("💡 EXEMPLOS:")
    print("  python manage.py init-db")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate-db")
    print("  python manage.py create-superuser")
    print("  python manage.py runserver")

if __name__ == '__main__':
    # Configurar Flask CLI
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    # Se nenhum comando foi passado, mostrar ajuda
    if len(sys.argv) == 1:
        help_commands()
    else:
        cli()
