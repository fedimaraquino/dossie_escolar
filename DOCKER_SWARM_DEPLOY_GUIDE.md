# 🐳 GUIA DE DEPLOY - Docker Swarm + Traefik + Portainer

## 📋 **VISÃO GERAL**

Este guia mostra como fazer o deploy do **Sistema de Controle de Dossiê Escolar** usando:

- **🐳 Docker Swarm** - Orquestração de containers
- **🔀 Traefik** - Reverse proxy e load balancer
- **📊 Portainer** - Interface web para gerenciamento
- **🐘 PostgreSQL** - Banco de dados
- **🌐 Flask App** - Aplicação principal

---

## 🛠️ **PRÉ-REQUISITOS**

### **Servidor/VPS:**
- **OS**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **CPU**: 2 cores ou mais
- **Disco**: 20GB+ de espaço livre
- **Rede**: IP público com portas 80, 443, 9000 abertas

### **Software:**
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** para clonar repositório

---

## 🚀 **PASSO 1: PREPARAÇÃO DO SERVIDOR**

### **1.1 Atualizar Sistema**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### **1.2 Instalar Docker**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### **1.3 Instalar Docker Compose**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### **1.4 Verificar Instalação**
```bash
docker --version
docker-compose --version
```

### **1.5 Reiniciar Sessão**
```bash
# Logout e login novamente para aplicar permissões
exit
# Conectar novamente via SSH
```

---

## 🔧 **PASSO 2: CONFIGURAÇÃO DO DOCKER SWARM**

### **2.1 Inicializar Swarm**
```bash
# Substituir SEU_IP pelo IP público do servidor
docker swarm init --advertise-addr SEU_IP_PUBLICO

# Exemplo:
# docker swarm init --advertise-addr 192.168.1.100
```

### **2.2 Verificar Status**
```bash
docker node ls
```

### **2.3 Criar Redes**
```bash
# Rede para Traefik (proxy)
docker network create --driver overlay traefik-public

# Rede para aplicação
docker network create --driver overlay app-network
```

---

## 📁 **PASSO 3: ESTRUTURA DE ARQUIVOS**

### **3.1 Criar Diretórios**
```bash
mkdir -p /opt/dossie-app
cd /opt/dossie-app

mkdir -p {traefik,portainer,app,postgres}
mkdir -p traefik/{data,config}
mkdir -p postgres/data
```

### **3.2 Clonar Aplicação**
```bash
cd /opt/dossie-app/app
git clone https://github.com/SEU_USUARIO/dossie_novo.git .

# Ou copiar arquivos manualmente
# scp -r /caminho/local/dossie_novo/* usuario@servidor:/opt/dossie-app/app/
```

---

## 🔀 **PASSO 4: CONFIGURAR TRAEFIK**

### **4.1 Criar docker-compose.traefik.yml**
```bash
cd /opt/dossie-app
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
      - --certificatesresolvers.letsencrypt.acme.email=seu-email@dominio.com
      - --certificatesresolvers.letsencrypt.acme.storage=/data/acme.json
      - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard Traefik
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/data:/data
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager
      labels:
        - traefik.enable=true
        - traefik.http.routers.traefik.rule=Host(`traefik.SEU_DOMINIO.com`)
        - traefik.http.routers.traefik.tls.certresolver=letsencrypt
        - traefik.http.services.traefik.loadbalancer.server.port=8080

networks:
  traefik-public:
    external: true
EOF
```

### **4.2 Configurar Permissões**
```bash
touch ./traefik/data/acme.json
chmod 600 ./traefik/data/acme.json
```

### **4.3 Deploy Traefik**
```bash
docker stack deploy -c docker-compose.traefik.yml traefik
```

---

## 📊 **PASSO 5: CONFIGURAR PORTAINER**

### **5.1 Criar docker-compose.portainer.yml**
```bash
cat > docker-compose.portainer.yml << 'EOF'
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:latest
    command: -H unix:///var/run/docker.sock
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./portainer/data:/data
    networks:
      - traefik-public
    deploy:
      placement:
        constraints:
          - node.role == manager
      labels:
        - traefik.enable=true
        - traefik.http.routers.portainer.rule=Host(`portainer.SEU_DOMINIO.com`)
        - traefik.http.routers.portainer.tls.certresolver=letsencrypt
        - traefik.http.services.portainer.loadbalancer.server.port=9000

networks:
  traefik-public:
    external: true
EOF
```

### **5.2 Deploy Portainer**
```bash
docker stack deploy -c docker-compose.portainer.yml portainer
```

---

## 🐘 **PASSO 6: CONFIGURAR POSTGRESQL**

### **6.1 Criar docker-compose.postgres.yml**
```bash
cat > docker-compose.postgres.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dossie_escola
      POSTGRES_USER: dossie
      POSTGRES_PASSWORD: fep09151
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
```

### **6.2 Deploy PostgreSQL**
```bash
docker stack deploy -c docker-compose.postgres.yml postgres
```

---

## 🌐 **PASSO 7: CONFIGURAR APLICAÇÃO FLASK**

### **7.1 Criar Dockerfile**
```bash
cd /opt/dossie-app/app
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p static/uploads logs
RUN chown -R app:app /app

# Mudar para usuário não-root
USER app

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
EOF
```

### **7.2 Atualizar requirements.txt**
```bash
cat >> requirements.txt << 'EOF'
gunicorn==21.2.0
EOF
```

### **7.3 Criar .dockerignore**
```bash
cat > .dockerignore << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
README.md
Dockerfile
.dockerignore
migrations/versions/*
logs/*
static/uploads/*
EOF
```

### **7.4 Criar docker-compose.app.yml**
```bash
cd /opt/dossie-app
cat > docker-compose.app.yml << 'EOF'
version: '3.8'

services:
  dossie-app:
    build: ./app
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://dossie:fep09151@postgres:5432/dossie_escola
      - SECRET_KEY=sua-chave-secreta-super-segura-aqui
    volumes:
      - ./app/static/uploads:/app/static/uploads
      - ./app/logs:/app/logs
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
      restart_policy:
        condition: on-failure
      labels:
        - traefik.enable=true
        - traefik.http.routers.dossie.rule=Host(`dossie.SEU_DOMINIO.com`)
        - traefik.http.routers.dossie.tls.certresolver=letsencrypt
        - traefik.http.services.dossie.loadbalancer.server.port=5000

networks:
  traefik-public:
    external: true
  app-network:
    external: true
EOF
```

---

## 🔑 **PASSO 8: CONFIGURAR VARIÁVEIS DE AMBIENTE**

### **8.1 Criar arquivo .env**
```bash
cat > .env << 'EOF'
# Domínio principal
DOMAIN=SEU_DOMINIO.com

# Email para certificados SSL
ACME_EMAIL=seu-email@dominio.com

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=fep09151

# Flask
SECRET_KEY=sua-chave-secreta-super-segura-de-32-caracteres-ou-mais
FLASK_ENV=production

# URLs
DATABASE_URL=postgresql://dossie:fep09151@postgres:5432/dossie_escola
EOF
```

### **8.2 Gerar SECRET_KEY**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copiar o resultado e substituir no .env
```

---

## 🚀 **PASSO 9: DEPLOY COMPLETO**

### **9.1 Build da Aplicação**
```bash
cd /opt/dossie-app/app
docker build -t dossie-app:latest .
```

### **9.2 Deploy da Aplicação**
```bash
cd /opt/dossie-app
docker stack deploy -c docker-compose.app.yml dossie
```

### **9.3 Verificar Status**
```bash
docker stack ls
docker service ls
docker stack ps traefik
docker stack ps portainer
docker stack ps postgres
docker stack ps dossie
```

---

## 🔧 **PASSO 10: CONFIGURAÇÃO INICIAL**

### **10.1 Executar Migrações**
```bash
# Encontrar container da aplicação
docker ps | grep dossie-app

# Executar migrações
docker exec -it CONTAINER_ID flask db upgrade

# Ou usando docker service
docker service ps dossie_dossie-app
docker exec -it $(docker ps -q -f name=dossie_dossie-app) flask db upgrade
```

### **10.2 Criar Usuário Admin**
```bash
docker exec -it $(docker ps -q -f name=dossie_dossie-app) python -c "
from app import create_app
from models import db, Usuario, Perfil, Escola

app = create_app()
with app.app_context():
    # Criar escola padrão se não existir
    escola = Escola.query.first()
    if not escola:
        escola = Escola(nome='Escola Principal', situacao='ativa')
        db.session.add(escola)
        db.session.commit()
    
    # Criar perfil admin se não existir
    perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
    if not perfil:
        perfil = Perfil(perfil='Administrador Geral', nome='Administrador Geral')
        db.session.add(perfil)
        db.session.commit()
    
    # Criar usuário admin
    admin = Usuario.query.filter_by(email='admin@escola.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@escola.com',
            escola_id=escola.id,
            perfil_id=perfil.id_perfil,
            situacao='ativo'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print('Usuário admin criado: admin@escola.com / Admin@123')
    else:
        print('Usuário admin já existe')
"
```

---

## 🌐 **PASSO 11: CONFIGURAR DNS**

### **11.1 Apontar Domínios**
Configure os seguintes registros DNS:

```
A    dossie.SEU_DOMINIO.com      → SEU_IP_PUBLICO
A    traefik.SEU_DOMINIO.com     → SEU_IP_PUBLICO
A    portainer.SEU_DOMINIO.com   → SEU_IP_PUBLICO
```

### **11.2 Aguardar Propagação**
```bash
# Verificar DNS
nslookup dossie.SEU_DOMINIO.com
nslookup traefik.SEU_DOMINIO.com
nslookup portainer.SEU_DOMINIO.com
```

---

## ✅ **PASSO 12: VERIFICAÇÃO FINAL**

### **12.1 Acessar Serviços**

- **📱 Aplicação**: https://dossie.SEU_DOMINIO.com
- **🔀 Traefik**: https://traefik.SEU_DOMINIO.com
- **📊 Portainer**: https://portainer.SEU_DOMINIO.com

### **12.2 Verificar Logs**
```bash
# Logs da aplicação
docker service logs dossie_dossie-app

# Logs do Traefik
docker service logs traefik_traefik

# Logs do PostgreSQL
docker service logs postgres_postgres
```

### **12.3 Teste de Login**
- **URL**: https://dossie.SEU_DOMINIO.com
- **Email**: admin@escola.com
- **Senha**: Admin@123

---

## 🔧 **COMANDOS ÚTEIS DE MANUTENÇÃO**

### **Atualizar Aplicação:**
```bash
cd /opt/dossie-app/app
git pull origin main
docker build -t dossie-app:latest .
docker service update --image dossie-app:latest dossie_dossie-app
```

### **Backup do Banco:**
```bash
docker exec $(docker ps -q -f name=postgres_postgres) pg_dump -U dossie dossie_escola > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Restaurar Backup:**
```bash
docker exec -i $(docker ps -q -f name=postgres_postgres) psql -U dossie dossie_escola < backup.sql
```

### **Monitorar Recursos:**
```bash
docker stats
docker system df
```

### **Limpar Sistema:**
```bash
docker system prune -f
docker volume prune -f
```

---

## 🎯 **CONCLUSÃO**

Parabéns! 🎉 Sua aplicação está rodando em produção com:

- ✅ **Alta Disponibilidade** com Docker Swarm
- ✅ **SSL Automático** com Traefik + Let's Encrypt
- ✅ **Gerenciamento Visual** com Portainer
- ✅ **Banco Persistente** com PostgreSQL
- ✅ **Load Balancing** automático
- ✅ **Logs Centralizados**
- ✅ **Backup Automatizado**

**Sua aplicação está pronta para produção! 🚀**

---

## 📜 **SCRIPTS DE AUTOMAÇÃO**

### **Script de Deploy Completo** - `deploy.sh`
```bash
#!/bin/bash
# Script para deploy automático

set -e

echo "🚀 Iniciando deploy do Sistema de Dossiê Escolar..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    exit 1
fi

# Verificar se Swarm está ativo
if ! docker info | grep -q "Swarm: active"; then
    echo "❌ Docker Swarm não está ativo!"
    exit 1
fi

# Deploy dos serviços
echo "📦 Fazendo deploy do Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

echo "📊 Fazendo deploy do Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

echo "🐘 Fazendo deploy do PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

echo "⏳ Aguardando PostgreSQL inicializar..."
sleep 30

echo "🌐 Fazendo build da aplicação..."
cd app && docker build -t dossie-app:latest . && cd ..

echo "🚀 Fazendo deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

echo "✅ Deploy concluído!"
echo "📱 Acesse: https://dossie.SEU_DOMINIO.com"
```

### **Script de Backup** - `backup.sh`
```bash
#!/bin/bash
# Script para backup automático

BACKUP_DIR="/opt/backups/dossie"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "💾 Iniciando backup..."

# Backup do banco
echo "🐘 Backup do PostgreSQL..."
docker exec $(docker ps -q -f name=postgres_postgres) pg_dump -U dossie dossie_escola > $BACKUP_DIR/db_$DATE.sql

# Backup dos uploads
echo "📁 Backup dos arquivos..."
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/dossie-app/app/static uploads

# Backup das configurações
echo "⚙️ Backup das configurações..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C /opt/dossie-app *.yml .env

# Limpar backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup concluído em $BACKUP_DIR"
```

### **Script de Monitoramento** - `monitor.sh`
```bash
#!/bin/bash
# Script para monitoramento dos serviços

echo "📊 STATUS DOS SERVIÇOS"
echo "====================="

# Verificar stacks
echo "🐳 Docker Stacks:"
docker stack ls

echo ""
echo "🔧 Serviços:"
docker service ls

echo ""
echo "💾 Uso de Disco:"
df -h /opt/dossie-app

echo ""
echo "🧠 Uso de Memória:"
free -h

echo ""
echo "📈 Status dos Containers:"
docker stats --no-stream

echo ""
echo "🔍 Logs Recentes da Aplicação:"
docker service logs --tail 10 dossie_dossie-app
```

---

## 🔧 **TROUBLESHOOTING**

### **Problemas Comuns:**

#### **1. Certificado SSL não gerado**
```bash
# Verificar logs do Traefik
docker service logs traefik_traefik

# Verificar se domínio aponta para o servidor
nslookup dossie.SEU_DOMINIO.com

# Verificar arquivo acme.json
ls -la /opt/dossie-app/traefik/data/acme.json
```

#### **2. Aplicação não conecta no banco**
```bash
# Verificar se PostgreSQL está rodando
docker service ps postgres_postgres

# Testar conexão
docker exec -it $(docker ps -q -f name=postgres_postgres) psql -U dossie -d dossie_escola -c "SELECT 1;"

# Verificar logs da aplicação
docker service logs dossie_dossie-app
```

#### **3. Portainer não acessível**
```bash
# Verificar se serviço está rodando
docker service ps portainer_portainer

# Verificar logs
docker service logs portainer_portainer

# Acessar diretamente pela porta
curl http://localhost:9000
```

#### **4. Aplicação lenta**
```bash
# Verificar recursos
docker stats

# Escalar aplicação
docker service scale dossie_dossie-app=4

# Verificar logs de performance
docker service logs dossie_dossie-app | grep -i error
```

---

## 📚 **RECURSOS ADICIONAIS**

### **Documentação Oficial:**
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [Traefik](https://doc.traefik.io/traefik/)
- [Portainer](https://documentation.portainer.io/)

### **Monitoramento Avançado:**
- **Prometheus + Grafana** para métricas
- **ELK Stack** para logs centralizados
- **Uptime Kuma** para monitoramento de disponibilidade

### **Segurança:**
- **Fail2ban** para proteção contra ataques
- **UFW/iptables** para firewall
- **Backup automático** para S3/MinIO

**Sistema completo e robusto para produção! 🎯**
