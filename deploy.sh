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

log "📊 Fazendo deploy do Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

log "🐘 Fazendo deploy do PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

log "⏳ Aguardando PostgreSQL inicializar..."
sleep 30

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

# Encontrar container da aplicação
APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)

if [ -z "$APP_CONTAINER" ]; then
    warn "Container da aplicação não encontrado ainda, aguardando..."
    sleep 30
    APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)
fi

if [ ! -z "$APP_CONTAINER" ]; then
    log "📦 Container encontrado: $APP_CONTAINER"
    
    # Executar migrações
    log "🔄 Executando migrações..."
    docker exec $APP_CONTAINER flask db upgrade || {
        warn "Tentando inicializar banco..."
        docker exec $APP_CONTAINER flask db init || true
        docker exec $APP_CONTAINER flask db migrate -m "Initial migration" || true
        docker exec $APP_CONTAINER flask db upgrade || true
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

log "✅ Deploy concluído com sucesso!"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🎉 DEPLOY CONCLUÍDO! 🎉                   ║${NC}"
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
