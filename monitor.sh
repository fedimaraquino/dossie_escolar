#!/bin/bash
# Script de Monitoramento - Sistema de Dossiê Escolar

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}$1${NC}"
}

warn() {
    echo -e "${YELLOW}$1${NC}"
}

error() {
    echo -e "${RED}$1${NC}"
}

info() {
    echo -e "${BLUE}$1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    📊 MONITORAMENTO DO SISTEMA DE DOSSIÊ ESCOLAR             ║"
echo "║    🌐 Servidor: 10.0.1.185                                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar Docker
info "🐳 STATUS DO DOCKER"
echo "==================="
if docker info > /dev/null 2>&1; then
    log "✅ Docker está rodando"
    if docker info | grep -q "Swarm: active"; then
        log "✅ Docker Swarm está ativo"
    else
        error "❌ Docker Swarm não está ativo"
    fi
else
    error "❌ Docker não está rodando"
    exit 1
fi

echo ""

# Status das Stacks
info "📦 STATUS DAS STACKS"
echo "===================="
docker stack ls

echo ""

# Status dos Serviços
info "🔧 STATUS DOS SERVIÇOS"
echo "======================"
docker service ls

echo ""

# Verificar saúde dos serviços
info "🏥 HEALTH CHECKS"
echo "================"

# Verificar Traefik
if curl -s http://10.0.1.185:8080/ping > /dev/null; then
    log "✅ Traefik está respondendo"
else
    error "❌ Traefik não está respondendo"
fi

# Verificar Portainer
if curl -s -I http://10.0.1.185:9000 | grep -q "200\|302"; then
    log "✅ Portainer está respondendo"
else
    error "❌ Portainer não está respondendo"
fi

# Verificar Aplicação
if curl -s -I http://10.0.1.185 | grep -q "200\|302"; then
    log "✅ Aplicação está respondendo"
else
    error "❌ Aplicação não está respondendo"
fi

# Verificar Aplicação Direta
if curl -s -I http://10.0.1.185:5000 | grep -q "200\|302"; then
    log "✅ Aplicação (porta 5000) está respondendo"
else
    error "❌ Aplicação (porta 5000) não está respondendo"
fi

echo ""

# Verificar PostgreSQL
info "🐘 STATUS DO POSTGRESQL"
echo "======================="
POSTGRES_CONTAINER=$(docker ps -q -f name=postgres_postgres)
if [ ! -z "$POSTGRES_CONTAINER" ]; then
    if docker exec $POSTGRES_CONTAINER pg_isready -U dossie > /dev/null 2>&1; then
        log "✅ PostgreSQL está respondendo"
        
        # Verificar conexão com banco
        if docker exec $POSTGRES_CONTAINER psql -U dossie -d dossie_escola -c "SELECT 1;" > /dev/null 2>&1; then
            log "✅ Banco de dados 'dossie_escola' acessível"
        else
            error "❌ Banco de dados 'dossie_escola' não acessível"
        fi
    else
        error "❌ PostgreSQL não está respondendo"
    fi
else
    error "❌ Container PostgreSQL não encontrado"
fi

echo ""

# Recursos do Sistema
info "💻 RECURSOS DO SISTEMA"
echo "======================"

# CPU e Memória
echo "🧠 Memória:"
free -h

echo ""
echo "💽 Espaço em Disco:"
df -h /opt

echo ""
echo "📊 Uso do Docker:"
docker system df

echo ""

# Top 5 containers por uso de CPU/Memória
info "🔝 TOP 5 CONTAINERS (CPU/MEMÓRIA)"
echo "=================================="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -6

echo ""

# Verificar logs recentes
info "📋 LOGS RECENTES"
echo "================"

echo "🌐 Últimos logs da aplicação:"
docker service logs dossie_dossie-app --tail 5 2>/dev/null || warn "Logs da aplicação não disponíveis"

echo ""
echo "🐘 Últimos logs do PostgreSQL:"
docker service logs postgres_postgres --tail 3 2>/dev/null || warn "Logs do PostgreSQL não disponíveis"

echo ""

# Verificar volumes
info "💾 VOLUMES DOCKER"
echo "================="
docker volume ls | grep dossie

echo ""

# Verificar redes
info "🌐 REDES DOCKER"
echo "==============="
docker network ls | grep -E "(traefik-public|app-network)"

echo ""

# Verificar conectividade de rede
info "🔗 CONECTIVIDADE DE REDE"
echo "========================"

# Ping para gateway
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
if ping -c 1 $GATEWAY > /dev/null 2>&1; then
    log "✅ Gateway ($GATEWAY) acessível"
else
    error "❌ Gateway ($GATEWAY) não acessível"
fi

# Verificar DNS
if nslookup google.com > /dev/null 2>&1; then
    log "✅ DNS funcionando"
else
    error "❌ DNS não funcionando"
fi

echo ""

# Verificar portas abertas
info "🚪 PORTAS ABERTAS"
echo "================="
netstat -tlnp | grep -E ":(80|443|5000|8080|9000) " | awk '{print $1, $4}' | sort

echo ""

# Resumo final
info "📊 RESUMO FINAL"
echo "==============="

# Contar serviços rodando
TOTAL_SERVICES=$(docker service ls --format "{{.Replicas}}" | wc -l)
RUNNING_SERVICES=$(docker service ls --format "{{.Replicas}}" | grep -c "/")

log "📦 Serviços: $RUNNING_SERVICES/$TOTAL_SERVICES rodando"

# Verificar se todos os serviços essenciais estão rodando
ESSENTIAL_SERVICES=("traefik_traefik" "portainer_portainer" "postgres_postgres" "dossie_dossie-app")
ALL_RUNNING=true

for service in "${ESSENTIAL_SERVICES[@]}"; do
    if docker service ls --format "{{.Name}}" | grep -q "^$service$"; then
        REPLICAS=$(docker service ls --filter name=$service --format "{{.Replicas}}")
        if [[ $REPLICAS == *"/"* ]]; then
            CURRENT=$(echo $REPLICAS | cut -d'/' -f1)
            DESIRED=$(echo $REPLICAS | cut -d'/' -f2)
            if [ "$CURRENT" = "$DESIRED" ] && [ "$CURRENT" != "0" ]; then
                log "✅ $service: $REPLICAS"
            else
                error "❌ $service: $REPLICAS"
                ALL_RUNNING=false
            fi
        else
            error "❌ $service: formato inválido ($REPLICAS)"
            ALL_RUNNING=false
        fi
    else
        error "❌ $service: não encontrado"
        ALL_RUNNING=false
    fi
done

echo ""

if $ALL_RUNNING; then
    log "🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!"
    log "🌐 Acesse: http://10.0.1.185"
else
    error "⚠️ ALGUNS SERVIÇOS APRESENTAM PROBLEMAS!"
    warn "💡 Execute: docker service ls para mais detalhes"
fi

echo ""
info "🕐 Monitoramento realizado em: $(date)"
echo ""
