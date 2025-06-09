# 🔄 GUIA COMPLETO - MIGRAÇÕES E ADMIN FLASK

## 🎯 **SISTEMA DE MIGRAÇÕES (Similar ao Django)**

### **📋 COMANDOS DISPONÍVEIS:**

#### **1. Inicializar Sistema de Migrações:**
```bash
python manage.py init-db
```
- Cria pasta `migrations/`
- Configura Alembic
- Cria migração inicial
- Aplica ao banco

#### **2. Criar Nova Migração (quando alterar models):**
```bash
python manage.py makemigrations
```
- Detecta mudanças nos models
- Cria arquivo de migração
- Similar ao `python manage.py makemigrations` do Django

#### **3. Aplicar Migrações:**
```bash
python manage.py migrate-db
```
- Aplica migrações pendentes
- Similar ao `python manage.py migrate` do Django

#### **4. Reverter Migração:**
```bash
python manage.py rollback
```
- Reverte última migração aplicada

#### **5. Ver Status das Migrações:**
```bash
python manage.py show-migrations
```
- Mostra histórico de migrações

---

## 🛠️ **EXEMPLO PRÁTICO - ADICIONANDO CAMPO:**

### **Cenário:** Adicionar campo `telefone_alternativo` ao modelo Usuario

#### **1. Alterar o Model:**
```python
# models/usuario.py
class Usuario(db.Model):
    # ... campos existentes ...
    telefone = db.Column(db.String(20))
    telefone_alternativo = db.Column(db.String(20))  # NOVO CAMPO
```

#### **2. Criar Migração:**
```bash
python manage.py makemigrations
# Descrição: Adicionar telefone alternativo ao usuario
```

#### **3. Aplicar Migração:**
```bash
python manage.py migrate-db
```

#### **4. Verificar no Banco:**
- Campo `telefone_alternativo` será criado automaticamente
- Dados existentes preservados

---

## 🔧 **OUTROS COMANDOS ÚTEIS:**

### **Gerenciamento de Usuários:**
```bash
# Criar usuário administrador
python manage.py create-superuser

# Shell interativo
python manage.py shell
```

### **Banco de Dados:**
```bash
# Resetar banco (CUIDADO!)
python manage.py reset-db

# Fazer backup
python manage.py backup-db
```

### **Desenvolvimento:**
```bash
# Iniciar servidor
python manage.py runserver

# Executar testes
python manage.py test

# Ver todos os comandos
python manage.py help-commands
```

---

## 🎛️ **ÁREA DE ADMINISTRAÇÃO FLASK**

### **📍 ACESSO:**
```
URL: http://localhost:5000/admin
Requisito: Usuário com perfil "Administrador Geral"
```

### **🔑 FUNCIONALIDADES:**

#### **1. Dashboard Administrativo:**
- Estatísticas gerais do sistema
- Usuários e dossiês recentes
- Ações rápidas

#### **2. Gerenciamento de Modelos:**
- Listar todos os registros
- Visualizar detalhes
- Busca e paginação
- Similar ao Django Admin

#### **3. Informações do Sistema:**
- Versão Python e plataforma
- Uso de memória e disco
- Configurações do banco

#### **4. Backup e Logs:**
- Criar backups do banco
- Visualizar logs do sistema
- Download de arquivos

### **📊 MODELOS DISPONÍVEIS:**
- **Usuários** - Gerenciar usuários do sistema
- **Escolas** - Administrar escolas
- **Dossiês** - Visualizar dossiês
- **Anexos** - Gerenciar anexos
- **Perfis** - Configurar perfis de acesso
- **Cidades** - Administrar cidades

---

## 🚀 **FLUXO DE TRABALHO COMPLETO:**

### **1. Desenvolvimento:**
```bash
# 1. Alterar models
# 2. Criar migração
python manage.py makemigrations

# 3. Aplicar migração
python manage.py migrate-db

# 4. Testar no admin
# http://localhost:5000/admin
```

### **2. Produção:**
```bash
# 1. Fazer backup
python manage.py backup-db

# 2. Aplicar migrações
python manage.py migrate-db

# 3. Verificar no admin
```

---

## 🔍 **COMPARAÇÃO COM DJANGO:**

| Django | Flask (Este Sistema) |
|--------|---------------------|
| `python manage.py makemigrations` | `python manage.py makemigrations` |
| `python manage.py migrate` | `python manage.py migrate-db` |
| `python manage.py createsuperuser` | `python manage.py create-superuser` |
| `python manage.py shell` | `python manage.py shell` |
| `python manage.py runserver` | `python manage.py runserver` |
| `/admin/` | `/admin/` |

---

## ⚠️ **BOAS PRÁTICAS:**

### **Migrações:**
1. **Sempre fazer backup** antes de aplicar migrações
2. **Testar em desenvolvimento** antes da produção
3. **Revisar arquivos de migração** antes de aplicar
4. **Não editar migrações** já aplicadas

### **Admin:**
1. **Acesso restrito** apenas para administradores
2. **Fazer backup** antes de alterações importantes
3. **Monitorar logs** regularmente
4. **Verificar espaço em disco** periodicamente

---

## 🎯 **EXEMPLOS DE USO:**

### **Adicionar Campo Email Secundário:**
```python
# 1. Editar models/usuario.py
email_secundario = db.Column(db.String(120))

# 2. Terminal
python manage.py makemigrations
python manage.py migrate-db
```

### **Criar Novo Model:**
```python
# 1. Criar models/categoria.py
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

# 2. Terminal
python manage.py makemigrations
python manage.py migrate-db
```

### **Acessar Admin:**
```
1. Login como admin
2. Ir para http://localhost:5000/admin
3. Gerenciar dados pelo interface web
```

---

## 🎉 **RESULTADO:**

✅ **Sistema de migrações** igual ao Django
✅ **Área de admin** funcional e intuitiva
✅ **Comandos familiares** para desenvolvedores Django
✅ **Backup automático** e logs
✅ **Interface web** para gerenciamento

**Agora você tem um Flask com a mesma facilidade do Django!** 🚀
