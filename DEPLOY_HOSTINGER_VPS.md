# 🚀 DEPLOY NA VPS HOSTINGER - Sistema de Dossiê Escolar

## 📋 **INFORMAÇÕES DA VPS**

- **🌐 IP Público**: `62.52.58.58`
- **🏢 Provedor**: Hostinger VPS
- **🐧 OS**: Ubuntu (presumido)
- **🔧 Acesso**: SSH

---

## 🔑 **PASSO 1: CONECTAR NA VPS**

### **1.1 Conectar via SSH**
```bash
# Conectar na VPS (substitua 'root' pelo seu usuário se diferente)
ssh root@62.52.58.58

# Ou se tiver usuário específico:
# ssh usuario@62.52.58.58
```

### **1.2 Atualizar Sistema**
```bash
# Atualizar pacotes
apt update && apt upgrade -y

# Instalar utilitários básicos
apt install -y curl wget git htop nano ufw
```

### **1.3 Configurar Firewall**
```bash
# Configurar UFW (firewall)
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 9000/tcp  # Portainer (temporário)
ufw --force enable

# Verificar status
ufw status
```

---

## 🐳 **PASSO 2: INSTALAR DOCKER**

### **2.1 Instalar Docker**
```bash
# Remover versões antigas
apt remove -y docker docker-engine docker.io containerd runc

# Instalar dependências
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar e habilitar Docker
systemctl start docker
systemctl enable docker

# Verificar instalação
docker --version
docker compose version
```

### **2.2 Configurar Docker Swarm**
```bash
# Inicializar Swarm com IP da VPS
docker swarm init --advertise-addr 62.52.58.58

# Criar redes
docker network create --driver overlay traefik-public
docker network create --driver overlay app-network

# Verificar
docker node ls
docker network ls
```

---

## 📁 **PASSO 3: PREPARAR ESTRUTURA**

### **3.1 Criar Diretórios**
```bash
# Criar estrutura de diretórios
mkdir -p /opt/dossie-app/{traefik/data,portainer,postgres/data,app,scripts}
cd /opt/dossie-app

# Configurar permissões
chmod 600 traefik/data
touch traefik/data/acme.json
chmod 600 traefik/data/acme.json
```

### **3.2 Transferir Código da Aplicação**

**Opção A - Via Git (se o código estiver no GitHub):**
```bash
cd /opt/dossie-app/app
git clone https://github.com/SEU_USUARIO/dossie_novo.git .
```

**Opção B - Via SCP (do seu computador local):**
```bash
# No seu computador local (não na VPS)
scp -r /caminho/para/dossie_novo/* root@62.52.58.58:/opt/dossie-app/app/
```

**Opção C - Via Upload Manual:**
```bash
# Criar arquivo temporário e colar o código
cd /opt/dossie-app/app
nano app.py  # Colar o código do app.py
# Repetir para todos os arquivos necessários
```

---

## 🌐 **PASSO 4: CONFIGURAR DOMÍNIO (OPCIONAL)**

### **4.1 Se Você Tem Domínio:**
```bash
# Configure no seu provedor de domínio:
# A    dossie.seudominio.com      → 62.52.58.58
# A    traefik.seudominio.com     → 62.52.58.58
# A    portainer.seudominio.com   → 62.52.58.58
```

### **4.2 Se NÃO Tem Domínio (Usar IP):**
```bash
# Vamos configurar para usar o IP diretamente
# Alguns ajustes serão necessários nos arquivos
```

---

## ⚙️ **PASSO 5: CRIAR ARQUIVOS DE CONFIGURAÇÃO**

### **5.1 Arquivo .env**
```bash
cd /opt/dossie-app
cat > .env << 'EOF'
# IP da VPS (sem domínio)
DOMAIN=62.52.58.58
USE_IP=true

# Email para certificados (não funcionará com IP, mas deixar)
ACME_EMAIL=admin@exemplo.com

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=Dossie@2024!Seguro

# Flask
SECRET_KEY=sua-chave-secreta-super-segura-de-32-caracteres-ou-mais-aqui
FLASK_ENV=production

# URLs
DATABASE_URL=postgresql://dossie:Dossie@2024!Seguro@postgres:5432/dossie_escola
EOF
```

### **5.2 Gerar SECRET_KEY**
```bash
# Gerar chave secreta
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copiar o resultado e substituir no .env
nano .env
```

### **5.3 Docker Compose - Traefik (Adaptado para IP)**
```bash
cat > docker-compose.traefik.yml << 'EOF'
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    command:
      - --api.dashboard=true
      - --api.insecure=true  # Para acesso via IP
      - --providers.docker=true
      - --providers.docker.swarmmode=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --log.level=INFO
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
        - traefik.http.routers.traefik.rule=Host(`62.52.58.58`)
        - traefik.http.routers.traefik.service=api@internal
        - traefik.http.services.traefik.loadbalancer.server.port=8080

networks:
  traefik-public:
    external: true
EOF
```

### **5.4 Docker Compose - Portainer**
```bash
cat > docker-compose.portainer.yml << 'EOF'
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:latest
    command: -H unix:///var/run/docker.sock
    ports:
      - "9000:9000"  # Acesso direto via IP
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
```

### **5.5 Docker Compose - PostgreSQL**
```bash
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
```

### **5.6 Dockerfile da Aplicação**
```bash
cd /opt/dossie-app/app
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p static/uploads logs
RUN chown -R app:app /app

# Mudar para usuário não-root
USER app

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
EOF
```

### **5.7 Docker Compose - Aplicação**
```bash
cd /opt/dossie-app
cat > docker-compose.app.yml << 'EOF'
version: '3.8'

services:
  dossie-app:
    build: ./app
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://dossie:Dossie@2024!Seguro@postgres:5432/dossie_escola
      - SECRET_KEY=sua-chave-secreta-super-segura-aqui
    ports:
      - "5000:5000"  # Acesso direto via IP
    volumes:
      - ./app/static/uploads:/app/static/uploads
      - ./app/logs:/app/logs
    networks:
      - traefik-public
      - app-network
    depends_on:
      - postgres
    deploy:
      replicas: 1  # Começar com 1 réplica
      restart_policy:
        condition: on-failure
      labels:
        - traefik.enable=true
        - traefik.http.routers.dossie.rule=Host(`62.52.58.58`)
        - traefik.http.services.dossie.loadbalancer.server.port=5000

networks:
  traefik-public:
    external: true
  app-network:
    external: true
EOF
```

---

## 🚀 **PASSO 6: FAZER DEPLOY**

### **6.1 Deploy dos Serviços**
```bash
cd /opt/dossie-app

# 1. Deploy Traefik
echo "🔀 Fazendo deploy do Traefik..."
docker stack deploy -c docker-compose.traefik.yml traefik

# 2. Deploy Portainer
echo "📊 Fazendo deploy do Portainer..."
docker stack deploy -c docker-compose.portainer.yml portainer

# 3. Deploy PostgreSQL
echo "🐘 Fazendo deploy do PostgreSQL..."
docker stack deploy -c docker-compose.postgres.yml postgres

# Aguardar PostgreSQL inicializar
echo "⏳ Aguardando PostgreSQL inicializar..."
sleep 30

# 4. Build e Deploy da Aplicação
echo "🏗️ Fazendo build da aplicação..."
cd app && docker build -t dossie-app:latest . && cd ..

echo "🌐 Fazendo deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie
```

### **6.2 Verificar Status**
```bash
# Verificar stacks
docker stack ls

# Verificar serviços
docker service ls

# Verificar logs
docker service logs dossie_dossie-app
docker service logs postgres_postgres
```

---

## 🔧 **PASSO 7: CONFIGURAÇÃO INICIAL**

### **7.1 Executar Migrações**
```bash
# Aguardar aplicação inicializar
sleep 60

# Executar migrações
docker exec -it $(docker ps -q -f name=dossie_dossie-app) flask db upgrade

# Se der erro, tentar:
docker service ps dossie_dossie-app
# Pegar o ID do container e executar:
# docker exec -it CONTAINER_ID flask db upgrade
```

### **7.2 Criar Usuário Admin**
```bash
# Criar usuário administrador
docker exec -it $(docker ps -q -f name=dossie_dossie-app) python -c "
from app import create_app
from models import db, Usuario, Perfil, Escola

app = create_app()
with app.app_context():
    # Criar escola padrão
    escola = Escola.query.first()
    if not escola:
        escola = Escola(nome='Escola Principal', situacao='ativa')
        db.session.add(escola)
        db.session.commit()
    
    # Criar perfil admin
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
        print('✅ Usuário admin criado: admin@escola.com / Admin@123')
    else:
        print('ℹ️ Usuário admin já existe')
"
```

---

## 🌐 **PASSO 8: ACESSAR A APLICAÇÃO**

### **8.1 URLs de Acesso**

- **📱 Aplicação Principal**: `http://62.52.58.58:5000`
- **📊 Portainer**: `http://62.52.58.58:9000`
- **🔀 Traefik Dashboard**: `http://62.52.58.58:8080`

### **8.2 Credenciais de Acesso**

**Sistema de Dossiê:**
- **Email**: `admin@escola.com`
- **Senha**: `Admin@123`

**Portainer:**
- Primeiro acesso: criar usuário admin
- Acessar: `http://62.52.58.58:9000`

### **8.3 Teste de Funcionamento**
```bash
# Testar aplicação
curl -I http://62.52.58.58:5000

# Testar Portainer
curl -I http://62.52.58.58:9000

# Verificar logs
docker service logs dossie_dossie-app --tail 20
```

---

## 🔧 **COMANDOS ÚTEIS DE MANUTENÇÃO**

### **Monitoramento:**
```bash
# Status dos serviços
docker service ls

# Logs da aplicação
docker service logs dossie_dossie-app

# Recursos do sistema
htop
df -h
```

### **Backup:**
```bash
# Backup do banco
docker exec $(docker ps -q -f name=postgres_postgres) pg_dump -U dossie dossie_escola > backup_$(date +%Y%m%d).sql

# Backup dos uploads
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz -C /opt/dossie-app/app/static uploads
```

### **Atualização:**
```bash
# Atualizar aplicação
cd /opt/dossie-app/app
git pull  # Se usando Git
docker build -t dossie-app:latest .
docker service update --image dossie-app:latest dossie_dossie-app
```

---

## ✅ **CONCLUSÃO**

🎉 **Parabéns! Sua aplicação está rodando na VPS Hostinger!**

**Acesse agora:**
- **🌐 Sistema**: http://62.52.58.58:5000
- **👤 Login**: admin@escola.com / Admin@123

**Próximos passos recomendados:**
1. **🔒 Configurar SSL** com domínio próprio
2. **📊 Configurar monitoramento** 
3. **💾 Automatizar backups**
4. **🔧 Ajustar recursos** conforme necessário

**Sua aplicação está pronta para uso! 🚀**
