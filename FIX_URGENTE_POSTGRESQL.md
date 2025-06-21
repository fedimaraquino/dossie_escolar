# 🚨 FIX URGENTE - PostgreSQL Erro 500

## ❌ PROBLEMA CONFIRMADO:
```
ERROR 500: SQLAlchemy connection failed
CAUSA: Role "dossie_user" does not exist
STATUS: CRÍTICO - Sistema inacessível
```

## ⚡ SOLUÇÃO IMEDIATA - EXECUTAR AGORA:

### **PASSO 1: Acessar Container PostgreSQL**

No EasyPanel:
1. Ir em **Services** → **postgres**
2. Clicar em **"Console"** ou **"Terminal"**
3. Executar comandos abaixo:

### **PASSO 2: Comandos SQL - COPIAR E COLAR:**

```bash
# Conectar como superuser
psql -U postgres

# Criar usuário dossie_user
CREATE USER dossie_user WITH PASSWORD 'Fep09151*';

# Criar database
CREATE DATABASE dossie_escola OWNER dossie_user;

# Conceder permissões básicas
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie_user;
GRANT CONNECT ON DATABASE dossie_escola TO dossie_user;

# Conectar ao banco específico
\c dossie_escola

# Conceder permissões no schema
GRANT ALL ON SCHEMA public TO dossie_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dossie_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dossie_user;

# Configurar permissões padrão para futuras tabelas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dossie_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dossie_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO dossie_user;

# Verificar criação
\du
\l
\q
```

### **PASSO 3: Reiniciar Aplicação**

Após executar os comandos SQL:
1. No EasyPanel → Serviço **dossie-app**
2. Clicar em **"Restart"**
3. Aguardar 30 segundos
4. Testar: https://dossie.easistemas.dev.br

## 🔧 ALTERNATIVA - REBUILD COMPLETO:

Se não conseguir acessar console PostgreSQL:

1. **PARAR** todos os serviços
2. **DELETAR** volume `postgres_data` ⚠️ (perde dados)
3. **REBUILD** projeto completo
4. PostgreSQL vai recriar do zero com script de inicialização

## ✅ VERIFICAÇÃO:

Após correção:
- ✅ Site deve carregar: https://dossie.easistemas.dev.br
- ✅ Login: admin@sistema.com / Admin@123
- ✅ Dashboard deve funcionar sem erro 500

## 📞 URGENTE:

**EXECUTE O PASSO 2 AGORA** - É a solução mais rápida!

Tempo estimado: **2 minutos** 