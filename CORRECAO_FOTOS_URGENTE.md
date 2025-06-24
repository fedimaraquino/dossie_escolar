# 🚨 CORREÇÃO URGENTE - FOTOS SENDO APAGADAS

## 📋 RESUMO EXECUTIVO

**Problema**: Fotos dos usuários desaparecem após restart do container  
**Causa**: Problema de persistência de volumes Docker  
**Solução**: Correção de configuração de volumes e permissões  
**Tempo estimado**: 10-15 minutos  
**Impacto**: Fotos existentes serão preservadas  

---

## 🔍 DIAGNÓSTICO RÁPIDO

### Verificar se é problema de volume:
```bash
# 1. Verificar volumes existentes
docker volume ls

# 2. Verificar se o volume app_uploads existe
docker volume ls | grep app_uploads

# 3. Verificar montagem no container
docker inspect CONTAINER_ID | grep -A 10 "Mounts"
```

### Verificar fotos atuais:
```bash
# 4. Verificar fotos no container
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos

# 5. Verificar fotos no volume
docker run --rm -v app_uploads:/data alpine ls -la /data/fotos
```

---

## 🔧 CORREÇÃO IMEDIATA

### Passo 1: Backup das Fotos (IMPORTANTE!)
```bash
# Criar backup das fotos atuais
docker exec -it CONTAINER_ID tar -czf /tmp/fotos_backup.tar.gz /app/static/uploads/fotos

# Copiar backup para host
docker cp CONTAINER_ID:/tmp/fotos_backup.tar.gz ./fotos_backup_$(date +%Y%m%d_%H%M%S).tar.gz
```

### Passo 2: Parar Aplicação
```bash
# Parar containers
docker-compose down
```

### Passo 3: Verificar Configuração
```bash
# Verificar se o docker-compose.yml tem volumes corretos
cat docker-compose.yml | grep -A 5 "volumes:"
```

### Passo 4: Aplicar Correção
```bash
# Reconstruir imagem (força rebuild)
docker-compose build --no-cache

# Iniciar com nova configuração
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

### Passo 5: Restaurar Fotos
```bash
# Restaurar fotos do backup
docker cp ./fotos_backup_*.tar.gz CONTAINER_ID:/tmp/
docker exec -it CONTAINER_ID tar -xzf /tmp/fotos_backup_*.tar.gz -C /

# Verificar se as fotos foram restauradas
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos
```

---

## 📝 CONFIGURAÇÃO CORRETA

### docker-compose.yml (Versão Corrigida):
```yaml
version: '3.8'

services:
  dossie-app:
    build: .
    image: dossie-app:local
    environment:
      - DATABASE_URL=postgresql://dossie_user:Fep09151*@dossie_db:5432/dossie_escola
      - SECRET_KEY=uma-chave-secreta-forte-para-desenvolvimento-local
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - UPLOAD_FOLDER=/app/static/uploads  # ✅ ADICIONADO
    ports:
      - "8000:8000"
    volumes:
      - app_uploads:/app/static/uploads:rw  # ✅ MODO RW EXPLÍCITO
      - app_logs:/app/instance/logs:rw
    depends_on:
      - dossie_db
    restart: unless-stopped  # ✅ RESTART POLICY

  dossie_db:
    image: postgres:13
    environment:
      - POSTGRES_USER=dossie_user
      - POSTGRES_PASSWORD=Fep09151*
      - POSTGRES_DB=dossie_escola
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  app_uploads:
    driver: local  # ✅ DRIVER EXPLÍCITO
  app_logs:
    driver: local
  postgres_data:
    driver: local
```

---

## ✅ TESTE DE VALIDAÇÃO

### Teste 1: Verificar Persistência
```bash
# 1. Fazer upload de uma foto via interface web
# 2. Verificar se a foto aparece
# 3. Reiniciar container: docker-compose restart dossie-app
# 4. Verificar se a foto ainda aparece
```

### Teste 2: Verificar Volume
```bash
# Verificar se o volume está sendo usado
docker volume inspect app_uploads

# Verificar conteúdo do volume
docker run --rm -v app_uploads:/data alpine ls -la /data/fotos
```

### Teste 3: Verificar Permissões
```bash
# Verificar permissões no container
docker exec -it CONTAINER_ID ls -la /app/static/uploads

# Verificar usuário da aplicação
docker exec -it CONTAINER_ID whoami
```

---

## 🆘 EM CASO DE PROBLEMAS

### Problema: Volume não existe
```bash
# Criar volume manualmente
docker volume create app_uploads

# Verificar se foi criado
docker volume ls | grep app_uploads
```

### Problema: Permissões incorretas
```bash
# Corrigir permissões no container
docker exec -it CONTAINER_ID chmod -R 755 /app/static/uploads

# Verificar permissões
docker exec -it CONTAINER_ID ls -la /app/static/uploads
```

### Problema: Fotos não aparecem
```bash
# Verificar logs da aplicação
docker-compose logs dossie-app

# Verificar se o diretório existe
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos
```

### Problema: Volume corrompido
```bash
# Parar aplicação
docker-compose down

# Remover volume (CUIDADO: perde dados)
docker volume rm app_uploads

# Recriar volume
docker volume create app_uploads

# Reiniciar aplicação
docker-compose up -d
```

---

## 📊 MONITORAMENTO

### Comandos de Verificação:
```bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f dossie-app

# Uso de volumes
docker system df -v

# Espaço em disco
docker exec -it CONTAINER_ID df -h
```

### Indicadores de Sucesso:
- ✅ `docker volume ls` mostra `app_uploads`
- ✅ Fotos permanecem após restart
- ✅ Novos uploads funcionam
- ✅ Permissões corretas (755)

---

## 🔄 PROCEDIMENTO DE RECUPERAÇÃO

### Se tudo falhar:
```bash
# 1. Parar tudo
docker-compose down

# 2. Backup manual das fotos
sudo cp -r /var/lib/docker/volumes/app_uploads/_data ./backup_fotos_manual

# 3. Limpar volumes
docker volume rm app_uploads app_logs

# 4. Recriar tudo
docker-compose up -d

# 5. Restaurar fotos
sudo cp -r ./backup_fotos_manual/* /var/lib/docker/volumes/app_uploads/_data/
```

---

## 📞 SUPORTE

**Documentação completa**: `step-by-step/correcao_persistencia_fotos.md`  
**Script de backup**: Backup automático das fotos  
**Configuração**: Volumes persistentes configurados  

---

**⚠️ IMPORTANTE**: Sempre faça backup antes de qualquer alteração!  
**🕐 Tempo**: 10-15 minutos para correção completa  
**🔄 Impacto**: Fotos existentes serão preservadas, novos uploads funcionarão 