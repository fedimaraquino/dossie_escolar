# 🚀 DEPLOY VIA GIT - INSTRUÇÕES FINAIS

## ✅ **ARQUIVOS CONFIGURADOS PARA GIT**

### **🔧 Configurações Atualizadas:**
1. **`env-servidor-local`** - SECRET_KEY gerada: `JKefBRECh7xT5CKxRYhGFT8PrsG0p-ABi_kFOT6raks`
2. **`docker-compose.app.yml`** - Build path corrigido para contexto local
3. **`deploy.sh`** - Verificação de SECRET_KEY adicionada
4. **`.gitignore`** - Atualizado para deploy via Git

### **🚀 Novos Scripts Criados:**
5. **`git-deploy.sh`** - Deploy completo via Git (clone + deploy)
6. **`git-update.sh`** - Atualização via Git (pull + redeploy)
7. **`README_GIT_DEPLOY.md`** - Documentação específica para Git

---

## 📦 **REPOSITÓRIO GITHUB**

### **Informações:**
- **👤 Usuário**: `fedimaraquino`
- **📦 Repositório**: `dossie_escolar`
- **🔗 URL**: `https://github.com/fedimaraquino/dossie_escolar.git`
- **🌿 Branch**: `main`
- **📁 Diretório**: `/var/www/dossie_escolar`

---

## 🎯 **DEPLOY EM 1 COMANDO**

### **Método Automático (Recomendado):**
```bash
# No servidor 10.0.1.185
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

### **Método Manual:**
```bash
# No servidor
git clone https://github.com/fedimaraquino/dossie_escolar.git /var/www/dossie_escolar
cd /var/www/dossie_escolar
chmod +x *.sh
./git-deploy.sh
```

---

## 🔄 **WORKFLOW COMPLETO**

### **1. Preparar Repositório (Primeira vez):**
```bash
# No seu computador local
cd /caminho/para/dossie_novo

# Inicializar Git (se não estiver)
git init
git remote add origin https://github.com/fedimaraquino/dossie_escolar.git

# Adicionar todos os arquivos
git add .
git commit -m "Deploy inicial via Git - Sistema de Dossiê Escolar"

# Enviar para GitHub
git push -u origin main
```

### **2. Deploy no Servidor:**
```bash
# Conectar no servidor
ssh usuario@10.0.1.185

# Instalar pré-requisitos (se necessário)
sudo apt update && sudo apt install -y git curl
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Reiniciar sessão para aplicar grupo docker
exit && ssh usuario@10.0.1.185

# Inicializar Docker Swarm
docker swarm init --advertise-addr 10.0.1.185

# Deploy via Git
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

### **3. Atualizações Futuras:**
```bash
# Fazer mudanças no código local
git add .
git commit -m "Descrição das mudanças"
git push origin main

# Atualizar no servidor
ssh usuario@10.0.1.185
cd /var/www/dossie_escolar
./git-update.sh
```

---

## 🌐 **ACESSOS APÓS DEPLOY**

### **URLs:**
- **📱 Sistema**: `http://10.0.1.185`
- **📱 Direto**: `http://10.0.1.185:5000`
- **📊 Portainer**: `http://10.0.1.185:9000`
- **🔀 Traefik**: `http://10.0.1.185:8080`

### **Login:**
- **Email**: `admin@local.escola`
- **Senha**: `Admin@Local123`

---

## 🔧 **COMANDOS ÚTEIS**

### **Status:**
```bash
cd /var/www/dossie_escolar
./monitor.sh                    # Status completo
docker service ls               # Lista serviços
docker stack ls                 # Lista stacks
```

### **Logs:**
```bash
docker service logs dossie_dossie-app --tail 50
docker service logs postgres_postgres --tail 20
```

### **Backup:**
```bash
cd /var/www/dossie_escolar
./backup.sh
```

### **Restart:**
```bash
docker service update --force dossie_dossie-app
```

---

## 🔑 **SECRET_KEY GERADA**

A SECRET_KEY foi gerada automaticamente:
```
JKefBRECh7xT5CKxRYhGFT8PrsG0p-ABi_kFOT6raks
```

**⚠️ IMPORTANTE**: Esta chave é única e segura. Não compartilhe publicamente.

---

## 📋 **CHECKLIST DE VERIFICAÇÃO**

### **Antes do Deploy:**
- [ ] Repositório criado no GitHub: `fedimaraquino/dossie_escolar`
- [ ] Código enviado para o repositório
- [ ] Servidor com Docker e Git instalados
- [ ] Docker Swarm inicializado

### **Após Deploy:**
- [ ] Sistema acessível em `http://10.0.1.185`
- [ ] Login funcionando
- [ ] Portainer acessível em `:9000`
- [ ] Traefik acessível em `:8080`
- [ ] Todos os serviços rodando: `docker service ls`

---

## 🆘 **TROUBLESHOOTING**

### **Problema: Git clone falha**
```bash
# Verificar conectividade
ping github.com

# Verificar Git
git --version || sudo apt install git
```

### **Problema: Docker não funciona**
```bash
# Verificar e iniciar Docker
sudo systemctl status docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout e login novamente
```

### **Problema: Swarm não ativo**
```bash
docker swarm init --advertise-addr 10.0.1.185
```

### **Problema: Aplicação não responde**
```bash
cd /var/www/dossie_escolar
./monitor.sh
docker service logs dossie_dossie-app --tail 100
docker service update --force dossie_dossie-app
```

---

## 🎯 **VANTAGENS DO DEPLOY VIA GIT**

✅ **Versionamento**: Controle total de versões
✅ **Atualizações**: Simples com `git pull`
✅ **Rollback**: Fácil voltar versões anteriores
✅ **Colaboração**: Múltiplos desenvolvedores
✅ **Backup**: Código sempre no GitHub
✅ **Automação**: Deploy e atualização automatizados
✅ **Rastreabilidade**: Histórico completo de mudanças
✅ **Segurança**: SECRET_KEY gerada automaticamente

---

## 📚 **DOCUMENTAÇÃO**

### **Arquivos de Referência:**
- **`README_GIT_DEPLOY.md`** - Documentação específica para Git
- **`docs/PASSO_A_PASSO.md`** - Guia detalhado
- **`docs/README_DEPLOY.md`** - Comandos úteis
- **`INSTRUCOES_DIRETORIO_CORRETO.md`** - Instruções específicas

---

## 🎉 **CONCLUSÃO**

**Sistema configurado para deploy via Git!**

### **Próximos Passos:**
1. **📤 Enviar código** para GitHub
2. **🚀 Executar deploy** no servidor
3. **🌐 Acessar sistema** em `http://10.0.1.185`
4. **🔄 Usar git-update.sh** para atualizações

### **Comando Final:**
```bash
# No servidor 10.0.1.185
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

**Deploy via Git configurado e pronto para uso! 🚀✨**
