#!/bin/bash
# Script para corrigir persistência de arquivos estáticos

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
echo "║    📁 CORREÇÃO DE PERSISTÊNCIA DE ARQUIVOS                   ║"
echo "║    🔧 Volumes Docker + Arquivos Estáticos                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🚀 Iniciando correção de persistência de arquivos..."

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ] || [ ! -f "Dockerfile" ]; then
    error "❌ Arquivos Docker não encontrados! Execute no diretório correto."
fi

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1; then
    error "❌ Docker não está rodando!"
fi

# Backup das fotos existentes
log "📸 Criando backup das fotos existentes..."
if docker ps | grep -q dossie-app; then
    CONTAINER_ID=$(docker ps | grep dossie-app | awk '{print $1}')
    
    # Criar backup das fotos
    docker exec -it $CONTAINER_ID tar -czf /tmp/fotos_backup.tar.gz /app/static/uploads/fotos 2>/dev/null || true
    
    # Copiar backup para host
    docker cp $CONTAINER_ID:/tmp/fotos_backup.tar.gz ./fotos_backup_$(date +%Y%m%d_%H%M%S).tar.gz 2>/dev/null || true
    
    log "✅ Backup criado: fotos_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
else
    warn "⚠️ Container não está rodando, pulando backup"
fi

# Parar containers
log "🛑 Parando containers..."
docker-compose down

# Verificar volumes existentes
log "📊 Verificando volumes existentes..."
docker volume ls | grep -E "(app_uploads|app_logs|app_static)" || warn "⚠️ Nenhum volume encontrado"

# Criar volumes se não existirem
log "🔧 Criando volumes necessários..."
docker volume create app_uploads 2>/dev/null || log "✅ Volume app_uploads já existe"
docker volume create app_logs 2>/dev/null || log "✅ Volume app_logs já existe"
docker volume create app_static 2>/dev/null || log "✅ Volume app_static já existe"

# Reconstruir imagem
log "🔨 Reconstruindo imagem Docker..."
docker-compose build --no-cache

# Iniciar containers
log "🚀 Iniciando containers com nova configuração..."
docker-compose up -d

# Aguardar inicialização
log "⏳ Aguardando containers inicializarem..."
sleep 30

# Verificar status
log "📋 Verificando status dos containers..."
docker-compose ps

# Verificar volumes montados
log "🔍 Verificando montagem de volumes..."
CONTAINER_ID=$(docker ps | grep dossie-app | awk '{print $1}')
if [ ! -z "$CONTAINER_ID" ]; then
    docker inspect $CONTAINER_ID | grep -A 10 "Mounts" || warn "⚠️ Não foi possível verificar mounts"
fi

# Restaurar fotos se backup existe
if [ -f "./fotos_backup_*.tar.gz" ]; then
    log "📸 Restaurando fotos do backup..."
    BACKUP_FILE=$(ls -t fotos_backup_*.tar.gz | head -1)
    if [ ! -z "$BACKUP_FILE" ]; then
        docker cp $BACKUP_FILE $CONTAINER_ID:/tmp/
        docker exec -it $CONTAINER_ID tar -xzf /tmp/$BACKUP_FILE -C / 2>/dev/null || warn "⚠️ Erro ao restaurar backup"
        log "✅ Fotos restauradas do backup"
    fi
fi

# Verificar diretórios de uploads
log "📁 Verificando diretórios de uploads..."
docker exec -it $CONTAINER_ID ls -la /app/static/uploads/ 2>/dev/null || warn "⚠️ Erro ao verificar diretórios"

# Verificar permissões
log "🔐 Verificando permissões..."
docker exec -it $CONTAINER_ID ls -la /app/static/uploads/fotos/ 2>/dev/null || warn "⚠️ Erro ao verificar permissões"

# Teste de funcionamento
log "🧪 Testando funcionamento..."
if curl -f -s http://localhost:8000 > /dev/null 2>&1; then
    log "✅ Aplicação acessível via web"
else
    warn "⚠️ Aplicação pode não estar acessível ainda"
fi

# Status final
log "📊 Status dos volumes:"
docker volume ls | grep -E "(app_uploads|app_logs|app_static)"

log "📊 Status dos containers:"
docker-compose ps

log "✅ Correção de persistência concluída!"
echo ""
log "🌐 URLs de Acesso:"
log "   📱 Sistema: http://localhost:8000"
log "   📊 Logs: docker-compose logs -f dossie-app"
echo ""
log "📋 IMPORTANTE:"
log "   1. As fotos agora são persistidas em volumes Docker"
log "   2. Os arquivos sobreviverão a restarts do container"
log "   3. Backup das fotos foi criado automaticamente"
echo ""

# Verificar se há fotos restauradas
if docker exec -it $CONTAINER_ID ls /app/static/uploads/fotos/ 2>/dev/null | grep -q "\.jpg\|\.png\|\.gif"; then
    log "🎉 Fotos restauradas com sucesso!"
else
    warn "⚠️ Nenhuma foto encontrada - pode ser normal se não havia fotos antes"
fi

log "🎯 Próximos passos:"
log "   1. Teste fazer upload de uma nova foto"
log "   2. Reinicie o container: docker-compose restart dossie-app"
log "   3. Verifique se a foto ainda aparece" 