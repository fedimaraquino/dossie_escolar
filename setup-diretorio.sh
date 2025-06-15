#!/bin/bash
# Script para configurar diretório correto da aplicação

set -e

# Cores
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

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    📁 CONFIGURAÇÃO DO DIRETÓRIO DA APLICAÇÃO                 ║"
echo "║    🎯 Diretório: /var/www/dossie_escolar                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🔧 Configurando diretório da aplicação..."

# Verificar se está rodando como root ou com sudo
if [[ $EUID -eq 0 ]]; then
    warn "Executando como root. Criando diretório e ajustando permissões..."
    
    # Criar diretório
    mkdir -p /var/www/dossie_escolar
    
    # Descobrir usuário real (se executado com sudo)
    if [ -n "$SUDO_USER" ]; then
        REAL_USER=$SUDO_USER
        REAL_GROUP=$(id -gn $SUDO_USER)
    else
        REAL_USER="www-data"
        REAL_GROUP="www-data"
    fi
    
    # Ajustar permissões
    chown -R $REAL_USER:$REAL_GROUP /var/www/dossie_escolar
    chmod -R 755 /var/www/dossie_escolar
    
    log "✅ Diretório criado: /var/www/dossie_escolar"
    log "✅ Proprietário: $REAL_USER:$REAL_GROUP"
    
else
    # Executando como usuário normal
    if [ -d "/var/www/dossie_escolar" ]; then
        if [ -w "/var/www/dossie_escolar" ]; then
            log "✅ Diretório /var/www/dossie_escolar já existe e é gravável"
        else
            warn "❌ Diretório existe mas não é gravável"
            info "💡 Execute: sudo chown -R $USER:$USER /var/www/dossie_escolar"
            exit 1
        fi
    else
        warn "❌ Diretório /var/www/dossie_escolar não existe"
        info "💡 Execute: sudo mkdir -p /var/www/dossie_escolar && sudo chown -R $USER:$USER /var/www/dossie_escolar"
        exit 1
    fi
fi

# Criar subdiretórios necessários
log "📁 Criando subdiretórios..."
cd /var/www/dossie_escolar

mkdir -p {traefik/data,backups,static/uploads,logs}

# Configurar permissões específicas
chmod 600 traefik/data/acme.json 2>/dev/null || touch traefik/data/acme.json && chmod 600 traefik/data/acme.json

log "✅ Subdiretórios criados"

# Verificar se arquivos da aplicação existem
log "🔍 Verificando arquivos da aplicação..."

REQUIRED_FILES=(
    "app.py"
    "requirements.txt"
    "docker-compose.app.yml"
    "docker-compose.traefik.yml"
    "docker-compose.portainer.yml"
    "docker-compose.postgres.yml"
    "Dockerfile"
    "deploy.sh"
)

MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    log "✅ Todos os arquivos necessários estão presentes"
else
    warn "⚠️ Arquivos faltando:"
    for file in "${MISSING_FILES[@]}"; do
        warn "   - $file"
    done
    echo ""
    info "💡 Transfira os arquivos da aplicação para /var/www/dossie_escolar"
    info "💡 Exemplo: rsync -avz /origem/ usuario@servidor:/var/www/dossie_escolar/"
fi

# Verificar permissões dos scripts
log "🔧 Verificando permissões dos scripts..."

SCRIPTS=("deploy.sh" "backup.sh" "monitor.sh")

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            log "✅ $script tem permissão de execução"
        else
            chmod +x "$script"
            log "✅ Permissão de execução adicionada a $script"
        fi
    else
        warn "⚠️ Script $script não encontrado"
    fi
done

# Verificar arquivo de configuração
log "⚙️ Verificando configuração..."

if [ -f "env-servidor-local" ]; then
    if [ ! -f ".env" ]; then
        cp env-servidor-local .env
        log "✅ Arquivo .env criado a partir de env-servidor-local"
    else
        log "✅ Arquivo .env já existe"
    fi
else
    warn "⚠️ Arquivo env-servidor-local não encontrado"
fi

# Verificar Docker
log "🐳 Verificando Docker..."

if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        log "✅ Docker está rodando"
        
        if docker info | grep -q "Swarm: active"; then
            log "✅ Docker Swarm está ativo"
        else
            warn "⚠️ Docker Swarm não está ativo"
            info "💡 Execute: docker swarm init --advertise-addr 10.0.1.185"
        fi
    else
        warn "⚠️ Docker não está rodando"
        info "💡 Execute: sudo systemctl start docker"
    fi
else
    warn "⚠️ Docker não está instalado"
    info "💡 Execute: curl -fsSL https://get.docker.com | sh"
fi

# Resumo final
echo ""
log "📊 RESUMO DA CONFIGURAÇÃO:"
log "   📁 Diretório: /var/www/dossie_escolar"
log "   👤 Proprietário: $(stat -c '%U:%G' /var/www/dossie_escolar)"
log "   📝 Permissões: $(stat -c '%a' /var/www/dossie_escolar)"
log "   📦 Arquivos: $((${#REQUIRED_FILES[@]} - ${#MISSING_FILES[@]}))/${#REQUIRED_FILES[@]} presentes"

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo ""
    log "🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
    log ""
    log "🚀 PRÓXIMOS PASSOS:"
    log "   1. cd /var/www/dossie_escolar"
    log "   2. ./deploy.sh"
    log "   3. Acessar: http://10.0.1.185"
else
    echo ""
    warn "⚠️ CONFIGURAÇÃO INCOMPLETA"
    warn "📋 Transfira os arquivos faltando antes de continuar"
fi

echo ""
info "📁 Diretório configurado: /var/www/dossie_escolar"
