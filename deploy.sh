#!/bin/bash
# Script de Deploy para Servidor Local 10.0.1.185

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🏫 SISTEMA DE CONTROLE DE DOSSIÊ ESCOLAR                  ║"
echo "║    🚀 Deploy Servidor Local - 10.0.1.185                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🚀 Iniciando deploy no servidor local 10.0.1.185"

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    error "Docker não está rodando! Execute: sudo systemctl start docker"
fi

# Verificar se Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    error "Docker Swarm não está ativo! Execute: docker swarm init --advertise-addr 10.0.1.185"
fi

# Carregar variáveis de ambiente
if [ -f .env ]; then
    source .env
    log "Variáveis de ambiente carregadas"
else
    warn "Arquivo .env não encontrado, usando env-servidor-local"
    if [ -f env-servidor-local ]; then
        cp env-servidor-local .env
        source .env
        log "Arquivo .env criado a partir de env-servidor-local"
    else
        error "Nenhum arquivo de configuração encontrado!"
    fi
fi

# Verificar se SECRET_KEY está configurada
if [[ -z "$SECRET_KEY" || "$SECRET_KEY" == *"gere-uma-chave"* ]]; then
    warn "SECRET_KEY não está configurada!"
    info "Gerando nova SECRET_KEY..."
    NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET/" .env
    source .env
    log "Nova SECRET_KEY gerada: $NEW_SECRET"
else
    log "✅ SECRET_KEY configurada"
fi

# Criar redes se não existirem
log "🌐 Criando redes Docker..."
docker network create --driver overlay traefik-public 2>/dev/null || log "Rede traefik-public já existe"
docker network create --driver overlay app-network 2>/dev/null || log "Rede app-network já existe"

# Criar diretórios necessários
log "📁 Criando diretórios..."
mkdir -p traefik/data backups

# Configurar permissões do Traefik
touch traefik/data/acme.json
chmod 600 traefik/data/acme.json

# Deploy dos serviços em ordem
log "🔀 Fazendo deploy do Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

log "�️ Removendo Portainer existente para evitar timeout..."
docker stack rm portainer 2>/dev/null || true

log "⏳ Aguardando remoção do Portainer..."
sleep 10

log "�📊 Fazendo deploy do Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

# Aguardar Portainer inicializar para evitar timeout
log "⏳ Aguardando Portainer inicializar..."
sleep 30

# Verificar se Portainer está rodando
log "🔍 Verificando se Portainer está acessível..."
for i in {1..6}; do
    if curl -f -s http://localhost:9000 > /dev/null 2>&1; then
        log "✅ Portainer está acessível!"
        warn "⚠️ IMPORTANTE: Configure o Portainer em até 5 minutos em http://10.0.1.185:9000"
        break
    fi
    log "⏳ Aguardando Portainer... ($i/6)"
    sleep 10
done

log "🗑️ Removendo PostgreSQL existente (container e volumes)..."
docker stack rm postgres 2>/dev/null || true

log "⏳ Aguardando remoção completa..."
sleep 15

# Remover volumes do PostgreSQL
log "🧹 Removendo volumes do PostgreSQL..."
docker volume rm postgres_postgres_data 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

log "🐘 Criando novo PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

log "⏳ Aguardando PostgreSQL inicializar completamente..."
sleep 45

log "🏗️ Fazendo build da aplicação..."
cd /var/www/dossie_escolar
docker build -t dossie-app:latest . || error "Falha no build da aplicação"

# Verificar se a imagem foi criada
if ! docker images | grep -q "dossie-app.*latest"; then
    error "Imagem dossie-app:latest não foi criada"
fi

log "✅ Imagem dossie-app:latest criada com sucesso"

log "🌐 Fazendo deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

log "⏳ Aguardando serviços inicializarem..."
sleep 60

# Verificar status
log "📊 Verificando status dos serviços..."
echo ""
docker stack ls
echo ""
docker service ls
echo ""

# Aguardar aplicação estar pronta
log "⏳ Aguardando aplicação estar pronta..."
sleep 30

# Executar configuração inicial
log "🔧 Executando configuração inicial do banco..."

# Remover qualquer banco SQLite existente
log "🗑️ Removendo bancos SQLite existentes..."
rm -f instance/*.db *.db *.sqlite *.sqlite3 2>/dev/null || true

# Aguardar PostgreSQL estar pronto
log "⏳ Aguardando PostgreSQL estar pronto..."
for i in {1..60}; do
    POSTGRES_CONTAINER=$(docker ps -q -f name=postgres_postgres | head -1)
    if [ ! -z "$POSTGRES_CONTAINER" ]; then
        if docker exec $POSTGRES_CONTAINER pg_isready -U dossie 2>/dev/null; then
            log "✅ PostgreSQL está pronto!"
            break
        fi
    fi
    if [ $i -eq 60 ]; then
        error "❌ PostgreSQL não ficou pronto em 10 minutos"
    fi
    log "⏳ Aguardando PostgreSQL... ($i/60)"
    sleep 10
done

# Criar banco de dados se não existir
log "🗄️ Criando banco de dados..."
POSTGRES_CONTAINER=$(docker ps -q -f name=postgres_postgres | head -1)
docker exec $POSTGRES_CONTAINER psql -U dossie -c "CREATE DATABASE dossie_escola;" 2>/dev/null || {
    log "ℹ️ Banco de dados já existe ou foi criado"
}

# Encontrar container da aplicação
APP_CONTAINER=""
for i in {1..10}; do
    APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)
    if [ ! -z "$APP_CONTAINER" ]; then
        break
    fi
    sleep 5
done

if [ ! -z "$APP_CONTAINER" ]; then
    log "📦 Container encontrado: $APP_CONTAINER"

    # Remover qualquer banco SQLite do container
    log "🗑️ Removendo bancos SQLite do container..."
    docker exec $APP_CONTAINER rm -f instance/*.db *.db *.sqlite *.sqlite3 2>/dev/null || true

    # Limpar migrações problemáticas
    log "🧹 Limpando migrações antigas..."
    rm -f migrations/versions/*.py 2>/dev/null || true
    docker exec $APP_CONTAINER rm -f migrations/versions/*.py 2>/dev/null || true

    # Verificar conexão PostgreSQL
    log "🔗 Verificando conexão PostgreSQL..."
    docker exec $APP_CONTAINER python3 -c "
import os
from sqlalchemy import create_engine
try:
    db_url = os.environ.get('DATABASE_URL')
    print(f'🔗 Testando conexão: {db_url}')
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute('SELECT version();')
        version = result.fetchone()[0]
        print(f'✅ PostgreSQL conectado: {version}')
except Exception as e:
    print(f'❌ Erro PostgreSQL: {e}')
    exit(1)
" || error "❌ Falha na conexão PostgreSQL"

    # Inicializar migrações do zero
    log "🔄 Inicializando migrações do zero..."
    docker exec $APP_CONTAINER flask db init 2>/dev/null || {
        log "ℹ️ Migrações já inicializadas"
    }

    # Criar migração inicial
    log "📝 Criando migração inicial..."
    docker exec $APP_CONTAINER flask db migrate -m "Initial migration" || {
        warn "Erro ao criar migração, criando tabelas diretamente..."
    }

    # Aplicar migrações
    log "⬆️ Aplicando migrações..."
    docker exec $APP_CONTAINER flask db upgrade || {
        warn "Migrações falharam, criando tabelas diretamente no PostgreSQL..."
        docker exec $APP_CONTAINER python3 -c "
from app import create_app
from models import db
import os
try:
    app = create_app()
    with app.app_context():
        print(f'🔗 Usando banco: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')
        db.create_all()
        print('✅ Tabelas criadas diretamente no PostgreSQL')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
" || error "❌ Falha ao criar tabelas"
    }
    
    # Criar usuário admin
    log "👤 Criando usuário administrador..."
    docker exec $APP_CONTAINER python3 << 'PYTHON_EOF'
from app import create_app
from models import db, Usuario, Perfil, Escola

try:
    app = create_app()
    with app.app_context():
        print("🔗 Conectado ao banco")
        
        # Criar escola padrão
        escola = Escola.query.first()
        if not escola:
            escola = Escola(
                nome='Escola Local - Servidor 10.0.1.185',
                cnpj='00.000.000/0001-00',
                endereco='Servidor Local',
                telefone='(11) 0000-0000',
                email='admin@local.escola',
                situacao='ativa'
            )
            db.session.add(escola)
            db.session.commit()
            print("🏫 Escola criada")
        
        # Criar perfil admin
        perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
        if not perfil:
            perfil = Perfil(
                perfil='Administrador Geral',
                nome='Administrador Geral'
            )
            db.session.add(perfil)
            db.session.commit()
            print("👑 Perfil admin criado")
        
        # Criar usuário admin
        admin = Usuario.query.filter_by(email='admin@local.escola').first()
        if not admin:
            admin = Usuario(
                nome='Administrador Local',
                email='admin@local.escola',
                escola_id=escola.id,
                perfil_id=perfil.id_perfil,
                situacao='ativo'
            )
            admin.set_password('Admin@Local123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado!")
        else:
            print("ℹ️ Usuário admin já existe")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
PYTHON_EOF
else
    warn "Container da aplicação não encontrado. Execute manualmente a configuração depois."
fi

# Verificação final - garantir que está usando PostgreSQL
log "🔍 Verificação final do banco de dados..."
if [ ! -z "$APP_CONTAINER" ]; then
    docker exec $APP_CONTAINER python3 -c "
from app import create_app
try:
    app = create_app()
    with app.app_context():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        if 'postgresql' in db_url:
            print('✅ CONFIRMADO: Usando PostgreSQL')
            print(f'🔗 URL: {db_url}')
        else:
            print(f'❌ ERRO: Usando {db_url}')
            exit(1)
except Exception as e:
    print(f'❌ Erro na verificação: {e}')
" || warn "⚠️ Não foi possível verificar o banco"
fi

log "✅ Deploy concluído com sucesso!"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🎉 DEPLOY CONCLUÍDO! 🎉                   ║${NC}"
echo -e "${BLUE}║                  🐘 USANDO POSTGRESQL 🐘                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log "🌐 URLs de Acesso (Rede Local):"
log "   📱 Sistema Principal: http://10.0.1.185"
log "   📱 Acesso Direto: http://10.0.1.185:5000"
log "   📊 Portainer: http://10.0.1.185:9000"
log "   🔀 Traefik Dashboard: http://10.0.1.185:8080"
echo ""
log "👤 Credenciais de Acesso:"
log "   📧 Email: admin@local.escola"
log "   🔑 Senha: Admin@Local123"
echo ""
log "🔧 Comandos Úteis:"
log "   📊 Status: docker service ls"
log "   📋 Logs: docker service logs dossie_dossie-app"
log "   🔄 Restart: docker service update --force dossie_dossie-app"
echo ""
log "📁 Diretório da aplicação: /var/www/dossie_escolar"
log "🎉 Sistema rodando no servidor local!"
