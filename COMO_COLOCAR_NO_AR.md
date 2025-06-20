# 🚀 COMO COLOCAR SUA APLICAÇÃO NO AR

## ARQUIVOS NECESSÁRIOS (já criados)
- ✅ `docker-compose.easypanel.yml` 
- ✅ `env-easypanel-production`
- ✅ `deploy-easypanel.sh`

---

## PASSO 1: ANTES DE COMEÇAR

### Configure sua senha do PostgreSQL:
1. Abra o arquivo `env-easypanel-production`
2. Mude esta linha:
   ```
   POSTGRES_PASSWORD=sua_senha_postgres_super_forte_aqui
   ```
   Para:
   ```
   POSTGRES_PASSWORD=MinhaSenh@123Forte
   ```

### Configure o DNS:
No painel do seu domínio, adicione:
- **Tipo**: A
- **Nome**: dossie
- **Valor**: IP da sua VPS Hostinger
- **TTL**: 300

---

## PASSO 2: ACESSE O EASYPANEL

Vá para: `https://SEU_IP_VPS:3000`

---

## PASSO 3: CRIAR O BANCO DE DADOS

1. **Create Project** → Nome: `dossie-escolar`
2. **Create Service** → **Database** → **PostgreSQL**
3. **Configurar:**
   - Service Name: `postgres`
   - POSTGRES_DB: `dossie_escola`
   - POSTGRES_USER: `dossie_user`
   - POSTGRES_PASSWORD: `MinhaSenh@123Forte` (a que você configurou)
   - Volume: `/var/lib/postgresql/data` (5GB)
   - Port: `5432`
4. **Create Service**
5. **AGUARDE** ficar verde "Running"

---

## PASSO 4: CRIAR A APLICAÇÃO

1. **Create Service** → **App**
2. **Configurar:**
   - Service Name: `dossie-app`
   - Repository: `https://github.com/SEU_USUARIO/SEU_REPO.git`
   - Branch: `main`
   - Port: `5000`

3. **Environment Variables** (copie TUDO):
```
FLASK_ENV=production
DATABASE_URL=postgresql://dossie_user:MinhaSenh@123Forte@postgres:5432/dossie_escola
SECRET_KEY=chave_secreta_32_caracteres_aqui
SERVER_NAME=dossie.easistemas.dev.br
UPLOAD_FOLDER=/app/static/uploads
MAX_CONTENT_LENGTH=16777216
PYTHONUNBUFFERED=1
```

4. **Volumes** (adicionar 2):
   - `/app/static/uploads` (2GB)
   - `/app/logs` (500MB)

5. **Create Service**
6. **AGUARDE** build completar e ficar verde "Running"

---

## PASSO 5: CONFIGURAR DOMÍNIO

1. **Aba Domains** → **Add Domain**
2. **Configurar:**
   - Domain: `dossie.easistemas.dev.br`
   - Target Service: `dossie-app`
   - Target Port: `5000`
   - SSL: Let's Encrypt ✅
   - Force HTTPS: ✅
3. **Save Domain**
4. **AGUARDE** SSL gerar (2-3 minutos)

---

## PASSO 6: TESTAR

Acesse: `https://dossie.easistemas.dev.br`

**Login:**
- Email: `admin@sistema.com`
- Senha: `Admin@123`

---

## SE DER ERRO:

### Erro de Build:
- Service `dossie-app` → Aba "Builds" → Ver erro
- Actions → "Rebuild"

### Erro de Banco:
- Service `postgres` → Actions → "Restart"
- Verificar se a senha está igual no banco e na aplicação

### Domínio não funciona:
- Verificar se DNS está configurado
- Aguardar mais tempo (até 24h para propagação)

---

## RESUMO DOS ARQUIVOS:

✅ **3 arquivos essenciais criados**
✅ **1 guia simples de configuração**
✅ **Sem complicação**

Siga este arquivo e sua aplicação estará no ar! 