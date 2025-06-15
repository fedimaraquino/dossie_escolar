#!/bin/bash
# Script para configurar SSH com GitHub

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
echo "║    🔑 CONFIGURAÇÃO SSH PARA GITHUB                           ║"
echo "║    📦 Repositório: fedimaraquino/dossie_escolar              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🔑 Configurando SSH para GitHub..."

# Verificar se SSH já está configurado
log "🔍 Verificando configuração SSH atual..."

if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    log "✅ SSH já está configurado corretamente!"
    log "📋 Testando acesso ao repositório..."
    
    if git ls-remote git@github.com:fedimaraquino/dossie_escolar.git &>/dev/null; then
        log "✅ Acesso ao repositório confirmado!"
        echo ""
        log "🎉 SSH está funcionando perfeitamente!"
        log "🚀 Você pode executar o deploy agora:"
        log "   curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash"
        exit 0
    else
        warn "⚠️ SSH configurado mas sem acesso ao repositório"
    fi
fi

# Verificar se já existe chave SSH
log "🔍 Verificando chaves SSH existentes..."

if [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    log "📋 Chaves SSH encontradas:"
    ls -la ~/.ssh/id_* 2>/dev/null || true
    echo ""
    
    # Mostrar chave pública
    if [ -f ~/.ssh/id_ed25519.pub ]; then
        log "🔑 Chave pública Ed25519:"
        cat ~/.ssh/id_ed25519.pub
    elif [ -f ~/.ssh/id_rsa.pub ]; then
        log "🔑 Chave pública RSA:"
        cat ~/.ssh/id_rsa.pub
    fi
    
    echo ""
    warn "⚠️ Chave SSH existe mas não está funcionando com GitHub"
    info "💡 Verifique se a chave foi adicionada no GitHub:"
    info "   1. Copie a chave pública acima"
    info "   2. Vá em: https://github.com/settings/ssh/new"
    info "   3. Cole a chave e salve"
    echo ""
    
    read -p "Chave já foi adicionada no GitHub? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "🔄 Testando novamente..."
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            log "✅ SSH funcionando agora!"
            exit 0
        else
            warn "❌ Ainda não está funcionando"
        fi
    fi
    
    read -p "Deseja gerar uma nova chave SSH? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "❌ Configuração cancelada"
        exit 1
    fi
fi

# Solicitar email
echo ""
read -p "📧 Digite seu email do GitHub: " EMAIL

if [ -z "$EMAIL" ]; then
    error "❌ Email é obrigatório!"
fi

# Gerar nova chave SSH
log "🔑 Gerando nova chave SSH Ed25519..."

ssh-keygen -t ed25519 -C "$EMAIL" -f ~/.ssh/id_ed25519 -N ""

if [ $? -ne 0 ]; then
    error "❌ Erro ao gerar chave SSH"
fi

log "✅ Chave SSH gerada com sucesso!"

# Iniciar ssh-agent
log "🔧 Configurando ssh-agent..."

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

if [ $? -ne 0 ]; then
    error "❌ Erro ao adicionar chave ao ssh-agent"
fi

log "✅ Chave adicionada ao ssh-agent!"

# Mostrar chave pública
echo ""
log "🔑 Sua chave pública SSH:"
echo ""
echo -e "${YELLOW}$(cat ~/.ssh/id_ed25519.pub)${NC}"
echo ""

# Instruções para adicionar no GitHub
log "📋 PRÓXIMOS PASSOS:"
echo ""
info "1. 📋 COPIE a chave pública acima (toda a linha)"
echo ""
info "2. 🌐 ABRA o GitHub no navegador:"
info "   https://github.com/settings/ssh/new"
echo ""
info "3. 📝 ADICIONE a chave:"
info "   - Title: Servidor $(hostname) - $(date +%Y-%m-%d)"
info "   - Key: Cole a chave pública copiada"
info "   - Clique em 'Add SSH key'"
echo ""

# Aguardar confirmação
read -p "✅ Chave adicionada no GitHub? Pressione ENTER para testar..."

# Testar conexão
log "🔄 Testando conexão SSH com GitHub..."

if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    log "✅ SSH configurado com sucesso!"
    echo ""
    
    # Testar acesso ao repositório
    log "📦 Testando acesso ao repositório..."
    if git ls-remote git@github.com:fedimaraquino/dossie_escolar.git &>/dev/null; then
        log "✅ Acesso ao repositório confirmado!"
        echo ""
        log "🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
        echo ""
        log "🚀 Agora você pode executar o deploy:"
        log "   curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash"
        echo ""
        log "🔄 Ou clonar manualmente:"
        log "   git clone git@github.com:fedimaraquino/dossie_escolar.git /var/www/dossie_escolar"
    else
        warn "⚠️ SSH funcionando mas repositório não encontrado"
        info "💡 Verifique se o repositório existe: https://github.com/fedimaraquino/dossie_escolar"
    fi
else
    error "❌ SSH ainda não está funcionando!

Possíveis problemas:
1. Chave não foi adicionada corretamente no GitHub
2. Aguarde alguns minutos e tente novamente
3. Verifique se copiou a chave completa

Para testar manualmente:
ssh -T git@github.com"
fi

echo ""
log "🔑 Configuração SSH finalizada!"
