# 🚀 GUIA SIMPLES - Deploy via SSH

## ⚡ **ORDEM CORRETA DE EXECUÇÃO**

### **PASSO 1: Configurar SSH (PRIMEIRO)**

#### **No seu computador local:**
```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@exemplo.com"

# Adicionar ao ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Mostrar chave pública para copiar
cat ~/.ssh/id_ed25519.pub
```

#### **No GitHub:**
1. Vá em: https://github.com/settings/ssh/new
2. Cole a chave pública
3. Salve

#### **Testar:**
```bash
ssh -T git@github.com
```

---

### **PASSO 2: Enviar código para GitHub (SEGUNDO)**
```bash
# No seu computador local
cd /caminho/para/dossie_novo

# Configurar Git (se não estiver)
git init
git remote add origin git@github.com:fedimaraquino/dossie_escolar.git

# Enviar código
git add .
git commit -m "Sistema completo para deploy"
git push -u origin main
```

---

### **PASSO 3: Deploy no servidor (TERCEIRO)**

#### **Configurar SSH no servidor também:**
```bash
# Conectar no servidor
ssh usuario@10.0.1.185

# Configurar SSH automaticamente
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/setup-ssh-github.sh | bash
```

#### **Fazer deploy:**
```bash
# Após SSH configurado
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

---

## 🎯 **RESUMO SUPER SIMPLES**

### **1. SSH Local:**
```bash
ssh-keygen -t ed25519 -C "seu-email@exemplo.com"
cat ~/.ssh/id_ed25519.pub  # Copiar e adicionar no GitHub
```

### **2. Enviar código:**
```bash
git add .
git commit -m "Deploy inicial"
git push origin main
```

### **3. SSH no servidor:**
```bash
ssh usuario@10.0.1.185
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/setup-ssh-github.sh | bash
```

### **4. Deploy:**
```bash
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

---

## 🔧 **SE DER ERRO**

### **Erro SSH:**
```bash
# Verificar se chave existe
ls ~/.ssh/

# Testar GitHub
ssh -T git@github.com

# Se não funcionar, executar setup
./setup-ssh-github.sh
```

### **Erro Git:**
```bash
# Verificar remote
git remote -v

# Corrigir se necessário
git remote set-url origin git@github.com:fedimaraquino/dossie_escolar.git
```

---

## 🌐 **ACESSAR SISTEMA**

Após deploy bem-sucedido:
- **Sistema**: `http://10.0.1.185`
- **Login**: `admin@local.escola` / `Admin@Local123`

---

## 📋 **ARQUIVOS IMPORTANTES**

### **Para executar:**
1. **`setup-ssh-github.sh`** - Configurar SSH
2. **`git-deploy.sh`** - Deploy completo
3. **`git-update.sh`** - Atualizações futuras

### **Para consultar:**
4. **`GUIA_SIMPLES_SSH.md`** - Este arquivo
5. **`README_GIT_DEPLOY.md`** - Documentação completa

---

## ✅ **CHECKLIST**

- [ ] SSH configurado no computador local
- [ ] Chave SSH adicionada no GitHub
- [ ] Código enviado para repositório
- [ ] SSH configurado no servidor
- [ ] Deploy executado
- [ ] Sistema acessível

---

## 🎉 **PRONTO!**

**Execute os passos na ordem e o sistema funcionará perfeitamente! 🚀**
