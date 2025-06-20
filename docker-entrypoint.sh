#!/bin/bash
set -e

# Esperar o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL está pronto!"

# Criar todas as tabelas automaticamente
echo "Criando tabelas do banco de dados..."
python -c "
import traceback
from app import create_app
from models import db
from models.perfil import Perfil
from models.permissao import Permissao, PerfilPermissao
from models.cidade import Cidade
from models.escola import Escola, ConfiguracaoEscola, CONFIGURACOES_PADRAO
from models.usuario import Usuario
from models.diretor import Diretor
from models.dossie import Dossie
from models.movimentacao import Movimentacao
from models.anexo import Anexo
from models.solicitante import Solicitante
from models.log_auditoria import LogAuditoria, LogSistema
from models.configuracao_avancada import ConfiguracaoSistema, HistoricoConfiguracao

try:
    app = create_app()
    with app.app_context():
        print('🔗 Conectado ao banco de dados')
        
        # Criar todas as tabelas
        print('📋 Criando tabelas...')
        db.create_all()
        print('✅ Tabelas criadas com sucesso!')
        
        # Criar escola padrão se não existir
        print('🏫 Verificando escola...')
        escola = Escola.query.first()
        if not escola:
            print('🏫 Criando escola padrão...')
            escola = Escola(
                nome='Escola Padrão',
                cnpj='00.000.000/0001-00',
                endereco='Endereço da Escola',
                telefone='(00) 0000-0000',
                email='contato@escola.com',
                uf='SP',
                situacao='ativa'
            )
            db.session.add(escola)
            db.session.commit()
            print(f'✅ Escola padrão criada com ID: {escola.id}')
        else:
            print(f'ℹ️ Escola já existe: {escola.nome} (ID: {escola.id})')
        
        # Criar perfil de administrador se não existir
        print('👑 Verificando perfil admin...')
        admin_perfil = Perfil.query.filter_by(perfil='Administrador').first()
        if not admin_perfil:
            print('👑 Criando perfil administrador...')
            admin_perfil = Perfil(
                perfil='Administrador',
                descricao='Perfil com acesso total ao sistema'
            )
            db.session.add(admin_perfil)
            db.session.commit()
            print(f'✅ Perfil de administrador criado com ID: {admin_perfil.id_perfil}')
        else:
            print(f'ℹ️ Perfil admin já existe: {admin_perfil.perfil} (ID: {admin_perfil.id_perfil})')
        
        # Criar usuário admin se não existir
        print('👤 Verificando usuário admin...')
        admin = Usuario.query.filter_by(email='admin@sistema.com').first()
        if not admin:
            print('👤 Criando usuário administrador...')
            print(f'   Escola ID: {escola.id}')
            print(f'   Perfil ID: {admin_perfil.id_perfil}')
            
            admin = Usuario(
                nome='Administrador do Sistema',
                email='admin@sistema.com',
                escola_id=escola.id,
                perfil_id=admin_perfil.id_perfil,
                situacao='ativo',
                status='ativo'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Usuário admin criado com sucesso!')
            print('📧 Credenciais: admin@sistema.com / Admin@123')
        else:
            print('ℹ️ Usuário admin já existe')
        
        print('🎉 Banco de dados inicializado com sucesso!')
        
except Exception as e:
    print(f'❌ Erro durante inicialização: {e}')
    print('📋 Traceback completo:')
    traceback.print_exc()
    exit(1)
"

# Iniciar a aplicação
echo "Iniciando aplicação..."
exec gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 --access-logfile - --error-logfile - app:app 