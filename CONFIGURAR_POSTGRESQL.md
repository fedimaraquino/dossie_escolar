# 🐘 CONFIGURAÇÃO POSTGRESQL PARA SISTEMA DE DOSSIÊ

## 📋 **SUAS CREDENCIAIS CONFIGURADAS:**
- **Banco:** `dossie_escola`
- **Usuário:** `dossie`
- **Senha:** `fep09151`
- **Host:** `localhost`
- **Porta:** `5432`

## 🔧 **PASSO A PASSO:**

### 1. **Instalar PostgreSQL (se não instalado)**
```bash
# Download oficial:
https://www.postgresql.org/download/windows/

# Ou via Winget:
winget install PostgreSQL.PostgreSQL

# Ou via Chocolatey:
choco install postgresql
```

### 2. **Configurar Banco via pgAdmin (Método Visual)**
1. Abra **pgAdmin**
2. Conecte ao servidor PostgreSQL
3. Clique direito em "Databases" → "Create" → "Database"
4. Nome: `dossie_escola`
5. Clique direito em "Login/Group Roles" → "Create" → "Login/Group Role"
6. Nome: `dossie`
7. Aba "Definition" → Senha: `fep09151`
8. Aba "Privileges" → Marque todas as opções
9. Clique direito no banco `dossie_escola` → "Properties" → "Security"
10. Adicione usuário `dossie` com todas as permissões

### 3. **Configurar Banco via Linha de Comando**
```bash
# Conectar como postgres
psql -U postgres

# Executar script de configuração
\i setup_database.sql

# Ou executar comandos manualmente:
CREATE DATABASE dossie_escola;
CREATE USER dossie WITH PASSWORD 'fep09151';
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;
\c dossie_escola;
GRANT ALL ON SCHEMA public TO dossie;
\q
```

### 4. **Testar Configuração**
```bash
# Testar conexão
python test_postgresql.py

# Se der erro, verificar:
# - PostgreSQL está rodando?
# - Banco foi criado?
# - Usuário foi criado?
# - Permissões foram dadas?
```

### 5. **Migrar Dados do SQLite**
```bash
# Migrar dados existentes
python migrate_to_postgresql.py

# Ou criar banco limpo
python app.py
```

### 6. **Iniciar Sistema**
```bash
# Iniciar aplicação
python app.py

# Acessar sistema
http://localhost:5000
```

## 🔍 **VERIFICAÇÕES:**

### **Testar Conexão Manual:**
```bash
psql -U dossie -d dossie_escola -h localhost
# Senha: fep09151
```

### **Verificar Tabelas:**
```sql
\dt  -- Listar tabelas
\du  -- Listar usuários
\l   -- Listar bancos
```

## ⚠️ **PROBLEMAS COMUNS:**

### **Erro de Conexão:**
- Verificar se PostgreSQL está rodando
- Verificar se porta 5432 está aberta
- Verificar arquivo `pg_hba.conf`

### **Erro de Permissão:**
```sql
-- Dar permissões extras se necessário
GRANT ALL ON ALL TABLES IN SCHEMA public TO dossie;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO dossie;
```

### **Erro de Encoding:**
- Verificar se banco foi criado com UTF8
- Verificar locale do sistema

## 🎯 **RESULTADO ESPERADO:**
Após configuração, o sistema deve:
1. ✅ Conectar ao PostgreSQL automaticamente
2. ✅ Criar tabelas no primeiro acesso
3. ✅ Migrar dados do SQLite (se existirem)
4. ✅ Funcionar normalmente com PostgreSQL

## 📞 **SUPORTE:**
Se houver problemas:
1. Execute: `python test_postgresql.py`
2. Verifique logs de erro
3. Confirme credenciais no arquivo `.env`
