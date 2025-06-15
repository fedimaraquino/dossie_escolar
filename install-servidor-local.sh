#!/bin/bash
# Script de Instalação Completa - Servidor Local 10.0.1.185
# Sistema de Controle de Dossiê Escolar

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

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🏫 SISTEMA DE CONTROLE DE DOSSIÊ ESCOLAR                  ║"
echo "║    🚀 Instalação Automática - Servidor Local                ║"
echo "║    🌐 IP: 10.0.1.185                                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   warn "Este script não deve ser executado como root"
   warn "Execute como usuário normal com sudo quando necessário"
   exit 1
fi

log "🔍 Verificando sistema..."

# Verificar IP do servidor
CURRENT_IP=$(hostname -I | awk '{print $1}')
if [[ "$CURRENT_IP" != "10.0.1.185" ]]; then
    warn "IP atual: $CURRENT_IP"
    warn "IP esperado: 10.0.1.185"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Atualizar sistema
log "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
log "🔧 Instalando dependências..."
sudo apt install -y curl wget git htop nano ufw net-tools python3 python3-pip

# Configurar firewall
log "🔥 Configurando firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 9000/tcp
sudo ufw allow 8080/tcp
sudo ufw allow from 10.0.1.0/24
sudo ufw --force enable

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    log "🐳 Instalando Docker..."
    
    # Remover versões antigas
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Instalar dependências
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Adicionar chave GPG
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Adicionar repositório
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    # Iniciar Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    log "✅ Docker instalado com sucesso!"
    
    # Verificar se precisa reiniciar sessão
    if ! groups | grep -q docker; then
        warn "⚠️ Você precisa fazer logout e login novamente para usar Docker sem sudo"
        warn "⚠️ Ou execute: newgrp docker"
        read -p "Executar 'newgrp docker' agora? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            exec newgrp docker
        fi
    fi
else
    log "✅ Docker já está instalado"
fi

# Verificar se Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    log "🔄 Inicializando Docker Swarm..."
    docker swarm init --advertise-addr 10.0.1.185
else
    log "✅ Docker Swarm já está ativo"
fi

# Criar redes
log "🌐 Criando redes Docker..."
docker network create --driver overlay traefik-public 2>/dev/null || log "ℹ️ Rede traefik-public já existe"
docker network create --driver overlay app-network 2>/dev/null || log "ℹ️ Rede app-network já existe"

# Criar estrutura de diretórios
log "📁 Criando estrutura de diretórios..."
sudo mkdir -p /opt/dossie-app
sudo chown -R $USER:$USER /opt/dossie-app
cd /opt/dossie-app

mkdir -p {traefik/data,portainer,postgres/{data,init},app,scripts,backups,monitoring/{prometheus,grafana/{dashboards,datasources}}}

# Configurar permissões do Traefik
touch traefik/data/acme.json
chmod 600 traefik/data/acme.json

# Gerar SECRET_KEY
log "🔑 Gerando chave secreta..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Criar arquivo .env
log "⚙️ Criando arquivo de configuração..."
cat > .env << EOF
# Servidor Local
DOMAIN=10.0.1.185
USE_IP=true
SERVER_IP=10.0.1.185

# Email para certificados (não usado com IP)
ACME_EMAIL=admin@empresa.local

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=DossieLocal@2024!Seguro

# Flask
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=production

# URLs
DATABASE_URL=postgresql://dossie:DossieLocal@2024!Seguro@postgres:5432/dossie_escola

# Configurações de rede
NETWORK_SUBNET=10.0.1.0/24
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
      - --accesslog=true
      - --global.sendanonymoususage=false
      - --ping=true
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
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

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
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - portainer_data:/data
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

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
      POSTGRES_PASSWORD: DossieLocal@2024!Seguro
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - app-network
    deploy:
      placement:
        constraints:
          - node.role == manager
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dossie -d dossie_escola"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  postgres_data:

networks:
  app-network:
    external: true
EOF

# Verificar se o código da aplicação existe
if [ ! -f "app/app.py" ]; then
    warn "⚠️ Código da aplicação não encontrado em /opt/dossie-app/app/"
    warn "📋 Você precisa copiar os arquivos da aplicação para /opt/dossie-app/app/"
    warn "💡 Exemplo: rsync -avz /caminho/origem/ /opt/dossie-app/app/"
    
    # Criar estrutura básica
    log "📝 Criando estrutura básica..."
    mkdir -p app
    
    cat > app/requirements.txt << 'EOF'
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
psycopg2-binary==2.9.10
Werkzeug==3.1.3
Pillow==11.0.0
gunicorn==21.2.0
Flask-Limiter==3.5.0
EOF
    
    warn "⚠️ Estrutura básica criada. Copie seus arquivos da aplicação antes de continuar."
    info "📋 Após copiar os arquivos, execute: ./deploy-local.sh"
    exit 0
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

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
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
      - DATABASE_URL=postgresql://dossie:DossieLocal@2024!Seguro@postgres:5432/dossie_escola
      - SECRET_KEY=${SECRET_KEY}
      - SERVER_NAME=10.0.1.185
    ports:
      - "5000:5000"
    volumes:
      - app_uploads:/app/static/uploads
      - app_logs:/app/logs
    networks:
      - traefik-public
      - app-network
    depends_on:
      - postgres
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
      labels:
        - traefik.enable=true
        - traefik.http.routers.dossie.rule=Host(\`10.0.1.185\`)
        - traefik.http.routers.dossie.entrypoints=web
        - traefik.http.services.dossie.loadbalancer.server.port=5000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  app_uploads:
  app_logs:

networks:
  traefik-public:
    external: true
  app-network:
    external: true
EOF

# Criar script de deploy
log "🚀 Criando script de deploy..."
cat > deploy-local.sh << 'EOF'
#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m'
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }

log "🚀 Iniciando deploy..."

# Verificações
docker info > /dev/null 2>&1 || { echo "❌ Docker não está rodando!"; exit 1; }
docker info | grep -q "Swarm: active" || { echo "❌ Docker Swarm não está ativo!"; exit 1; }

# Carregar variáveis
[ -f .env ] && source .env

# Deploy
log "🔀 Deploy Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

log "📊 Deploy Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

log "🐘 Deploy PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

log "⏳ Aguardando PostgreSQL..."
sleep 30

log "🏗️ Build da aplicação..."
cd app && docker build -t dossie-app:latest . && cd ..

log "🌐 Deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

log "⏳ Aguardando inicialização..."
sleep 60

log "📊 Status:"
docker stack ls
docker service ls

log "✅ Deploy concluído!"
log "🌐 Acesse: http://10.0.1.185"
EOF

chmod +x deploy-local.sh

# Criar script de configuração inicial
log "🔧 Criando script de configuração..."
cat > setup-inicial.sh << 'EOF'
#!/bin/bash
set -e

GREEN='\033[0;32m'
NC='\033[0m'
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }

log "🗄️ Configurando banco de dados..."

sleep 60

APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)
[ -z "$APP_CONTAINER" ] && { echo "❌ Container não encontrado!"; exit 1; }

log "🔄 Executando migrações..."
docker exec $APP_CONTAINER flask db upgrade || {
    docker exec $APP_CONTAINER flask db init || true
    docker exec $APP_CONTAINER flask db migrate -m "Initial migration" || true
    docker exec $APP_CONTAINER flask db upgrade || true
}

log "👤 Criando usuário admin..."
docker exec $APP_CONTAINER python3 << 'PYTHON_EOF'
from app import create_app
from models import db, Usuario, Perfil, Escola

try:
    app = create_app()
    with app.app_context():
        escola = Escola.query.first()
        if not escola:
            escola = Escola(nome='Escola Local', situacao='ativa')
            db.session.add(escola)
            db.session.commit()
        
        perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
        if not perfil:
            perfil = Perfil(perfil='Administrador Geral', nome='Administrador Geral')
            db.session.add(perfil)
            db.session.commit()
        
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
            print("✅ Admin criado: admin@local.escola / Admin@Local123")
        else:
            print("ℹ️ Admin já existe")
except Exception as e:
    print(f"❌ Erro: {e}")
PYTHON_EOF

log "✅ Configuração concluída!"
log "🌐 Acesse: http://10.0.1.185"
log "👤 Login: admin@local.escola / Admin@Local123"
EOF

chmod +x setup-inicial.sh

log "✅ Instalação concluída!"
log ""
log "🎯 PRÓXIMOS PASSOS:"
log "1. Copie os arquivos da aplicação para /opt/dossie-app/app/"
log "2. Execute: ./deploy-local.sh"
log "3. Execute: ./setup-inicial.sh"
log "4. Acesse: http://10.0.1.185"
log ""
log "📁 Diretório: /opt/dossie-app"
log "🎉 Sistema pronto para deploy!"
