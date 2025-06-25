# Configuração de Volumes Persistentes no EasyPanel - Sistema de Controle de Dossiê Escolar

## Data da Implementação
**27/01/2025**

## Problema Identificado
Como configurar os volumes persistentes no EasyPanel para garantir que as fotos dos usuários não sejam perdidas após reinicialização dos containers.

## Arquivos Envolvidos
- `docker-compose.easypanel.yml` - Configuração Docker para EasyPanel
- `step-by-step/configuracao_volumes_easypanel.md` - Este guia
- Interface web do EasyPanel

## Visão Geral da Solução
Configuração manual dos volumes persistentes através da interface web do EasyPanel para garantir persistência dos arquivos estáticos.

## Configuração no EasyPanel

### 1. Acessar o EasyPanel

#### URL de Acesso:
```
https://seu-servidor:8080
# ou
http://seu-servidor:8080
```

#### Credenciais:
- **Usuário**: admin (ou seu usuário configurado)
- **Senha**: (sua senha do EasyPanel)

### 2. Localizar o Projeto

#### Navegação:
1. **Dashboard** → **Projects**
2. **Encontrar o projeto**: `dossie-app` ou `dossie`
3. **Clicar no projeto** para acessar detalhes

### 3. Configurar Volumes

#### Passo 1: Acessar Configurações
1. **Clicar em "Settings"** ou "Configurações"
2. **Selecionar "Volumes"** ou "Storage"
3. **Verificar volumes existentes**

#### Passo 2: Criar Volumes Necessários

##### Volume 1: app_uploads
```
Nome: app_uploads
Tipo: Local Volume
Driver: local
Caminho: /var/lib/docker/volumes/app_uploads/_data
```

##### Volume 2: app_logs
```
Nome: app_logs
Tipo: Local Volume
Driver: local
Caminho: /var/lib/docker/volumes/app_logs/_data
```

##### Volume 3: app_static
```
Nome: app_static
Tipo: Local Volume
Driver: local
Caminho: /var/lib/docker/volumes/app_static/_data
```

##### Volume 4: postgres_data
```
Nome: postgres_data
Tipo: Local Volume
Driver: local
Caminho: /var/lib/docker/volumes/postgres_data/_data
```

### 4. Configurar Mapeamento de Volumes

#### Passo 1: Acessar Docker Compose
1. **Ir para "Docker Compose"** ou "Compose"
2. **Editar o arquivo** `docker-compose.yml`

#### Passo 2: Verificar Configuração Atual
```yaml
services:
  dossie-app:
    # ... outras configurações ...
    volumes:
      - app_uploads:/app/static/uploads:rw
      - app_logs:/app/logs:rw
      - app_static:/app/static:rw
    # ... outras configurações ...

  postgres:
    # ... outras configurações ...
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # ... outras configurações ...

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

#### Passo 3: Aplicar Configuração
1. **Salvar** as alterações
2. **Deploy** ou "Redeploy" o projeto
3. **Aguardar** a aplicação reiniciar

### 5. Verificar Configuração

#### Comandos SSH (se necessário):
```bash
# Conectar via SSH ao servidor
ssh root@seu-servidor

# Verificar volumes criados
docker volume ls | grep -E "(app_uploads|app_logs|app_static|postgres_data)"

# Verificar montagem nos containers
docker ps
docker inspect CONTAINER_ID | grep -A 10 "Mounts"

# Verificar conteúdo dos volumes
docker run --rm -v app_uploads:/data alpine ls -la /data
```

## Interface Web do EasyPanel

### Localização dos Menus:

#### 1. Dashboard Principal
```
📊 Dashboard
├── 📁 Projects (Projetos)
├── 🔧 Settings (Configurações)
├── 📊 Monitoring (Monitoramento)
└── 👤 User Management (Usuários)
```

#### 2. Configurações do Projeto
```
📁 Projeto: dossie-app
├── 🚀 Deploy (Implantar)
├── ⚙️ Settings (Configurações)
├── 📋 Logs (Registros)
├── 🔄 Redeploy (Reimplantar)
└── 🗑️ Delete (Excluir)
```

#### 3. Configurações de Volumes
```
⚙️ Settings
├── 📦 Volumes (Volumes)
├── 🌐 Networks (Redes)
├── 🔐 Environment (Variáveis)
└── 📁 Files (Arquivos)
```

## Configuração Manual via SSH

### Se a interface web não permitir:

#### Passo 1: Conectar via SSH
```bash
ssh root@seu-servidor
```

#### Passo 2: Navegar para o projeto
```bash
cd /opt/easypanel/projects/dossie-app
# ou
cd /var/lib/easypanel/projects/dossie-app
```

#### Passo 3: Criar volumes manualmente
```bash
# Criar volumes
docker volume create app_uploads
docker volume create app_logs
docker volume create app_static
docker volume create postgres_data

# Verificar criação
docker volume ls | grep -E "(app_uploads|app_logs|app_static|postgres_data)"
```

#### Passo 4: Editar docker-compose.yml
```bash
# Editar arquivo
nano docker-compose.yml

# Verificar se os volumes estão configurados corretamente
# Salvar e sair (Ctrl+X, Y, Enter)
```

#### Passo 5: Redeploy
```bash
# Parar containers
docker-compose down

# Iniciar com nova configuração
docker-compose up -d

# Verificar status
docker-compose ps
```

## Verificação de Funcionamento

### Teste 1: Verificar Volumes
```bash
# Listar volumes
docker volume ls

# Verificar detalhes
docker volume inspect app_uploads
```

### Teste 2: Verificar Montagem
```bash
# Verificar containers
docker ps

# Verificar mounts
docker inspect CONTAINER_ID | grep -A 10 "Mounts"
```

### Teste 3: Teste de Persistência
```bash
# 1. Fazer upload de uma foto via interface web
# 2. Verificar se a foto aparece
# 3. Reiniciar container via EasyPanel
# 4. Verificar se a foto ainda aparece
```

### Teste 4: Verificar Diretórios
```bash
# Verificar diretórios no container
docker exec -it CONTAINER_ID ls -la /app/static/uploads/

# Verificar permissões
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos/
```

## Troubleshooting

### Problema: Volumes não aparecem no EasyPanel
```bash
# Verificar se o EasyPanel tem permissão
sudo chown -R easypanel:easypanel /var/lib/docker/volumes/

# Reiniciar EasyPanel
sudo systemctl restart easypanel
```

### Problema: Volumes não são montados
```bash
# Verificar se os volumes existem
docker volume ls

# Recriar volumes se necessário
docker volume rm app_uploads app_logs app_static
docker volume create app_uploads app_logs app_static
```

### Problema: Permissões incorretas
```bash
# Corrigir permissões
docker exec -it CONTAINER_ID chmod -R 755 /app/static/uploads

# Verificar proprietário
docker exec -it CONTAINER_ID ls -la /app/static/uploads/
```

### Problema: EasyPanel não reconhece alterações
```bash
# Forçar redeploy
# 1. Parar projeto no EasyPanel
# 2. Aguardar 30 segundos
# 3. Iniciar projeto novamente
```

## Comandos Úteis

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

## Próximos Passos

### Imediatos:
1. ✅ Configurar volumes no EasyPanel
2. ✅ Testar persistência de fotos
3. ✅ Validar funcionamento completo

### Preventivos:
1. **Configurar backup automático** dos volumes
2. **Implementar monitoramento** de espaço
3. **Documentar procedimento** de recuperação

### Melhorias:
1. **Implementar CDN** para fotos
2. **Configurar cache** de imagens
3. **Otimizar tamanho** das fotos

---

**Status**: ✅ **IMPLEMENTADO**  
**Última atualização**: 27/01/2025  
**Próxima revisão**: Após configuração no EasyPanel 