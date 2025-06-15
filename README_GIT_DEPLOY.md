# 🏫 Sistema de Controle de Dossiê Escolar - Deploy via Git

Sistema web completo para gerenciamento de dossiês escolares desenvolvido em Flask com Docker Swarm, Traefik e Portainer.

## 🚀 **Deploy Rápido via Git - Servidor Local**

### **📦 Repositório GitHub:**
- **URL**: `https://github.com/fedimaraquino/dossie_escolar.git`
- **Usuário**: `fedimaraquino`
- **Repositório**: `dossie_escolar`

### **🎯 Pré-requisitos:**
- Servidor com IP `10.0.1.185`
- Git e Docker instalados
- Docker Swarm ativo

---

## ⚡ **DEPLOY EM 1 COMANDO**

### **Método Automático (Recomendado):**
```bash
# Conectar no servidor e executar
ssh usuario@10.0.1.185
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

## 🔄 **ATUALIZAÇÕES**

### **Atualização Automática:**
```bash
cd /var/www/dossie_escolar
./git-update.sh
```

### **Atualização Manual:**
```bash
cd /var/www/dossie_escolar
git pull origin main
./deploy.sh
```

---

## 🌐 **ACESSAR SISTEMA**

### **URLs de Acesso:**
- **📱 Sistema Principal**: `http://10.0.1.185`
- **📱 Acesso Direto**: `http://10.0.1.185:5000`
- **📊 Portainer**: `http://10.0.1.185:9000`
- **🔀 Traefik**: `http://10.0.1.185:8080`

### **Credenciais Padrão:**
- **Email**: `admin@local.escola`
- **Senha**: `Admin@Local123`

---

## 🔧 **COMANDOS ÚTEIS**

### **Status do Sistema:**
```bash
cd /var/www/dossie_escolar
./monitor.sh              # Status completo
docker service ls         # Lista serviços
docker stack ls           # Lista stacks
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

## 🏗️ **ARQUITETURA**

- **🐳 Docker Swarm** - Orquestração de containers
- **🔀 Traefik** - Reverse proxy e load balancer
- **📊 Portainer** - Interface de gerenciamento
- **🐘 PostgreSQL** - Banco de dados
- **🌐 Flask** - Framework web Python
- **📱 Bootstrap 5** - Interface responsiva

---

## 📦 **ESTRUTURA DO REPOSITÓRIO**

```
/var/www/dossie_escolar/
├── 📄 README.md                    # Documentação original
├── 📄 README_GIT_DEPLOY.md         # Este arquivo
├── ⚙️ .env                         # Configurações (gerado)
├── 🚀 git-deploy.sh                # Deploy via Git
├── 🔄 git-update.sh                # Atualização via Git
├── 🚀 deploy.sh                    # Deploy local
├── 💾 backup.sh                    # Backup automático
├── 📊 monitor.sh                   # Monitoramento
├── 🐳 Dockerfile                   # Imagem Docker
├── 📋 docker-compose.*.yml         # Configurações Docker
├── 🌐 app.py                       # Aplicação principal
├── 🔧 manage.py                    # Comandos de gerenciamento
├── 📁 models/                      # Modelos do banco
├── 🎮 controllers/                 # Controllers
├── 🎨 templates/                   # Templates HTML
├── 📊 static/                      # Arquivos estáticos
├── 🔧 utils/                       # Utilitários
├── 📚 docs/                        # Documentação completa
├── 🗄️ migrations/                  # Migrações do banco
├── 📁 traefik/data/                # Dados do Traefik
└── 💾 backups/                     # Backups do sistema
```

---

## ✅ **FUNCIONALIDADES**

### **👥 Gestão de Usuários:**
- Perfis: Admin Geral, Admin Escolar, Funcionário
- Controle de permissões por escola
- Sistema de autenticação seguro

### **📋 Controle de Dossiês:**
- Cadastro completo de dossiês
- Upload de documentos
- Movimentações e histórico
- Busca avançada

### **🏫 Multi-tenant:**
- Suporte a múltiplas escolas
- Isolamento total de dados
- Administração centralizada

### **🔒 Segurança:**
- Rate limiting
- Logs de auditoria
- Validação de dados
- Backup automático

---

## 🔧 **CONFIGURAÇÃO**

### **Variáveis de Ambiente (env-servidor-local):**
```bash
# Servidor Local
DOMAIN=10.0.1.185
SERVER_IP=10.0.1.185

# Repositório Git
GIT_REPO=https://github.com/fedimaraquino/dossie_escolar.git
GIT_BRANCH=main

# Banco de dados
POSTGRES_DB=dossie_escola
POSTGRES_USER=dossie
POSTGRES_PASSWORD=DossieLocal@2024!Seguro

# Flask (gerada automaticamente)
SECRET_KEY=JKefBRECh7xT5CKxRYhGFT8PrsG0p-ABi_kFOT6raks
```

---

## 🆘 **TROUBLESHOOTING**

### **Problemas Comuns:**

#### **1. Git clone falha:**
```bash
# Verificar conectividade
ping github.com

# Verificar Git
git --version

# Instalar Git se necessário
sudo apt install git
```

#### **2. Docker não funciona:**
```bash
# Verificar Docker
docker --version
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Adicionar usuário ao grupo
sudo usermod -aG docker $USER
# Logout e login novamente
```

#### **3. Swarm não ativo:**
```bash
# Inicializar Swarm
docker swarm init --advertise-addr 10.0.1.185

# Verificar status
docker info | grep Swarm
```

#### **4. Aplicação não responde:**
```bash
cd /var/www/dossie_escolar
./monitor.sh

# Verificar logs
docker service logs dossie_dossie-app --tail 100

# Restart
docker service update --force dossie_dossie-app
```

### **Comandos de Emergência:**
```bash
# Parar tudo
docker stack rm dossie traefik portainer postgres

# Limpar sistema
docker system prune -f

# Reiniciar deploy
cd /var/www/dossie_escolar
./git-deploy.sh
```

---

## 📋 **WORKFLOW DE DESENVOLVIMENTO**

### **Para Desenvolvedores:**

#### **1. Fazer mudanças no código:**
```bash
# Editar arquivos localmente
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

#### **2. Atualizar no servidor:**
```bash
# No servidor
cd /var/www/dossie_escolar
./git-update.sh
```

#### **3. Verificar deploy:**
```bash
# Verificar status
./monitor.sh

# Verificar logs
docker service logs dossie_dossie-app --tail 50
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

---

## 📞 **SUPORTE**

### **Para dúvidas ou problemas:**
1. **Consulte** a documentação em `docs/`
2. **Execute** `./monitor.sh` para diagnóstico
3. **Verifique** logs dos serviços
4. **Use** comandos de troubleshooting acima

### **Documentação Completa:**
- **[docs/PASSO_A_PASSO.md](docs/PASSO_A_PASSO.md)** - Guia detalhado
- **[docs/README_DEPLOY.md](docs/README_DEPLOY.md)** - Comandos úteis
- **[INSTRUCOES_DIRETORIO_CORRETO.md](INSTRUCOES_DIRETORIO_CORRETO.md)** - Instruções específicas

---

## 🎉 **CONCLUSÃO**

**Sistema pronto para produção com deploy via Git!**

- ✅ **Deploy automático** em 1 comando
- ✅ **Atualizações simples** via Git
- ✅ **Infraestrutura robusta** com Docker Swarm
- ✅ **Monitoramento completo** incluído
- ✅ **Backup automático** configurado

**Acesse: http://10.0.1.185 e comece a usar! 🚀**
