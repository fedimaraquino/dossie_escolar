#!/bin/bash
# Script de Deploy Automático para VPS Hostinger
# IP: 62.52.58.58

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

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   error "Este script deve ser executado como root (sudo)"
fi

log "🚀 Iniciando deploy do Sistema de Dossiê Escolar na VPS Hostinger"
log "🌐 IP: 62.52.58.58"

# Atualizar sistema
log "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências básicas
log "🔧 Instalando dependências..."
apt install -y curl wget git htop nano ufw python3

# Configurar firewall
log "🔥 Configurando firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp  # Aplicação
ufw allow 9000/tcp  # Portainer
ufw allow 8080/tcp  # Traefik
ufw --force enable

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    log "🐳 Instalando Docker..."
    
    # Remover versões antigas
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Instalar dependências
    apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Adicionar chave GPG
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Adicionar repositório
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Iniciar Docker
    systemctl start docker
    systemctl enable docker
    
    log "✅ Docker instalado com sucesso!"
else
    log "✅ Docker já está instalado"
fi

# Verificar se Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    log "🔄 Inicializando Docker Swarm..."
    docker swarm init --advertise-addr 62.52.58.58
else
    log "✅ Docker Swarm já está ativo"
fi

# Criar redes
log "🌐 Criando redes Docker..."
docker network create --driver overlay traefik-public 2>/dev/null || log "ℹ️ Rede traefik-public já existe"
docker network create --driver overlay app-network 2>/dev/null || log "ℹ️ Rede app-network já existe"

# Criar estrutura de diretórios
log "📁 Criando estrutura de diretórios..."
mkdir -p /opt/dossie-app/{traefik/data,portainer,postgres/data,app,scripts}
cd /opt/dossie-app

# Configurar permissões do Traefik
touch traefik/data/acme.json
chmod 600 traefik/data/acme.json

# Gerar SECRET_KEY
log "🔑 Gerando chave secreta..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Criar arquivo .env
log "⚙️ Criando arquivo de configuração..."
cat > .env << EOF
# VPS Hostinger
DOMAIN=62.52.58.58
USE_IP=true

# Email para certificados
ACME_EMAIL=admin@exemplo.com

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=Dossie@2024!Seguro

# Flask
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production

# URLs
DATABASE_URL=postgresql://dossie:Dossie@2024!Seguro@postgres:5432/dossie_escola
EOF

# Criar docker-compose.traefik.yml
log "🔀 Criando configuração do Traefik..."
cat > docker-compose.traefik.yml << 'EOF'
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    command:
      - --api.dashboard=true
      - --api.insecure=true
      - --providers.docker=true
      - --providers.docker.swarmmode=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --log.level=INFO
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/data:/data
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager

networks:
  traefik-public:
    external: true
EOF

# Criar docker-compose.portainer.yml
log "📊 Criando configuração do Portainer..."
cat > docker-compose.portainer.yml << 'EOF'
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:latest
    command: -H unix:///var/run/docker.sock
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager

volumes:
  portainer_data:

networks:
  traefik-public:
    external: true
EOF

# Criar docker-compose.postgres.yml
log "🐘 Criando configuração do PostgreSQL..."
cat > docker-compose.postgres.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dossie_escola
      POSTGRES_USER: dossie
      POSTGRES_PASSWORD: Dossie@2024!Seguro
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - ./postgres/data:/var/lib/postgresql/data
    networks:
      - app-network
    deploy:
      placement:
        constraints:
          - node.role == manager
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

networks:
  app-network:
    external: true
EOF

# Verificar se o código da aplicação existe
if [ ! -f "app/app.py" ]; then
    warn "⚠️ Código da aplicação não encontrado em /opt/dossie-app/app/"
    warn "📋 Você precisa copiar os arquivos da aplicação para /opt/dossie-app/app/"
    warn "💡 Use: scp -r /caminho/local/dossie_novo/* root@62.52.58.58:/opt/dossie-app/app/"
    
    # Criar estrutura básica para teste
    log "📝 Criando estrutura básica para teste..."
    mkdir -p app
    
    # Criar requirements.txt básico
    cat > app/requirements.txt << 'EOF'
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
psycopg2-binary==2.9.10
Werkzeug==3.1.3
Pillow==11.0.0
gunicorn==21.2.0
EOF
    
    warn "⚠️ Criada estrutura básica. Copie seus arquivos da aplicação antes de continuar."
    warn "🔄 Execute novamente este script após copiar os arquivos."
    exit 1
fi

# Criar Dockerfile se não existir
if [ ! -f "app/Dockerfile" ]; then
    log "🐳 Criando Dockerfile..."
    cat > app/Dockerfile << 'EOF'
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p static/uploads logs
RUN chown -R app:app /app

USER app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
EOF
fi

# Criar docker-compose.app.yml
log "🌐 Criando configuração da aplicação..."
cat > docker-compose.app.yml << EOF
version: '3.8'

services:
  dossie-app:
    build: ./app
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://dossie:Dossie@2024!Seguro@postgres:5432/dossie_escola
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "5000:5000"
    volumes:
      - ./app/static/uploads:/app/static/uploads
      - ./app/logs:/app/logs
    networks:
      - traefik-public
      - app-network
    depends_on:
      - postgres
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure

networks:
  traefik-public:
    external: true
  app-network:
    external: true
EOF

# Deploy dos serviços
log "🚀 Iniciando deploy dos serviços..."

log "🔀 Deploy do Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

log "📊 Deploy do Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

log "🐘 Deploy do PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

log "⏳ Aguardando PostgreSQL inicializar..."
sleep 30

log "🏗️ Build da aplicação..."
cd app && docker build -t dossie-app:latest . && cd ..

log "🌐 Deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

log "⏳ Aguardando aplicação inicializar..."
sleep 60

# Verificar status
log "📊 Verificando status dos serviços..."
docker stack ls
docker service ls

log "✅ Deploy concluído com sucesso!"
log ""
log "🌐 URLs de Acesso:"
log "   📱 Aplicação: http://62.52.58.58:5000"
log "   📊 Portainer: http://62.52.58.58:9000"
log "   🔀 Traefik:   http://62.52.58.58:8080"
log ""
log "👤 Credenciais padrão:"
log "   📧 Email: admin@escola.com"
log "   🔑 Senha: Admin@123"
log ""
log "🔧 Próximos passos:"
log "   1. Acesse o Portainer e configure o usuário admin"
log "   2. Execute as migrações do banco de dados"
log "   3. Crie o usuário administrador"
log ""
log "🎉 Sua aplicação está rodando na VPS Hostinger!"
