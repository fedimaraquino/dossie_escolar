#!/bin/bash
# Script de Backup Automático - Sistema de Dossiê Escolar

set -e

# Configurações
BACKUP_DIR="/var/www/dossie_escolar/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Criar diretório de backup
mkdir -p $BACKUP_DIR

log "💾 Iniciando backup do sistema..."

# Backup do banco de dados
log "🐘 Fazendo backup do PostgreSQL..."
POSTGRES_CONTAINER=$(docker ps -q -f name=postgres_postgres)

if [ ! -z "$POSTGRES_CONTAINER" ]; then
    docker exec $POSTGRES_CONTAINER pg_dump -U dossie dossie_escola > $BACKUP_DIR/db_$DATE.sql
    log "✅ Backup do banco salvo: db_$DATE.sql"
else
    warn "Container PostgreSQL não encontrado!"
fi

# Backup dos uploads
log "📁 Fazendo backup dos arquivos de upload..."
if docker volume ls | grep -q dossie_app_uploads; then
    docker run --rm \
        -v dossie_app_uploads:/data \
        -v $BACKUP_DIR:/backup \
        alpine tar czf /backup/uploads_$DATE.tar.gz -C /data .
    log "✅ Backup dos uploads salvo: uploads_$DATE.tar.gz"
else
    warn "Volume de uploads não encontrado!"
fi

# Backup das configurações
log "⚙️ Fazendo backup das configurações..."
cd /var/www/dossie_escolar
tar czf $BACKUP_DIR/config_$DATE.tar.gz \
    docker-compose.*.yml \
    .env \
    Dockerfile \
    deploy.sh \
    backup.sh 2>/dev/null || warn "Alguns arquivos de configuração não foram encontrados"

log "✅ Backup das configurações salvo: config_$DATE.tar.gz"

# Backup dos logs
log "📋 Fazendo backup dos logs..."
if docker volume ls | grep -q dossie_app_logs; then
    docker run --rm \
        -v dossie_app_logs:/data \
        -v $BACKUP_DIR:/backup \
        alpine tar czf /backup/logs_$DATE.tar.gz -C /data . 2>/dev/null || warn "Logs não encontrados"
    log "✅ Backup dos logs salvo: logs_$DATE.tar.gz"
fi

# Limpar backups antigos
log "🧹 Limpando backups antigos (mais de $RETENTION_DAYS dias)..."
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# Mostrar resumo
log "📊 Resumo do backup:"
ls -lh $BACKUP_DIR/*$DATE* 2>/dev/null || warn "Nenhum arquivo de backup criado hoje"

# Calcular espaço usado
BACKUP_SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)
log "💽 Espaço total usado pelos backups: $BACKUP_SIZE"

log "✅ Backup concluído com sucesso!"
log "📁 Localização: $BACKUP_DIR"

# Verificar espaço em disco
DISK_USAGE=$(df -h /opt | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    warn "⚠️ Espaço em disco baixo: ${DISK_USAGE}% usado"
    warn "💡 Considere limpar backups antigos ou aumentar espaço"
fi

log "🎉 Backup finalizado!"
