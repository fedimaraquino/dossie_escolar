# 🐘 GUIA COMPLETO - POSTGRESQL PARA SISTEMA DE DOSSIÊ

## 📊 **SUAS CREDENCIAIS CONFIGURADAS:**
- **Banco:** `dossie_escola`
- **Usuário:** `dossie`
- **Senha:** `fep09151`
- **Host:** `localhost:5432`

## 🚀 **PASSO A PASSO COMPLETO:**

### **1. INSTALAR POSTGRESQL**

#### **Opção A - Download Oficial (Recomendado):**
1. Acesse: https://www.postgresql.org/download/windows/
2. Baixe a versão mais recente
3. Execute o instalador
4. **IMPORTANTE:** Anote a senha do usuário `postgres`
5. Mantenha porta padrão: `5432`

#### **Opção B - Via Winget:**
```cmd
winget install PostgreSQL.PostgreSQL
```

#### **Opção C - Via Chocolatey:**
```cmd
choco install postgresql
```

### **2. INICIAR SERVIÇO POSTGRESQL**

#### **Via Services (Recomendado):**
1. Pressione `Win + R`
2. Digite: `services.msc`
3. Procure por "PostgreSQL" 
4. Clique direito → "Iniciar"
5. Clique direito → "Propriedades" → "Automático"

#### **Via Linha de Comando:**
```cmd
# Como Administrador
net start postgresql-x64-14
```

### **3. CONFIGURAR BANCO E USUÁRIO**

#### **Via pgAdmin (Interface Gráfica):**
1. Abra **pgAdmin** (instalado com PostgreSQL)
2. Conecte ao servidor local
3. Senha: a que você definiu na instalação
4. Clique direito em "Databases" → "Create" → "Database"
5. Nome: `dossie_escola`
6. Encoding: `UTF8`
7. Clique direito em "Login/Group Roles" → "Create" → "Login/Group Role"
8. Nome: `dossie`
9. Aba "Definition" → Senha: `fep09151`
10. Aba "Privileges" → Marque todas as opções
11. Clique direito no banco `dossie_escola` → "Properties" → "Security"
12. Adicione usuário `dossie` com todas as permissões

#### **Via Linha de Comando:**
```cmd
# Conectar como postgres
psql -U postgres

# Executar comandos SQL:
CREATE DATABASE dossie_escola 
    WITH ENCODING 'UTF8' 
    LC_COLLATE = 'Portuguese_Brazil.1252' 
    LC_CTYPE = 'Portuguese_Brazil.1252';

CREATE USER dossie WITH PASSWORD 'fep09151';

GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;

\c dossie_escola;

GRANT ALL ON SCHEMA public TO dossie;

\q
```

### **4. TESTAR CONFIGURAÇÃO**

#### **Teste 1 - Diagnóstico Automático:**
```cmd
python check_database.py
```

#### **Teste 2 - Conexão Manual:**
```cmd
psql -U dossie -d dossie_escola -h localhost
# Senha: fep09151
```

#### **Teste 3 - Criar Tabelas:**
```cmd
python setup_tables.py
```

### **5. INICIAR SISTEMA**
```cmd
python app.py
```

## 🔧 **RESOLUÇÃO DE PROBLEMAS:**

### **Erro: "Serviço não inicia"**
1. Verifique se PostgreSQL foi instalado corretamente
2. Execute como Administrador:
   ```cmd
   sc start postgresql-x64-14
   ```
3. Verifique logs em: `C:\Program Files\PostgreSQL\14\data\log\`

### **Erro: "Banco não existe"**
```sql
-- Conectar como postgres e executar:
CREATE DATABASE dossie_escola;
```

### **Erro: "Usuário sem permissão"**
```sql
-- Conectar como postgres e executar:
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;
\c dossie_escola;
GRANT ALL ON SCHEMA public TO dossie;
```

### **Erro: "Conexão recusada"**
1. Verificar se PostgreSQL está rodando
2. Verificar arquivo `pg_hba.conf`:
   - Localização: `C:\Program Files\PostgreSQL\14\data\pg_hba.conf`
   - Adicionar linha: `host all all 127.0.0.1/32 md5`
3. Reiniciar serviço PostgreSQL

## 📋 **VERIFICAÇÃO FINAL:**

### **Checklist de Configuração:**
- [ ] PostgreSQL instalado
- [ ] Serviço PostgreSQL rodando
- [ ] Banco `dossie_escola` criado
- [ ] Usuário `dossie` criado
- [ ] Permissões concedidas
- [ ] Conexão testada
- [ ] Tabelas criadas
- [ ] Sistema funcionando

### **Comandos de Verificação:**
```cmd
# 1. Verificar serviço
sc query postgresql-x64-14

# 2. Testar conexão
python check_database.py

# 3. Criar tabelas
python setup_tables.py

# 4. Iniciar sistema
python app.py
```

## 🎯 **RESULTADO ESPERADO:**

Após configuração completa:
- ✅ PostgreSQL rodando
- ✅ Banco `dossie_escola` funcionando
- ✅ Usuário `dossie` com acesso
- ✅ Tabelas criadas automaticamente
- ✅ Sistema acessível em http://localhost:5000
- ✅ Login: admin@sistema.com / admin123

## 💡 **ALTERNATIVA TEMPORÁRIA:**

Se PostgreSQL não funcionar imediatamente:
```cmd
# O sistema funciona com SQLite como backup
python app.py
# Acesse: http://localhost:5000
```

Depois configure PostgreSQL e execute:
```cmd
python migrate_to_postgresql.py  # Migrar dados do SQLite
```
