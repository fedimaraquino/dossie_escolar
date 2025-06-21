#!/bin/bash
set -e

# Esperar o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL está pronto!"

# Executar migrações do banco de dados
echo "Executando migrações do banco de dados..."

# Limpar problemas de migrações múltiplas
echo "Verificando estado das migrações..."

# Se há problemas com multiple heads, resetar
flask db heads 2>/dev/null | grep -q "Multiple head revisions" && {
    echo "⚠️ Detectado problema de múltiplas heads. Corrigindo..."
    
    # Marcar todas as migrações como aplicadas (força sinc)
    flask db stamp heads 2>/dev/null || {
        echo "Forçando reset das migrações..."
        # Se falhar, usar abordagem mais direta
        python -c "
from app import create_app
from flask_migrate import stamp
app = create_app()
with app.app_context():
    try:
        stamp(revision='heads')
        print('✅ Migrações sincronizadas')
    except:
        print('ℹ️ Usando criação direta de tabelas')
        from models import db
        db.create_all()
        stamp()
        print('✅ Banco inicializado')
" || echo "⚠️ Continuando com inicialização manual..."
    }
}

# Verificar se migrations existe, senão inicializar
if [ ! -d "migrations" ] || [ ! -f "migrations/alembic.ini" ]; then
    echo "📁 Inicializando estrutura de migrações..."
    rm -rf migrations 2>/dev/null || true
    flask db init
fi

# Aplicar migrações
echo "📋 Aplicando migrações..."
flask db upgrade 2>/dev/null || {
    echo "🔄 Primeira execução - criando migration inicial..."
    
    # Verificar se há tabelas no banco
    HAS_TABLES=$(python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print('1' if tables else '0')
" 2>/dev/null || echo "0")

    if [ "$HAS_TABLES" = "1" ]; then
        echo "📊 Banco já tem tabelas - sincronizando migrações..."
        flask db stamp head 2>/dev/null || {
            # Forçar marca como migrado
            python -c "
from app import create_app
from flask_migrate import stamp
app = create_app()
with app.app_context():
    stamp()
" 2>/dev/null || echo "⚠️ Continuando..."
        }
    else
        echo "🆕 Banco vazio - criando primeira migração..."
        flask db migrate -m "Initial migration" 2>/dev/null || {
            echo "📋 Criando tabelas diretamente..."
            python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
"
            flask db stamp head 2>/dev/null || echo "⚠️ Continuando sem stamp..."
        }
    fi
    
    # Tentar aplicar novamente
    flask db upgrade 2>/dev/null || echo "ℹ️ Migrações já aplicadas"
}

# Criar dados iniciais
echo "Verificando dados iniciais..."
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
        
        # Verificar se tabelas existem (migrações já aplicadas)
        print('📋 Verificando estrutura do banco...')
        
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
        admin_perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
        if not admin_perfil:
            print('👑 Criando perfil administrador...')
            admin_perfil = Perfil(
                perfil='Administrador Geral',
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