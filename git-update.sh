#!/bin/bash
# Script de Atualização via Git - Sistema de Dossiê Escolar
# Repositório: https://github.com/fedimaraquino/dossie_escolar.git

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Configurações
APP_DIR="/var/www/dossie_escolar"
BRANCH="main"

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🔄 ATUALIZAÇÃO VIA GIT                                    ║"
echo "║    📦 Repositório: fedimaraquino/dossie_escolar              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🔄 Iniciando atualização via Git..."

# Verificar se diretório existe
if [ ! -d "$APP_DIR" ]; then
    error "❌ Diretório $APP_DIR não encontrado! Execute git-deploy.sh primeiro"
fi

# Ir para o diretório
cd "$APP_DIR"

# Verificar se é um repositório Git
if [ ! -d ".git" ]; then
    error "❌ Não é um repositório Git! Execute git-deploy.sh primeiro"
fi

# Verificar status atual
log "📋 Status atual do repositório:"
git status --porcelain

# Verificar se há mudanças locais
if ! git diff --quiet || ! git diff --cached --quiet; then
    warn "⚠️ Há mudanças locais não commitadas:"
    git status --short
    echo ""
    read -p "Deseja descartar as mudanças locais? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git reset --hard HEAD
        git clean -fd
        log "🧹 Mudanças locais descartadas"
    else
        error "❌ Atualização cancelada. Commit ou descarte as mudanças primeiro"
    fi
fi

# Mostrar commit atual
log "📋 Commit atual:"
git log --oneline -1

# Fazer fetch para verificar atualizações
log "📥 Verificando atualizações no repositório..."
git fetch origin

# Verificar se há atualizações
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    log "✅ Repositório já está atualizado!"
    log "📋 Commit atual: $(git log --oneline -1)"
    exit 0
fi

# Mostrar mudanças que serão aplicadas
log "📋 Mudanças que serão aplicadas:"
git log --oneline $LOCAL_COMMIT..$REMOTE_COMMIT

echo ""
read -p "Deseja aplicar essas atualizações? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    log "❌ Atualização cancelada pelo usuário"
    exit 0
fi

# Fazer backup antes da atualização
log "💾 Fazendo backup antes da atualização..."
if [ -f "backup.sh" ]; then
    ./backup.sh
    log "✅ Backup realizado"
else
    warn "⚠️ Script de backup não encontrado"
fi

# Aplicar atualizações
log "📥 Aplicando atualizações do Git..."
git reset --hard origin/$BRANCH

# Mostrar novo commit
log "✅ Atualização aplicada!"
log "📋 Novo commit:"
git log --oneline -1

# Verificar se houve mudanças nos arquivos Docker
DOCKER_CHANGED=false
if git diff --name-only $LOCAL_COMMIT $REMOTE_COMMIT | grep -E "(Dockerfile|docker-compose|requirements\.txt)" > /dev/null; then
    DOCKER_CHANGED=true
    log "🐳 Detectadas mudanças nos arquivos Docker"
fi

# Verificar se houve mudanças no código Python
CODE_CHANGED=false
if git diff --name-only $LOCAL_COMMIT $REMOTE_COMMIT | grep -E "\.(py|html|css|js)$" > /dev/null; then
    CODE_CHANGED=true
    log "🐍 Detectadas mudanças no código da aplicação"
fi

# Atualizar configuração se necessário
if [ -f "env-servidor-local" ]; then
    if [ ! -f ".env" ] || [ "env-servidor-local" -nt ".env" ]; then
        log "⚙️ Atualizando configuração..."
        cp env-servidor-local .env
        source .env
        log "✅ Configuração atualizada"
    fi
fi

# Dar permissões aos scripts
chmod +x *.sh 2>/dev/null || true

# Rebuild e redeploy se necessário
if [ "$DOCKER_CHANGED" = true ]; then
    log "🏗️ Fazendo rebuild da aplicação (mudanças no Docker)..."
    docker build -t dossie-app:latest .
    
    log "🔄 Atualizando serviço da aplicação..."
    docker service update --image dossie-app:latest dossie_dossie-app
    
    log "⏳ Aguardando atualização..."
    sleep 30
    
elif [ "$CODE_CHANGED" = true ]; then
    log "🔄 Reiniciando aplicação (mudanças no código)..."
    docker service update --force dossie_dossie-app
    
    log "⏳ Aguardando reinicialização..."
    sleep 20
fi

# Verificar se há migrações pendentes
log "🔄 Verificando migrações do banco..."
APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)

if [ ! -z "$APP_CONTAINER" ]; then
    # Executar migrações se necessário
    docker exec $APP_CONTAINER flask db upgrade 2>/dev/null || {
        warn "⚠️ Erro ao executar migrações. Pode ser necessário intervenção manual."
    }
    log "✅ Migrações verificadas"
else
    warn "⚠️ Container da aplicação não encontrado"
fi

# Verificar status dos serviços
log "📊 Verificando status dos serviços..."
docker service ls

# Verificar se aplicação está respondendo
log "🌐 Testando aplicação..."
sleep 10

if curl -f -s http://10.0.1.185 > /dev/null; then
    log "✅ Aplicação está respondendo!"
else
    warn "⚠️ Aplicação pode não estar respondendo ainda. Aguarde alguns minutos."
fi

log "✅ Atualização concluída com sucesso!"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  🎉 ATUALIZAÇÃO CONCLUÍDA! 🎉                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log "🌐 Sistema atualizado e rodando em: http://10.0.1.185"
log "📋 Commit atual: $(git log --oneline -1)"
echo ""
log "🔧 Comandos úteis:"
log "   📊 Status: docker service ls"
log "   📋 Logs: docker service logs dossie_dossie-app --tail 50"
log "   🔄 Restart: docker service update --force dossie_dossie-app"
echo ""
log "🎉 Sistema atualizado via Git!"
