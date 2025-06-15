#!/bin/bash
# Script para corrigir timeout do Portainer

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
echo "║    📊 CORREÇÃO DO PORTAINER                                  ║"
echo "║    🔧 Timeout de Segurança                                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "📊 Corrigindo timeout do Portainer..."

# Verificar se arquivo existe
if [ ! -f "docker-compose.portainer.yml" ]; then
    error "❌ Arquivo docker-compose.portainer.yml não encontrado!"
fi

# Verificar se Portainer está rodando
if docker service ls | grep -q portainer_portainer; then
    log "📊 Portainer encontrado, reiniciando..."
    
    # Tentar restart simples primeiro
    log "🔄 Tentando restart simples..."
    docker service update --force portainer_portainer
    
    log "⏳ Aguardando reinicialização..."
    sleep 30
    
    # Verificar se está funcionando
    if curl -f -s http://localhost:9000 > /dev/null 2>&1; then
        log "✅ Portainer funcionando após restart!"
        log "🌐 Acesse: http://10.0.1.185:9000"
        exit 0
    else
        warn "⚠️ Restart simples não funcionou, recriando..."
    fi
else
    log "📊 Portainer não encontrado, criando..."
fi

# Remover Portainer completamente
log "🗑️ Removendo Portainer..."
docker stack rm portainer 2>/dev/null || true

# Aguardar remoção completa
log "⏳ Aguardando remoção completa..."
sleep 15

# Limpar volumes órfãos se necessário
log "🧹 Limpando volumes órfãos..."
docker volume prune -f 2>/dev/null || true

# Recriar Portainer
log "📊 Recriando Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

# Aguardar inicialização
log "⏳ Aguardando Portainer inicializar..."
sleep 45

# Verificar se está rodando
PORTAINER_RUNNING=false
for i in {1..12}; do
    if docker service ls | grep portainer_portainer | grep -q "1/1"; then
        PORTAINER_RUNNING=true
        break
    fi
    log "⏳ Aguardando Portainer... ($i/12)"
    sleep 10
done

if [ "$PORTAINER_RUNNING" = true ]; then
    log "✅ Portainer está rodando!"
    
    # Testar acesso web
    log "🌐 Testando acesso web..."
    sleep 10
    
    if curl -f -s http://localhost:9000 > /dev/null 2>&1; then
        log "✅ Portainer acessível via web!"
    else
        warn "⚠️ Portainer rodando mas pode não estar acessível ainda"
    fi
else
    warn "⚠️ Portainer pode não estar rodando corretamente"
    log "📋 Verificando logs..."
    docker service logs portainer_portainer --tail 10
fi

# Status final
log "📊 Status dos serviços:"
docker service ls

log "✅ Correção do Portainer concluída!"
echo ""
log "🌐 URLs de Acesso:"
log "   📊 Portainer: http://10.0.1.185:9000"
log "   📱 Sistema: http://10.0.1.185"
log "   🔀 Traefik: http://10.0.1.185:8080"
echo ""
log "📋 IMPORTANTE:"
log "   1. Acesse o Portainer em até 5 minutos"
log "   2. Crie o usuário admin na primeira tela"
log "   3. Escolha 'Docker Swarm' como ambiente"
echo ""

if [ "$PORTAINER_RUNNING" = true ]; then
    log "🎉 Portainer corrigido e funcionando!"
    info "👆 Acesse agora: http://10.0.1.185:9000"
else
    warn "⚠️ Pode ser necessário verificar logs para mais detalhes"
fi
