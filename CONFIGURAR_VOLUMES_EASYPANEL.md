# 🔧 CONFIGURAR VOLUMES PERSISTENTES NO EASYPANEL

## 📋 RESUMO EXECUTIVO

**Objetivo**: Configurar volumes persistentes no EasyPanel para fotos dos usuários  
**Problema**: Fotos desaparecem após restart dos containers  
**Solução**: Configuração de volumes via interface web do EasyPanel  
**Tempo estimado**: 15-20 minutos  

---

## 🌐 ACESSO AO EASYPANEL

### URL de Acesso:
```
https://seu-servidor:8080
# ou
http://seu-servidor:8080
```

### Credenciais:
- **Usuário**: admin (ou seu usuário)
- **Senha**: (sua senha do EasyPanel)

---

## 📁 NAVEGAÇÃO NO EASYPANEL

### 1. Dashboard Principal
```
📊 Dashboard
└── 📁 Projects (Projetos)
```

### 2. Projeto Dossiê
```
📁 Projeto: dossie-app
├── 🚀 Deploy
├── ⚙️ Settings ← CLICAR AQUI
├── 📋 Logs
└── 🔄 Redeploy
```

### 3. Configurações
```
⚙️ Settings
├── 📦 Volumes ← CLICAR AQUI
├── 🌐 Networks
├── 🔐 Environment
└── 📁 Files
```

---

## 🔧 CONFIGURAÇÃO DOS VOLUMES

### Passo 1: Criar Volumes

#### Volume 1: app_uploads
```
Nome: app_uploads
Tipo: Local Volume
Driver: local
Descrição: Fotos e arquivos enviados pelos usuários
```

#### Volume 2: app_logs
```
Nome: app_logs
Tipo: Local Volume
Driver: local
Descrição: Logs da aplicação
```

#### Volume 3: app_static
```
Nome: app_static
Tipo: Local Volume
Driver: local
Descrição: Arquivos estáticos completos
```

#### Volume 4: postgres_data
```
Nome: postgres_data
Tipo: Local Volume
Driver: local
Descrição: Dados do banco PostgreSQL
```

### Passo 2: Verificar Docker Compose

#### Configuração Correta:
```yaml
services:
  dossie-app:
    volumes:
      - app_uploads:/app/static/uploads:rw
      - app_logs:/app/logs:rw
      - app_static:/app/static:rw

  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  app_uploads:
    driver: local
  app_logs:
    driver: local
  app_static:
    driver: local
  postgres_data:
    driver: local
```

### Passo 3: Aplicar Configuração
1. **Salvar** as alterações
2. **Clicar em "Deploy"** ou "Redeploy"
3. **Aguardar** a aplicação reiniciar (2-3 minutos)

---

## 🖥️ CONFIGURAÇÃO VIA SSH (ALTERNATIVA)

### Se a interface web não permitir:

```bash
# 1. Conectar via SSH
ssh root@seu-servidor

# 2. Criar volumes manualmente
docker volume create app_uploads
docker volume create app_logs
docker volume create app_static
docker volume create postgres_data

# 3. Verificar criação
docker volume ls | grep -E "(app_uploads|app_logs|app_static|postgres_data)"

# 4. Navegar para o projeto
cd /opt/easypanel/projects/dossie-app
# ou
cd /var/lib/easypanel/projects/dossie-app

# 5. Editar docker-compose.yml
nano docker-compose.yml

# 6. Redeploy
docker-compose down
docker-compose up -d
```

---

## ✅ VERIFICAÇÃO DE FUNCIONAMENTO

### Teste 1: Verificar Volumes
```bash
# Via SSH
docker volume ls | grep -E "(app_uploads|app_logs|app_static|postgres_data)"
```

### Teste 2: Verificar Montagem
```bash
# Verificar containers
docker ps

# Verificar mounts
docker inspect CONTAINER_ID | grep -A 10 "Mounts"
```

### Teste 3: Teste de Persistência
```
1. Fazer upload de uma foto via interface web
2. Verificar se a foto aparece
3. Reiniciar container via EasyPanel
4. Verificar se a foto ainda aparece
```

### Teste 4: Verificar Diretórios
```bash
# Verificar diretórios no container
docker exec -it CONTAINER_ID ls -la /app/static/uploads/

# Verificar permissões
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos/
```

---

## 🆘 TROUBLESHOOTING

### Problema: Volumes não aparecem no EasyPanel
```bash
# Verificar permissões
sudo chown -R easypanel:easypanel /var/lib/docker/volumes/

# Reiniciar EasyPanel
sudo systemctl restart easypanel
```

### Problema: Volumes não são montados
```bash
# Verificar se existem
docker volume ls

# Recriar se necessário
docker volume rm app_uploads app_logs app_static
docker volume create app_uploads app_logs app_static
```

### Problema: Permissões incorretas
```bash
# Corrigir permissões
docker exec -it CONTAINER_ID chmod -R 755 /app/static/uploads
```

### Problema: EasyPanel não reconhece alterações
```
1. Parar projeto no EasyPanel
2. Aguardar 30 segundos
3. Iniciar projeto novamente
```

---

## 📊 COMANDOS ÚTEIS

### Verificação de Status:
```bash
# Status dos containers
docker-compose ps

# Logs da aplicação
docker-compose logs -f dossie-app

# Uso de volumes
docker system df -v
```

### Backup de Volumes:
```bash
# Backup do volume de uploads
docker run --rm -v app_uploads:/data -v $(pwd):/backup alpine tar -czf /backup/app_uploads_backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v app_uploads:/data -v $(pwd):/backup alpine tar -xzf /backup/app_uploads_backup.tar.gz -C /data
```

---

## 🎯 INDICADORES DE SUCESSO

### ✅ Configuração Correta:
- Volumes aparecem no EasyPanel
- Containers iniciam sem erro
- Fotos permanecem após restart
- Permissões corretas (755)

### ✅ Funcionamento:
- Upload de fotos funciona
- Fotos aparecem na interface
- Persistência após reinicialização
- Logs sem erros de permissão

---

## 📞 SUPORTE

**Documentação completa**: `step-by-step/configuracao_volumes_easypanel.md`  
**Configuração Docker**: `docker-compose.easypanel.yml`  
**Interface Web**: EasyPanel Dashboard  

---

**⚠️ IMPORTANTE**: Sempre faça backup antes de alterar volumes!  
**🕐 Tempo**: 15-20 minutos para configuração completa  
**🔄 Impacto**: Fotos existentes serão preservadas, novos uploads funcionarão 