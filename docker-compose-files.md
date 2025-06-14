# 📁 ARQUIVOS DOCKER-COMPOSE PRONTOS

## 🔀 **docker-compose.traefik.yml**

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    command:
      - --api.dashboard=true
      - --api.insecure=false
      - --providers.docker=true
      - --providers.docker.swarmmode=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}
      - --certificatesresolvers.letsencrypt.acme.storage=/data/acme.json
      - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
      - --global.sendanonymoususage=false
      - --log.level=INFO
      - --accesslog=true
    ports:
      - "80:80"
      - "443:443"
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
      labels:
        - traefik.enable=true
        - traefik.http.routers.traefik.rule=Host(`traefik.${DOMAIN}`)
        - traefik.http.routers.traefik.tls.certresolver=letsencrypt
        - traefik.http.routers.traefik.service=api@internal
        - traefik.http.routers.traefik.middlewares=auth
        - traefik.http.middlewares.auth.basicauth.users=admin:$$2y$$10$$K8V2VzWzVzWzVzWzVzWzVe
        # Redirect HTTP to HTTPS
        - traefik.http.routers.http-catchall.rule=hostregexp(`{host:.+}`)
        - traefik.http.routers.http-catchall.entrypoints=web
        - traefik.http.routers.http-catchall.middlewares=redirect-to-https
        - traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https

networks:
  traefik-public:
    external: true
```

---

## 📊 **docker-compose.portainer.yml**

```yaml
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:latest
    command: -H unix:///var/run/docker.sock
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
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
      labels:
        - traefik.enable=true
        - traefik.http.routers.portainer.rule=Host(`portainer.${DOMAIN}`)
        - traefik.http.routers.portainer.tls.certresolver=letsencrypt
        - traefik.http.routers.portainer.entrypoints=websecure
        - traefik.http.services.portainer.loadbalancer.server.port=9000

volumes:
  portainer_data:

networks:
  traefik-public:
    external: true
```

---

## 🐘 **docker-compose.postgres.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
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
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres-backup:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_backups:/backups
      - ./scripts/backup.sh:/backup.sh
    networks:
      - app-network
    deploy:
      replicas: 0  # Executar manualmente
    command: /bin/sh -c "chmod +x /backup.sh && /backup.sh"

volumes:
  postgres_data:
  postgres_backups:

networks:
  app-network:
    external: true
```

---

## 🌐 **docker-compose.app.yml**

```yaml
version: '3.8'

services:
  dossie-app:
    image: dossie-app:latest
    build:
      context: ./app
      dockerfile: Dockerfile
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - SECRET_KEY=${SECRET_KEY}
      - UPLOAD_FOLDER=/app/static/uploads
      - MAX_CONTENT_LENGTH=16777216  # 16MB
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
      rollback_config:
        parallelism: 1
        delay: 5s
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
        - traefik.http.routers.dossie.rule=Host(`dossie.${DOMAIN}`)
        - traefik.http.routers.dossie.tls.certresolver=letsencrypt
        - traefik.http.routers.dossie.entrypoints=websecure
        - traefik.http.services.dossie.loadbalancer.server.port=5000
        - traefik.http.routers.dossie.middlewares=security-headers
        - traefik.http.middlewares.security-headers.headers.customrequestheaders.X-Forwarded-Proto=https
        - traefik.http.middlewares.security-headers.headers.customrequestheaders.X-Forwarded-For=$$remote_addr
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    networks:
      - app-network
    deploy:
      resources:
        limits:
          memory: 128M
        reservations:
          memory: 64M
    command: redis-server --appendonly yes --maxmemory 100mb --maxmemory-policy allkeys-lru

volumes:
  app_uploads:
  app_logs:

networks:
  traefik-public:
    external: true
  app-network:
    external: true
```

---

## 📊 **docker-compose.monitoring.yml** (Opcional)

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - traefik-public
      - app-network
    deploy:
      labels:
        - traefik.enable=true
        - traefik.http.routers.prometheus.rule=Host(`prometheus.${DOMAIN}`)
        - traefik.http.routers.prometheus.tls.certresolver=letsencrypt
        - traefik.http.services.prometheus.loadbalancer.server.port=9090

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - traefik-public
      - app-network
    deploy:
      labels:
        - traefik.enable=true
        - traefik.http.routers.grafana.rule=Host(`grafana.${DOMAIN}`)
        - traefik.http.routers.grafana.tls.certresolver=letsencrypt
        - traefik.http.services.grafana.loadbalancer.server.port=3000

volumes:
  prometheus_data:
  grafana_data:

networks:
  traefik-public:
    external: true
  app-network:
    external: true
```

---

## 🔧 **docker-compose.override.yml** (Desenvolvimento)

```yaml
version: '3.8'

services:
  dossie-app:
    build:
      context: ./app
      target: development
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    volumes:
      - ./app:/app
    ports:
      - "5000:5000"
    command: flask run --host=0.0.0.0 --port=5000 --reload

  postgres:
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=dossie_escola_dev
```

---

## 📜 **Arquivo .env de Exemplo**

```bash
# Domínio principal
DOMAIN=exemplo.com

# Email para certificados SSL
ACME_EMAIL=admin@exemplo.com

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=senha_super_segura_aqui

# Flask
SECRET_KEY=sua-chave-secreta-de-32-caracteres-ou-mais-aqui
FLASK_ENV=production

# Traefik
TRAEFIK_AUTH_USER=admin
TRAEFIK_AUTH_PASSWORD=senha_dashboard_traefik

# Backup
BACKUP_RETENTION_DAYS=7
BACKUP_S3_BUCKET=meu-bucket-backup
```

---

## 🚀 **Script de Deploy Rápido**

```bash
#!/bin/bash
# deploy-all.sh

set -e

echo "🚀 Deploy completo do Sistema de Dossiê Escolar"

# Carregar variáveis de ambiente
source .env

# Criar redes se não existirem
docker network create --driver overlay traefik-public 2>/dev/null || true
docker network create --driver overlay app-network 2>/dev/null || true

# Deploy em ordem
echo "📦 Deploy Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

echo "📊 Deploy Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

echo "🐘 Deploy PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

echo "⏳ Aguardando PostgreSQL..."
sleep 30

echo "🏗️ Build da aplicação..."
docker build -t dossie-app:latest ./app

echo "🌐 Deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

echo "✅ Deploy concluído!"
echo "🌐 Aplicação: https://dossie.${DOMAIN}"
echo "📊 Portainer: https://portainer.${DOMAIN}"
echo "🔀 Traefik: https://traefik.${DOMAIN}"
```

**Todos os arquivos estão prontos para uso em produção! 🎯**
