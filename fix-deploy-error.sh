#!/bin/bash
# Script para corrigir erro de deploy - "no image specified"

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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
echo "║    🔧 CORREÇÃO DE ERRO DE DEPLOY                             ║"
echo "║    ❌ Erro: no image specified                               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🔧 Corrigindo erro de deploy..."

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.app.yml" ]; then
    error "❌ Arquivo docker-compose.app.yml não encontrado!
    
Execute este script no diretório /var/www/dossie_escolar"
fi

# Parar serviços que podem estar com problema
log "🛑 Parando serviços com problema..."
docker stack rm dossie 2>/dev/null || true

log "⏳ Aguardando serviços pararem..."
sleep 10

# Limpar imagens problemáticas
log "🧹 Limpando imagens problemáticas..."
docker image prune -f

# Fazer build da aplicação
log "🏗️ Fazendo build da aplicação..."
if [ ! -f "Dockerfile" ]; then
    error "❌ Dockerfile não encontrado!"
fi

docker build -t dossie-app:latest . || error "❌ Falha no build da aplicação"

# Verificar se a imagem foi criada
if ! docker images | grep -q "dossie-app.*latest"; then
    error "❌ Imagem dossie-app:latest não foi criada"
fi

log "✅ Imagem dossie-app:latest criada com sucesso"

# Verificar arquivo docker-compose.app.yml
log "🔍 Verificando docker-compose.app.yml..."

if grep -q "build:" docker-compose.app.yml; then
    warn "⚠️ Arquivo ainda tem 'build:' em vez de 'image:'"
    log "🔧 Corrigindo docker-compose.app.yml..."
    
    # Fazer backup
    cp docker-compose.app.yml docker-compose.app.yml.backup
    
    # Corrigir arquivo
    sed -i 's/build: \./image: dossie-app:latest/' docker-compose.app.yml
    
    log "✅ docker-compose.app.yml corrigido"
fi

# Verificar se a correção foi aplicada
if grep -q "image: dossie-app:latest" docker-compose.app.yml; then
    log "✅ docker-compose.app.yml está correto"
else
    error "❌ docker-compose.app.yml ainda não está correto"
fi

# Fazer deploy da aplicação
log "🚀 Fazendo deploy da aplicação corrigida..."
docker stack deploy -c docker-compose.app.yml dossie

log "⏳ Aguardando serviços inicializarem..."
sleep 30

# Verificar status
log "📊 Verificando status dos serviços..."
docker service ls

# Verificar se aplicação está rodando
APP_RUNNING=$(docker service ls | grep dossie_dossie-app | grep -c "1/1" || echo "0")

if [ "$APP_RUNNING" -eq "1" ]; then
    log "✅ Aplicação está rodando!"
    
    # Testar aplicação
    log "🌐 Testando aplicação..."
    sleep 10
    
    if curl -f -s http://localhost:5000 > /dev/null 2>&1; then
        log "✅ Aplicação está respondendo!"
    else
        warn "⚠️ Aplicação pode não estar respondendo ainda"
    fi
else
    warn "⚠️ Aplicação pode não estar rodando corretamente"
    
    log "📋 Verificando logs..."
    docker service logs dossie_dossie-app --tail 20
fi

log "✅ Correção concluída!"
echo ""
log "🌐 URLs de Acesso:"
log "   📱 Sistema: http://10.0.1.185"
log "   📱 Direto: http://10.0.1.185:5000"
echo ""
log "🔧 Comandos úteis:"
log "   📊 Status: docker service ls"
log "   📋 Logs: docker service logs dossie_dossie-app --tail 50"
log "   🔄 Restart: docker service update --force dossie_dossie-app"
echo ""

if [ "$APP_RUNNING" -eq "1" ]; then
    log "🎉 Erro corrigido com sucesso!"
else
    warn "⚠️ Pode ser necessário verificar logs para mais detalhes"
fi
