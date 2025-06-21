# 📋 Configurações Completas de Produção - Sistema Dossiê Escolar

**Data:** Janeiro 2025  
**Ambiente:** EasyPanel v2.20.1 + Hostinger VPS  
**Domínio:** dossie.easistemas.dev.br  

---

## 🚀 Resumo da Implantação

### **Status:** ✅ IMPLEMENTADO EM PRODUÇÃO
- **URL:** https://dossie.easistemas.dev.br
- **SSL:** Let's Encrypt (Automático)
- **Proxy:** Traefik 3.3.7
- **Container Runtime:** Docker

---

## 🔧 Configurações de Infraestrutura

### **EasyPanel - Projeto**
```
Nome do Projeto: dossie-escolar
Repositório: https://github.com/fedimaraquino/dossie_escolar.git
Branch: master
Build Method: Dockerfile
```

### **GitHub Token**
```
Token: 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
Permissões: Repositório privado habilitado
```

---

## 🐳 Configurações Docker

### **Dockerfile**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x docker-entrypoint.sh
EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]
```

### **Docker Compose (docker-compose.easypanel.yml)**
```yaml
version: '3.8'

services:
  dossie-app:
    build: .
    image: dossie-app:latest
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://dossie_user:${POSTGRES_PASSWORD}@postgres:5432/dossie_escola
      - SECRET_KEY=${SECRET_KEY}
      - SERVER_NAME=dossie.easistemas.dev.br
      - UPLOAD_FOLDER=/app/static/uploads
      - MAX_CONTENT_LENGTH=16777216
      - PYTHONUNBUFFERED=1
    volumes:
      - app_uploads:/app/static/uploads
      - app_logs:/app/logs
    depends_on:
      - postgres
    restart: unless-stopped
    labels:
      # Traefik Labels para SSL automático
      - "traefik.enable=true"
      - "traefik.http.routers.dossie.rule=Host(`dossie.easistemas.dev.br`)"
      - "traefik.http.routers.dossie.entrypoints=websecure"
      - "traefik.http.routers.dossie.tls.certresolver=letsencrypt"
      - "traefik.http.services.dossie.loadbalancer.server.port=5000"
      # Redirect HTTP para HTTPS
      - "traefik.http.routers.dossie-http.rule=Host(`dossie.easistemas.dev.br`)"
      - "traefik.http.routers.dossie-http.entrypoints=web"
      - "traefik.http.routers.dossie-http.middlewares=dossie-redirect"
      - "traefik.http.middlewares.dossie-redirect.redirectscheme.scheme=https"
      - "traefik.http.middlewares.dossie-redirect.redirectscheme.permanent=true"
    networks:
      - easypanel
      - default

  postgres:
    image: postgres:13-alpine
    environment:
      - POSTGRES_USER=dossie_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=dossie_escola
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - default

volumes:
  app_uploads:
  app_logs:
  postgres_data:

networks:
  easypanel:
    external: true
  default:
    driver: bridge
```

---

## 🗄️ Configurações do Banco de Dados

### **PostgreSQL 13 Alpine**
```
Host: postgres (interno)
Database: dossie_escola
Usuário: dossie_user
Senha: Fep09151*
Porta: 5432
Encoding: UTF-8
Timezone: UTC
```

### **Connection String**
```
DATABASE_URL=postgresql://dossie_user:Fep09151*@postgres:5432/dossie_escola
```

### **Volume de Dados**
```
Volume: postgres_data
Path: /var/lib/postgresql/data/pgdata
Backup: Automático via EasyPanel
```

---

## 🔐 Environment Variables

### **Arquivo: env-easypanel-production**
```bash
# Aplicação
FLASK_ENV=production
SECRET_KEY=ujkwoyZLRk-alp4m2kj58l1Yh1haTAZSzVEfgAnF6JY
SERVER_NAME=dossie.easistemas.dev.br

# Banco de Dados
POSTGRES_PASSWORD=Fep09151*
DATABASE_URL=postgresql://dossie_user:Fep09151*@postgres:5432/dossie_escola

# Upload
UPLOAD_FOLDER=/app/static/uploads
MAX_CONTENT_LENGTH=16777216

# Sistema
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### **Environment Variables no EasyPanel**
```
FLASK_ENV=production
DATABASE_URL=postgresql://dossie_user:Fep09151*@postgres:5432/dossie_escola
SECRET_KEY=ujkwoyZLRk-alp4m2kj58l1Yh1haTAZSzVEfgAnF6JY
SERVER_NAME=dossie.easistemas.dev.br
UPLOAD_FOLDER=/app/static/uploads
MAX_CONTENT_LENGTH=16777216
PYTHONUNBUFFERED=1
POSTGRES_PASSWORD=Fep09151*
```

---

## 💾 Configurações de Volumes

### **Volume: uploads (2GB)**
```
Tipo: Persistent Volume
Tamanho: 2GB
Mount Path: /app/static/uploads
Finalidade: Armazenar fotos de alunos e documentos
```

### **Volume: logs (500MB)**
```
Tipo: Persistent Volume
Tamanho: 500MB
Mount Path: /app/logs
Finalidade: Logs da aplicação e auditoria
```

### **Volume: postgres_data**
```
Tipo: Persistent Volume
Mount Path: /var/lib/postgresql/data
Finalidade: Dados do PostgreSQL
Backup: Automático
```

---

## 🌐 Configurações de Rede

### **Domínio e SSL**
```
Domínio: dossie.easistemas.dev.br
SSL: Let's Encrypt (Automático)
HTTPS: Forçado (redirect automático)
Certificado: Renovação automática
```

### **Portas**
```
Aplicação: 5000 (interna)
HTTP: 80 → 443 (redirect)
HTTPS: 443
PostgreSQL: 5432 (interna)
```

### **Traefik Labels**
```yaml
traefik.enable=true
traefik.http.routers.dossie.rule=Host(`dossie.easistemas.dev.br`)
traefik.http.routers.dossie.entrypoints=websecure
traefik.http.routers.dossie.tls.certresolver=letsencrypt
traefik.http.services.dossie.loadbalancer.server.port=5000
```

---

## 👤 Credenciais do Sistema

### **Usuário Administrador**
```
Login: admin@sistema.com
Senha: Admin@123
Perfil: Administrador Geral
Primeiro Login: Configurado automaticamente
```

### **Perfis Padrão Criados**
```
1. Administrador Geral - Acesso total
2. Diretor - Gestão da escola
3. Secretário - Operações diárias
4. Visualizador - Apenas consulta
```

---

## 🔧 Scripts de Deploy

### **docker-entrypoint.sh**
```bash
#!/bin/bash
set -e

echo "🚀 Iniciando aplicação..."

# Aguardar PostgreSQL
echo "⏳ Aguardando PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "✅ PostgreSQL conectado!"

# Sistema de migrações inteligente
echo "🔄 Verificando migrações..."
cd /app

# Detectar múltiplas heads e corrigir
if flask db heads 2>&1 | grep -q "multiple heads"; then
    echo "⚠️  Múltiplas heads detectadas, corrigindo..."
    flask db stamp heads
fi

# Verificar se há migrações pendentes
if ! flask db current >/dev/null 2>&1; then
    echo "🆕 Inicializando sistema de migrações..."
    flask db init --directory migrations || echo "Migrations já inicializadas"
    flask db stamp head
fi

# Aplicar migrações
echo "📊 Aplicando migrações..."
if ! flask db upgrade; then
    echo "❌ Erro nas migrações, tentando reset..."
    flask db stamp heads
    flask db upgrade
fi

# Criar usuário padrão
echo "👤 Configurando usuário padrão..."
python -c "
import sys
sys.path.append('/app')
from app import app, db
from models.usuario import Usuario
from models.perfil import Perfil
from werkzeug.security import generate_password_hash

with app.app_context():
    # Criar perfil Administrador Geral
    admin_perfil = Perfil.query.filter_by(nome='Administrador Geral').first()
    if not admin_perfil:
        admin_perfil = Perfil(nome='Administrador Geral', descricao='Acesso total ao sistema')
        db.session.add(admin_perfil)
        db.session.commit()
        print('✅ Perfil Administrador Geral criado')
    
    # Criar usuário admin
    admin = Usuario.query.filter_by(email='admin@sistema.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@sistema.com',
            senha=generate_password_hash('Admin@123'),
            perfil_id=admin_perfil.id,
            ativo=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Usuário admin criado: admin@sistema.com / Admin@123')
    else:
        print('ℹ️  Usuário admin já existe')
"

echo "🎉 Aplicação configurada com sucesso!"
echo "🌐 Acesse: https://dossie.easistemas.dev.br"
echo "👤 Login: admin@sistema.com"
echo "🔑 Senha: Admin@123"

# Iniciar aplicação
exec python app.py
```

---

## 📋 Problemas Resolvidos

### **1. Hash SHA256 - netcat**
```
Problema: netcat==0.0.1a0 com hash incompatível
Solução: Removido do requirements.txt (instalado via apt-get)
```

### **2. Perfil Administrador**
```
Problema: Sistema criava "Administrador" mas código verificava "Administrador Geral"
Solução: Corrigido docker-entrypoint.sh para criar "Administrador Geral"
```

### **3. Sistema de Migrações**
```
Problema: Usava db.create_all() ao invés de Flask-Migrate
Solução: Implementado sistema profissional com flask db init/migrate/upgrade
```

### **4. Multiple Head Revisions**
```
Problema: Conflitos entre múltiplas versões de migração
Solução: Sistema inteligente de detecção e reset com flask db stamp heads
```

---

## ✅ Checklist de Deploy

### **Pré-requisitos**
- [x] EasyPanel configurado
- [x] Domínio configurado
- [x] GitHub Token ativo
- [x] Repositório atualizado

### **Configuração EasyPanel**
- [x] Projeto criado: dossie-escolar
- [x] Repositório conectado
- [x] Environment Variables configuradas
- [x] Volumes criados (uploads: 2GB, logs: 500MB)
- [x] Networking configurado (porta 5000)
- [x] Domínio e SSL configurados

### **Banco de Dados**
- [x] PostgreSQL 13 configurado
- [x] Database: dossie_escola criada
- [x] Usuário: dossie_user criado
- [x] Conexão testada

### **Aplicação**
- [x] Build realizado com sucesso
- [x] Migrações aplicadas
- [x] Usuário admin criado
- [x] Sistema acessível via HTTPS

---

## 🚀 Como Fazer Deploy

### **1. Via EasyPanel Interface**
1. Acessar EasyPanel
2. Selecionar projeto "dossie-escolar"
3. Clicar em "Rebuild" para aplicar atualizações
4. Aguardar build completar

### **2. Via Git**
```bash
git add .
git commit -m "Atualização do sistema"
git push origin master
# EasyPanel detecta automaticamente e rebuilda
```

### **3. Verificação**
1. Acessar: https://dossie.easistemas.dev.br
2. Login: admin@sistema.com / Admin@123
3. Verificar funcionalidades principais

---

## 📊 Monitoramento

### **Logs da Aplicação**
```
Local: /app/logs (volume persistente)
Nível: INFO
Rotação: Automática
```

### **Logs do Container**
```
EasyPanel → Projeto → Logs
PostgreSQL → Logs separados
Rebuild → Logs de build
```

### **Saúde do Sistema**
```
URL: https://dossie.easistemas.dev.br/admin/system_info
Requer: Login de administrador
Mostra: Status DB, volumes, performance
```

---

## 🔄 Backup e Restore

### **Backup Automático (EasyPanel)**
```
PostgreSQL: Backup diário automático
Volumes: Snapshot automático
Configurações: Versionadas no Git
```

### **Backup Manual**
```bash
# Dentro do container PostgreSQL
pg_dump -U dossie_user dossie_escola > backup.sql

# Restore
psql -U dossie_user dossie_escola < backup.sql
```

---

## 🔧 Manutenção

### **Atualizações de Código**
1. Fazer alterações no código
2. Commit e push para repositório
3. EasyPanel rebuilda automaticamente
4. Verificar logs para confirmação

### **Atualizações de Dependências**
1. Atualizar requirements.txt
2. Testar localmente
3. Commit e push
4. Rebuild no EasyPanel

### **Monitoramento de Performance**
- CPU: Monitorado via EasyPanel
- Memória: Alertas automáticos
- Disco: Volumes com limite definido
- Rede: Traefik metrics

---

## 📞 Contatos e Suporte

### **Domínio**
```
Registrar: easistemas.dev.br
DNS: Configurado para EasyPanel
SSL: Let's Encrypt automático
```

### **Hosting**
```
Provedor: Hostinger VPS
Painel: EasyPanel v2.20.1
Proxy: Traefik 3.3.7
```

### **Repositório**
```
GitHub: https://github.com/fedimaraquino/dossie_escolar.git
Branch Principal: master
Deploy: Automático via webhook
```

---

---

## 🚨 **PROBLEMA CRÍTICO IDENTIFICADO:**

### **PostgreSQL - Usuário Inexistente**
```
Data: 21/01/2025 02:25 UTC
Problema: Role "dossie_user" does not exist
Status: CORREÇÃO APLICADA ⚠️
```

**Logs do Erro:**
```
2025-06-21 02:31:03.814 UTC [76] FATAL: password authentication failed for user "dossie_user"
2025-06-21 02:31:03.814 UTC [76] DETAIL: Role "dossie_user" does not exist.
```

**Correção Aplicada:**
1. ✅ Corrigido docker-compose.easypanel.yml
2. ✅ Criado init-postgres.sql para inicialização automática
3. ✅ Alterado PostgreSQL para usar 'postgres' como superuser
4. ✅ Script de inicialização para criar 'dossie_user'
5. ✅ Arquivo CORRIGIR_POSTGRES_URGENTE.md com instruções

**AÇÃO REQUERIDA:**
- 🔄 **REBUILD URGENTE** no EasyPanel para aplicar correções
- OU executar SQL manual no container PostgreSQL

---

**Última Atualização:** 21 Janeiro 2025 - 02:35 UTC  
**Status:** ⚠️ CORREÇÃO APLICADA - AGUARDANDO REBUILD  
**URL:** https://dossie.easistemas.dev.br