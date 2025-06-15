# 📁 INSTRUÇÕES - Deploy via Git

## 🎯 **REPOSITÓRIO GITHUB**

A aplicação agora está configurada para deploy via Git:
- **📦 Repositório**: `https://github.com/fedimaraquino/dossie_escolar.git`
- **📁 Diretório**: `/var/www/dossie_escolar`
- **🔑 SECRET_KEY**: Gerada automaticamente

---

## 🔧 **ARQUIVOS ATUALIZADOS**

Os seguintes arquivos foram ajustados para o novo diretório:

✅ **`env-servidor-local`** - Adicionada variável APP_DIR
✅ **`docker-compose.app.yml`** - Build path atualizado
✅ **`deploy.sh`** - Caminhos corrigidos
✅ **`backup.sh`** - Diretório de backup atualizado
✅ **`docs/PASSO_A_PASSO.md`** - Instruções atualizadas
✅ **`README.md`** - Comandos corrigidos
✅ **`docs/README_DEPLOY.md`** - Paths atualizados
✅ **`setup-diretorio.sh`** - Novo script de configuração

---

## 🚀 **INSTRUÇÕES DE DEPLOY VIA GIT**

### **MÉTODO 1: Deploy Inicial (Recomendado)**
```bash
# Conectar no servidor
ssh usuario@10.0.1.185

# Instalar Git e Docker (se necessário)
sudo apt update && sudo apt install -y git
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Reiniciar sessão para aplicar grupo docker
exit && ssh usuario@10.0.1.185

# Inicializar Swarm
docker swarm init --advertise-addr 10.0.1.185

# Fazer deploy via Git (um comando!)
curl -fsSL https://raw.githubusercontent.com/fedimaraquino/dossie_escolar/main/git-deploy.sh | bash
```

### **MÉTODO 2: Deploy Manual**
```bash
# No servidor
git clone https://github.com/fedimaraquino/dossie_escolar.git /var/www/dossie_escolar
cd /var/www/dossie_escolar
chmod +x *.sh
./git-deploy.sh
```

### **ATUALIZAÇÕES**
```bash
# Para atualizar o sistema
cd /var/www/dossie_escolar
./git-update.sh

# Ou simplesmente
git pull && ./deploy.sh
```

### **PASSO 4: Acessar Sistema**
- **Sistema**: `http://10.0.1.185`
- **Login**: `admin@local.escola` / `Admin@Local123`

---

## 📋 **VERIFICAÇÕES**

### **Verificar Estrutura:**
```bash
ls -la /var/www/dossie_escolar/
```

### **Verificar Permissões:**
```bash
ls -ld /var/www/dossie_escolar/
stat /var/www/dossie_escolar/
```

### **Verificar Scripts:**
```bash
ls -la /var/www/dossie_escolar/*.sh
```

---

## 🔧 **COMANDOS ÚTEIS**

### **Status do Sistema:**
```bash
cd /var/www/dossie_escolar
./monitor.sh
```

### **Backup:**
```bash
cd /var/www/dossie_escolar
./backup.sh
```

### **Logs:**
```bash
docker service logs dossie_dossie-app --tail 50
```

### **Restart:**
```bash
docker service update --force dossie_dossie-app
```

---

## 🗂️ **ESTRUTURA FINAL**

```
/var/www/dossie_escolar/
├── 📄 README.md
├── ⚙️ .env                         # Configurações
├── 🚀 deploy.sh                    # Deploy automático
├── 💾 backup.sh                    # Backup automático
├── 📊 monitor.sh                   # Monitoramento
├── 🔧 setup-diretorio.sh           # Configuração inicial
├── 🐳 Dockerfile
├── 📋 docker-compose.*.yml
├── 🌐 app.py
├── 🔧 manage.py
├── 📁 models/
├── 🎮 controllers/
├── 🎨 templates/
├── 📊 static/
├── 🔧 utils/
├── 📚 docs/
├── 🗄️ migrations/
├── 📁 traefik/data/
└── 💾 backups/
```

---

## ⚠️ **IMPORTANTE**

### **Permissões:**
- O diretório `/var/www/dossie_escolar` deve ter permissões corretas
- Scripts devem ter permissão de execução (`chmod +x *.sh`)
- Usuário deve ter acesso de escrita ao diretório

### **Docker:**
- Docker deve estar instalado e rodando
- Docker Swarm deve estar ativo
- Usuário deve estar no grupo docker

### **Rede:**
- Porta 80, 443, 5000, 8080, 9000 devem estar abertas
- IP 10.0.1.185 deve estar acessível na rede

---

## 🆘 **TROUBLESHOOTING**

### **Problema: Permissão negada**
```bash
sudo chown -R $USER:$USER /var/www/dossie_escolar
chmod +x /var/www/dossie_escolar/*.sh
```

### **Problema: Diretório não existe**
```bash
sudo mkdir -p /var/www/dossie_escolar
sudo chown -R $USER:$USER /var/www/dossie_escolar
```

### **Problema: Docker não funciona**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout e login novamente
```

### **Problema: Swarm não ativo**
```bash
docker swarm init --advertise-addr 10.0.1.185
```

---

## ✅ **VERIFICAÇÃO FINAL**

Após o deploy, verificar:

- [ ] Sistema acessível em `http://10.0.1.185`
- [ ] Login funcionando
- [ ] Portainer em `http://10.0.1.185:9000`
- [ ] Traefik em `http://10.0.1.185:8080`
- [ ] Todos os serviços rodando: `docker service ls`

---

## 🎉 **CONCLUSÃO**

Todos os arquivos foram atualizados para o diretório correto `/var/www/dossie_escolar`.

**O sistema está pronto para deploy no local correto! 🚀**

---

## 📞 **SUPORTE**

1. **Leia**: `docs/PASSO_A_PASSO.md` para instruções detalhadas
2. **Execute**: `./setup-diretorio.sh` para verificar configuração
3. **Execute**: `./monitor.sh` para diagnóstico
4. **Verifique**: Logs com `docker service logs dossie_dossie-app`

**Diretório correto configurado e pronto para uso! 📁✨**
