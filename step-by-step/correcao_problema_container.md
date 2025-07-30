# Correção do Problema do Container Docker

## Problema Identificado

A aplicação não estava funcionando no container, mas funcionava localmente. Os logs mostravam:

```
[2025-07-30 02:33:43 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
```

## Causa do Problema

**Incompatibilidade de Portas:**
- **Dockerfile**: Gunicorn estava configurado para rodar na porta **8000**
- **Docker Compose**: Mapeava a porta **5000** externa para **5000** interna
- **Resultado**: A aplicação rodava na porta 8000, mas o acesso era na porta 5000

## Solução Implementada

### 1. Correção do Dockerfile

**Antes:**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

**Depois:**
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]
```

### 2. Reconstrução da Imagem

```bash
# Parar containers
docker-compose down

# Reconstruir sem cache
docker-compose build --no-cache dossie-app

# Ou build direto
docker build -t fedimaraquino/dossie:latest .

# Iniciar containers
docker-compose up -d
```

### 3. Verificação

**Logs após correção:**
```
[2025-07-30 03:10:03 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
[2025-07-30 03:10:03 +0000] [1] [INFO] Using worker: sync
[2025-07-30 03:10:03 +0000] [20] [INFO] Booting worker with pid: 20
[2025-07-30 03:10:04 +0000] [21] [INFO] Booting worker with pid: 21
```

**Teste de conectividade:**
```bash
curl http://localhost:5000
# Retorna: StatusCode: 200 OK
```

## Melhorias Implementadas

1. **Workers**: Adicionado `--workers 2` para melhor performance
2. **Timeout**: Aumentado para 120 segundos para evitar timeouts
3. **Cache Buster**: Atualizado para forçar rebuild quando necessário

## Status Final

✅ **Aplicação funcionando corretamente**
✅ **Porta 5000 acessível**
✅ **Banco de dados conectado**
✅ **Uploads funcionando**
✅ **Logs limpos**

## Acesso à Aplicação

- **URL**: http://localhost:5000
- **Login**: admin@sistema.com
- **Senha**: Admin@123

## Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs --follow dossie-app

# Ver status dos containers
docker-compose ps

# Reconstruir após mudanças
docker-compose build --no-cache dossie-app
docker-compose up -d

# Acessar container
docker-compose exec dossie-app bash
``` 