#!/bin/bash
# Script de Deploy via Git - Sistema de Dossiê Escolar
# Repositório: https://github.com/fedimaraquino/dossie_escolar.git

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
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
REPO_URL="git@github.com:fedimaraquino/dossie_escolar.git"
APP_DIR="/var/www/dossie_escolar"
BRANCH="main"

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🏫 SISTEMA DE CONTROLE DE DOSSIÊ ESCOLAR                  ║"
echo "║    🚀 Deploy via Git - Servidor Local                       ║"
echo "║    📦 Repositório: fedimaraquino/dossie_escolar              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🚀 Iniciando deploy via Git no servidor local 10.0.1.185"

# Verificar se Git está instalado
if ! command -v git &> /dev/null; then
    error "Git não está instalado! Execute: sudo apt install git"
fi

# Verificar se SSH está configurado para GitHub
log "🔑 Verificando acesso SSH ao GitHub..."
if ! ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    error "❌ SSH não está configurado para GitHub!

📋 Configure SSH seguindo estes passos:

1. Gerar chave SSH:
   ssh-keygen -t ed25519 -C \"seu-email@exemplo.com\"

2. Adicionar ao ssh-agent:
   eval \"\$(ssh-agent -s)\"
   ssh-add ~/.ssh/id_ed25519

3. Copiar chave pública:
   cat ~/.ssh/id_ed25519.pub

4. Adicionar no GitHub:
   - Vá em: Settings > SSH and GPG keys > New SSH key
   - Cole a chave pública

5. Testar:
   ssh -T git@github.com"
else
    log "✅ SSH configurado corretamente para GitHub"
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    error "Docker não está rodando! Execute: sudo systemctl start docker"
fi

# Verificar se Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    error "Docker Swarm não está ativo! Execute: docker swarm init --advertise-addr 10.0.1.185"
fi

# Criar diretório se não existir
if [ ! -d "$APP_DIR" ]; then
    log "📁 Criando diretório $APP_DIR..."
    sudo mkdir -p "$APP_DIR"
    sudo chown -R $USER:$USER "$APP_DIR"
fi

# Verificar se é um repositório Git existente
if [ -d "$APP_DIR/.git" ]; then
    log "📦 Repositório Git existente encontrado"
    cd "$APP_DIR"
    
    # Verificar se é o repositório correto
    CURRENT_REPO=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$CURRENT_REPO" != "$REPO_URL" ]]; then
        warn "⚠️ Repositório diferente detectado: $CURRENT_REPO"
        warn "⚠️ Esperado: $REPO_URL"
        read -p "Deseja remover e clonar novamente? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd ..
            sudo rm -rf "$APP_DIR"
            log "🗑️ Diretório removido"
        else
            error "❌ Deploy cancelado"
        fi
    else
        log "✅ Repositório correto detectado"
        
        # Verificar se há mudanças locais
        if ! git diff --quiet || ! git diff --cached --quiet; then
            warn "⚠️ Há mudanças locais não commitadas"
            git status --porcelain
            read -p "Deseja descartar as mudanças locais? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git reset --hard HEAD
                git clean -fd
                log "🧹 Mudanças locais descartadas"
            else
                error "❌ Deploy cancelado. Commit ou descarte as mudanças primeiro"
            fi
        fi
        
        # Fazer pull das atualizações
        log "📥 Fazendo pull das atualizações..."
        git fetch origin
        git reset --hard origin/$BRANCH
        log "✅ Código atualizado do repositório"
    fi
fi

# Clonar repositório se não existir
if [ ! -d "$APP_DIR/.git" ]; then
    log "📥 Clonando repositório do GitHub..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
    log "✅ Repositório clonado com sucesso"
fi

# Ir para o diretório da aplicação
cd "$APP_DIR"

# Verificar branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    log "🔄 Mudando para branch $BRANCH..."
    git checkout "$BRANCH"
fi

# Mostrar informações do commit atual
log "📋 Informações do commit atual:"
git log --oneline -1
echo ""

# Verificar se arquivo de configuração existe
if [ ! -f "env-servidor-local" ]; then
    error "❌ Arquivo env-servidor-local não encontrado no repositório!"
fi

# Configurar ambiente
log "⚙️ Configurando ambiente..."
cp env-servidor-local .env
source .env

log "✅ Configuração carregada"

# Verificar SECRET_KEY
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

# Dar permissões aos scripts
log "🔧 Configurando permissões dos scripts..."
chmod +x *.sh
log "✅ Permissões configuradas"

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
docker build -t dossie-app:latest .

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

log "✅ Deploy via Git concluído com sucesso!"
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
log "📦 Repositório Git:"
log "   🔗 URL: $REPO_URL"
log "   🌿 Branch: $BRANCH"
log "   📁 Diretório: $APP_DIR"
echo ""
log "🔧 Comandos Úteis:"
log "   📊 Status: docker service ls"
log "   📋 Logs: docker service logs dossie_dossie-app"
log "   🔄 Restart: docker service update --force dossie_dossie-app"
log "   📥 Atualizar: cd $APP_DIR && git pull && ./deploy.sh"
echo ""
log "🎉 Sistema rodando no servidor local via Git!"
