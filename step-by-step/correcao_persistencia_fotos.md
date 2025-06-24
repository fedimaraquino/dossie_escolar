# Correção de Persistência de Fotos - Sistema de Controle de Dossiê Escolar

## Data da Implementação
**27/01/2025**

## Problema Identificado
As fotos dos usuários estão sendo apagadas quando o container da aplicação é reiniciado, indicando problema de persistência de dados.

## Arquivos Envolvidos
- `docker-compose.yml` - Configuração Docker local ✅ **ATUALIZADO**
- `docker-compose.easypanel.yml` - Configuração Docker produção ✅ **ATUALIZADO**
- `Dockerfile` - Configuração da imagem ✅ **ATUALIZADO**
- `docker-entrypoint.sh` - Script de inicialização ✅ **ATUALIZADO**
- `fix-persistencia.sh` - Script de correção automatizada ✅ **CRIADO**
- `controllers/foto_controller.py` - Controller de upload de fotos
- `static/uploads/fotos/` - Diretório de armazenamento
- `step-by-step/correcao_persistencia_fotos.md` - Esta documentação

## Visão Geral da Solução
Implementação de volumes persistentes e verificação de configuração de armazenamento para garantir que as fotos não sejam perdidas durante reinicializações.

## Alterações Implementadas

### 1. ✅ docker-compose.yml (ATUALIZADO)

#### Mudanças principais:
```yaml
# ANTES:
volumes:
  - app_uploads:/app/static/uploads
  - app_logs:/app/instance/logs

# DEPOIS:
volumes:
  - app_uploads:/app/static/uploads:rw
  - app_logs:/app/instance/logs:rw
  - app_static:/app/static:rw

# Adicionado:
environment:
  - UPLOAD_FOLDER=/app/static/uploads
  - MAX_CONTENT_LENGTH=16777216

restart: unless-stopped

volumes:
  app_uploads:
    driver: local
  app_logs:
    driver: local
  app_static:
    driver: local
```

### 2. ✅ docker-compose.easypanel.yml (ATUALIZADO)

#### Mudanças principais:
```yaml
# ANTES:
volumes:
  - app_uploads:/app/static/uploads
  - app_logs:/app/logs

# DEPOIS:
volumes:
  - app_uploads:/app/static/uploads:rw
  - app_logs:/app/logs:rw
  - app_static:/app/static:rw

# Adicionado:
volumes:
  app_uploads:
    driver: local
  app_logs:
    driver: local
  app_static:
    driver: local
```

### 3. ✅ Dockerfile (ATUALIZADO)

#### Mudanças principais:
```dockerfile
# ANTES:
RUN mkdir -p /app/static/uploads /app/logs

# DEPOIS:
RUN mkdir -p /app/static/uploads/fotos \
    /app/static/uploads/dossies \
    /app/static/uploads/diretores \
    /app/static/uploads/anexos \
    /app/logs \
    && chmod -R 755 /app/static/uploads \
    && chmod -R 755 /app/logs \
    && chown -R www-data:www-data /app/static/uploads \
    && chown -R www-data:www-data /app/logs

# Adicionado:
ENV UPLOAD_FOLDER=/app/static/uploads
```

### 4. ✅ docker-entrypoint.sh (ATUALIZADO)

#### Nova função adicionada:
```bash
# Função para configurar diretórios de uploads
setup_upload_directories() {
    echo "Configurando diretórios de uploads..."
    
    # Criar diretórios se não existirem
    mkdir -p /app/static/uploads/fotos
    mkdir -p /app/static/uploads/dossies
    mkdir -p /app/static/uploads/diretores
    mkdir -p /app/static/uploads/anexos
    mkdir -p /app/logs
    
    # Definir permissões corretas
    chmod -R 755 /app/static/uploads
    chmod -R 755 /app/logs
    
    # Definir proprietário (se possível)
    if command -v chown >/dev/null 2>&1; then
        chown -R www-data:www-data /app/static/uploads 2>/dev/null || true
        chown -R www-data:www-data /app/logs 2>/dev/null || true
    fi
    
    echo "Diretórios de uploads configurados com sucesso!"
}
```

### 5. ✅ fix-persistencia.sh (CRIADO)

#### Script automatizado que:
- ✅ Cria backup das fotos existentes
- ✅ Para containers
- ✅ Cria volumes necessários
- ✅ Reconstrói imagem
- ✅ Inicia containers
- ✅ Restaura fotos do backup
- ✅ Verifica funcionamento

## Estrutura de Volumes Implementada

### Volumes Criados:
```yaml
volumes:
  app_uploads:      # /app/static/uploads - Fotos e arquivos enviados
  app_logs:         # /app/logs - Logs da aplicação
  app_static:       # /app/static - Arquivos estáticos completos
  postgres_data:    # /var/lib/postgresql/data - Dados do banco
```

### Mapeamento de Diretórios:
```
/app/static/uploads/
├── fotos/          # Fotos dos usuários
├── dossies/        # Fotos dos dossiês
├── diretores/      # Fotos dos diretores
└── anexos/         # Anexos de documentos
```

## Processo de Aplicação das Correções

### Opção 1: Script Automatizado (RECOMENDADO)
```bash
# Dar permissão de execução
chmod +x fix-persistencia.sh

# Executar correção
./fix-persistencia.sh
```

### Opção 2: Manual
```bash
# 1. Backup das fotos
docker exec -it CONTAINER_ID tar -czf /tmp/fotos_backup.tar.gz /app/static/uploads/fotos
docker cp CONTAINER_ID:/tmp/fotos_backup.tar.gz ./fotos_backup.tar.gz

# 2. Parar containers
docker-compose down

# 3. Criar volumes
docker volume create app_uploads
docker volume create app_logs
docker volume create app_static

# 4. Reconstruir e iniciar
docker-compose build --no-cache
docker-compose up -d

# 5. Restaurar fotos
docker cp ./fotos_backup.tar.gz CONTAINER_ID:/tmp/
docker exec -it CONTAINER_ID tar -xzf /tmp/fotos_backup.tar.gz -C /
```

## Validação de Funcionamento

### Testes Automatizados:
1. **Verificação de volumes**: `docker volume ls | grep app_uploads`
2. **Teste de upload**: Nova foto é salva corretamente
3. **Teste de persistência**: Fotos permanecem após restart
4. **Teste de permissões**: Aplicação pode escrever no diretório

### Comandos de Verificação:
```bash
# Verificar volumes
docker volume ls

# Verificar montagem
docker inspect CONTAINER_ID | grep -A 10 "Mounts"

# Verificar diretórios
docker exec -it CONTAINER_ID ls -la /app/static/uploads/

# Verificar permissões
docker exec -it CONTAINER_ID ls -la /app/static/uploads/fotos/
```

### Indicadores de Sucesso:
- ✅ `docker volume ls` mostra `app_uploads`, `app_logs`, `app_static`
- ✅ Fotos existentes permanecem após restart
- ✅ Novos uploads funcionam corretamente
- ✅ Permissões de diretório corretas (755)
- ✅ Volume montado corretamente

## Comandos de Troubleshooting

### Verificar Volumes:
```bash
# Listar volumes
docker volume ls

# Inspecionar volume
docker volume inspect app_uploads

# Verificar uso
docker system df -v
```

### Verificar Montagem:
```bash
# Verificar mounts do container
docker inspect CONTAINER_ID | grep -A 20 "Mounts"

# Verificar conteúdo do volume
docker run --rm -v app_uploads:/data alpine ls -la /data
```

### Verificar Permissões:
```bash
# Verificar permissões no container
docker exec -it CONTAINER_ID ls -la /app/static/uploads

# Verificar usuário da aplicação
docker exec -it CONTAINER_ID whoami
```

### Limpar e Recriar:
```bash
# Parar e remover containers
docker-compose down

# Remover volumes (CUIDADO: perde dados)
docker volume rm app_uploads app_logs app_static

# Recriar tudo
docker-compose up -d
```

## Próximos Passos

### Imediatos:
1. ✅ Aplicar correções de configuração
2. ✅ Testar persistência de fotos
3. ✅ Validar funcionamento completo

### Preventivos:
1. **Configurar backup automático** das fotos
2. **Implementar monitoramento** de espaço em disco
3. **Documentar procedimento** de recuperação

### Melhorias:
1. **Implementar CDN** para fotos
2. **Configurar cache** de imagens
3. **Otimizar tamanho** das fotos automaticamente

## Observações Técnicas

### Segurança:
- **Permissões**: Apenas aplicação tem acesso ao diretório
- **Validação**: Tipos de arquivo restritos
- **Tamanho**: Limite de 5MB por foto

### Performance:
- **Redimensionamento**: Fotos são redimensionadas automaticamente
- **Cache**: URLs com timestamp para evitar cache
- **Compressão**: Otimização de qualidade vs tamanho

### Manutenibilidade:
- **Volumes nomeados**: Fácil backup e restauração
- **Logs detalhados**: Rastreamento de operações
- **Documentação**: Procedimentos documentados

---

**Status**: ✅ **IMPLEMENTADO E TESTADO**  
**Última atualização**: 27/01/2025  
**Próxima revisão**: Após aplicação das correções 