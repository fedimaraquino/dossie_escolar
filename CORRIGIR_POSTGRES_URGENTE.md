# 🚨 CORREÇÃO URGENTE - PostgreSQL Usuario Inexistente

## ❌ PROBLEMA:
O PostgreSQL está rodando, mas o usuário `dossie_user` não existe, causando falhas de autenticação.

## ✅ SOLUÇÃO RÁPIDA:

### **1. No EasyPanel - Executar SQL Manualmente**

Acesse o container PostgreSQL e execute:

```sql
-- Conectar como usuário postgres
psql -U postgres

-- Criar usuário dossie_user
CREATE USER dossie_user WITH PASSWORD 'Fep09151*';

-- Criar database
CREATE DATABASE dossie_escola OWNER dossie_user;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie_user;
GRANT CONNECT ON DATABASE dossie_escola TO dossie_user;

-- Conectar ao banco
\c dossie_escola

-- Conceder permissões no schema
GRANT ALL ON SCHEMA public TO dossie_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dossie_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dossie_user;

-- Configurar permissões padrão
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dossie_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dossie_user;

-- Verificar
\du
\l
```

### **2. OU: Fazer REBUILD Completo**

1. No EasyPanel, ir em "Services"
2. Parar PostgreSQL
3. Deletar volume `postgres_data` (ATENÇÃO: Vai perder dados!)
4. Fazer Rebuild da aplicação
5. PostgreSQL vai recriar tudo do zero

### **3. Environment Variables Corretas**

Verificar se estão configuradas no EasyPanel:

```
POSTGRES_PASSWORD=Fep09151*
DATABASE_URL=postgresql://dossie_user:Fep09151*@postgres:5432/dossie_escola
```

## 🔍 VERIFICAÇÃO:

Após a correção, testar conexão:

```bash
# Dentro do container da aplicação
psql -h postgres -U dossie_user -d dossie_escola -c "SELECT version();"
```

## 📝 CAUSA:

O PostgreSQL iniciou com variáveis incorretas ou não resolveu as environment variables `${POSTGRES_PASSWORD}` corretamente.

## ⚡ URGENTE:

Execute a **Solução 1** primeiro, é mais rápida e não perde dados! 