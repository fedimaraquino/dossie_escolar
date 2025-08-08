# 📚 Sistema de Controle de Dossiê Escolar

## 🎯 Finalidade do Sistema

O **Sistema de Controle de Dossiê Escolar** é uma aplicação web robusta desenvolvida para modernizar e otimizar a gestão de dossiês escolares em redes municipais de ensino. O sistema digitaliza processos manuais, garantindo maior eficiência, segurança e conformidade com a legislação educacional brasileira.

### **Objetivo Principal**
Proporcionar uma plataforma centralizada e segura para o gerenciamento completo de dossiês escolares, permitindo o controle de documentos, movimentações e relatórios de forma digital, transparente e auditável.

### **Público-Alvo**
- Secretarias Municipais de Educação
- Escolas da rede pública municipal
- Gestores educacionais
- Funcionários administrativos das escolas

---

## 🌟 O que é o Sistema

### **Visão Geral**
Sistema web multi-tenant que permite o gerenciamento isolado e seguro de dossiês escolares para múltiplas escolas municipais através de uma única plataforma. Cada escola mantém total privacidade de seus dados enquanto compartilha a mesma infraestrutura tecnológica.

### **Características Principais**
- **🏫 Multi-tenant**: Suporte a múltiplas escolas com isolamento total de dados
- **🔐 Segurança Avançada**: Conformidade com LGPD e melhores práticas de segurança
- **📊 Dashboard Inteligente**: Visualização de estatísticas e indicadores em tempo real
- **📁 Gestão Documental**: Upload, categorização e controle de documentos
- **🔄 Controle de Movimentação**: Rastreabilidade completa de dossiês
- **📈 Relatórios**: Geração de relatórios customizados e analíticos

---

## 🎨 Usabilidade e Interface

### **Design Responsivo**
- Interface moderna e intuitiva baseada em Bootstrap 5
- Totalmente responsiva para desktop, tablet e mobile
- Experiência de usuário otimizada com navegação simplificada

### **Facilidade de Uso**
- **Dashboard Centralizado**: Acesso rápido a todas as funcionalidades
- **Busca Inteligente**: Localização rápida de dossiês e documentos
- **Formulários Intuitivos**: Cadastros simplificados com validação em tempo real
- **Feedback Visual**: Notificações claras sobre ações realizadas

### **Acessibilidade**
- Suporte a leitores de tela
- Contraste adequado para usuários com deficiência visual
- Navegação por teclado
- Padrões WCAG 2.1 implementados

---

## 💻 Linguagens e Tecnologias Utilizadas

### **Stack Tecnológico**

| Camada | Tecnologia | Versão | Finalidade |
|--------|------------|--------|------------|
| **Backend** | Python | 3.9+ | Lógica de negócio e API |
| **Framework Web** | Flask | 2.3.x | Aplicação web robusta |
| **ORM** | SQLAlchemy | 2.0.x | Mapeamento objeto-relacional |
| **Frontend** | HTML5/CSS3/JavaScript | - | Interface do usuário |
| **Framework CSS** | Bootstrap | 5.3.x | Design responsivo |
| **Ícones** | Font Awesome | 6.x | Iconografia moderna |
| **Containerização** | Docker | 20.10.x | Deploy e distribuição |
| **Proxy Reverso** | Traefik | 3.3.7 | Roteamento e SSL |

### **Linguagens de Programação**
- **Python**: Linguagem principal do backend
- **JavaScript**: Interatividade no frontend
- **SQL**: Consultas e manipulação de dados
- **HTML/CSS**: Estrutura e estilização da interface
- **Bash/PowerShell**: Scripts de automação e deploy

---

## 🗄️ Banco de Dados

### **Arquitetura de Dados**
- **Produção**: PostgreSQL 13 (banco robusto para ambiente corporativo)
- **Desenvolvimento**: SQLite (banco local para desenvolvimento)
- **Migrations**: Flask-Migrate para versionamento do esquema

### **Principais Entidades**
- **Usuario**: Controle de acesso e autenticação
- **Escola**: Configuração das instituições de ensino
- **Dossie**: Núcleo do sistema - dossiês escolares
- **Solicitante**: Pessoas que solicitam dossiês
- **Movimentacao**: Controle de entrada/saída de dossiês
- **Anexo**: Documentos anexados aos dossiês
- **LogAuditoria**: Registro de todas as ações do sistema

### **Relacionamentos**
```
Escola → Usuario → Dossie → Movimentacao
             ↓         ↓
          Permissao   Anexo
```

---

### **🎯 Gestão de Dossiês**
- **Categorização Inteligente**: Classificação por tipo (Disciplinar, Acadêmico, Médico, Social)
- **Controle de Status**: Gerenciamento de estados (Ativo, Arquivado, Em Análise, Urgente)
- **Movimentação Controlada**: Registro de entrada/saída com auditoria completa
- **Priorização**: Sistema de prioridades para dossiês urgentes

### **📁 Gestão Documental**
- **Upload Seguro**: Validação de tipos de arquivo e tamanho (até 16MB)
- **Metadados Automáticos**: Registro automático de data, usuário e escola
- **Busca Avançada**: Localização por conteúdo e metadados
- **Versionamento**: Controle de versões de documentos

### **👥 Gestão de Usuários**
- **Perfis Hierárquicos**: Administrador Geral, Administrador da Escola, Operacional
- **Permissões Granulares**: Controle detalhado de acesso por módulo
- **Multi-tenant**: Isolamento total de dados entre escolas

### **📊 Dashboard e Relatórios**
- **Estatísticas em Tempo Real**: Indicadores de performance e uso
- **Relatórios Customizados**: Geração de relatórios por período e categoria
- **Gráficos Interativos**: Visualização de dados com charts modernos
- **Exportação**: Relatórios em PDF e Excel

### **🔍 Busca e Filtros**
- **Busca Global**: Localização rápida em todo o sistema
- **Filtros Avançados**: Refinamento por múltiplos critérios
- **Histórico de Buscas**: Acesso rápido a buscas anteriores

---

## 🏗️ Arquitetura do Sistema

### **Padrão Arquitetural**
- **MVC (Model-View-Controller)**: Separação clara de responsabilidades
- **Multi-tenant**: Arquitetura para múltiplos clientes com isolamento de dados
- **RESTful API**: Endpoints organizados seguindo padrões REST
- **Modular**: Código organizado em módulos independentes

### **Estrutura de Módulos**
```
📦 Sistema de Controle de Dossiê Escolar
├── 🎯 Core (Núcleo)
│   ├── app.py - Aplicação principal Flask
│   ├── models/ - Modelos de dados (SQLAlchemy)
│   └── controllers/ - Controladores de negócio
├── 👥 Gestão de Usuários
│   ├── auth/ - Autenticação e autorização
│   ├── usuarios/ - CRUD de usuários
│   ├── perfis/ - Gestão de perfis
│   └── permissoes/ - Sistema de permissões
├── 🏫 Gestão Escolar
│   ├── escolas/ - Configuração de escolas
│   ├── diretores/ - Gestão de diretores
│   └── cidades/ - Cadastro de cidades
├── 📋 Gestão de Dossiês
│   ├── dossies/ - CRUD de dossiês
│   ├── solicitantes/ - Gestão de solicitantes
│   ├── movimentacoes/ - Controle de movimentação
│   └── anexos/ - Upload e gestão de documentos
├── 📊 Relatórios e Analytics
│   ├── relatorios/ - Geração de relatórios
│   └── dashboard/ - Dashboard e estatísticas
└── 🔧 Administração
    ├── admin/ - Painel administrativo
    ├── logs/ - Sistema de auditoria
    └── configuracao/ - Configurações do sistema
```

### **Deploy e Infraestrutura**
- **Containerização**: Docker para portabilidade e escalabilidade
- **Proxy Reverso**: Traefik para roteamento e SSL automático
- **SSL/TLS**: Certificados Let's Encrypt para segurança
- **Backup Automático**: Sistema de backup com Backblaze B2

---

## 🔐 Conformidades e Proteção

### **Conformidade LGPD**
- **Consentimento**: Controle de consentimento para tratamento de dados
- **Minimização**: Coleta apenas dos dados necessários
- **Transparência**: Relatórios de uso e compartilhamento de dados
- **Direito ao Esquecimento**: Funcionalidade de exclusão de dados
- **Auditoria**: Log completo de acesso e modificação de dados pessoais

### **Conformidade Educacional**
- **Lei de Acesso à Informação (LAI)**: Transparência nos processos
- **Estatuto da Criança e do Adolescente (ECA)**: Proteção de dados de menores
- **Normas do MEC**: Seguimento das diretrizes educacionais nacionais
- **ISO 27001**: Práticas de segurança da informação

### **Proteção de Dados**
- **Criptografia em Trânsito**: HTTPS/TLS 1.3 para todas as comunicações
- **Criptografia em Repouso**: Dados sensíveis criptografados no banco
- **Backup Seguro**: Backups criptografados e versionados
- **Retenção de Dados**: Políticas claras de retenção e exclusão

---

## 🛡️ Segurança

### **Autenticação e Autorização**
- **Autenticação Multifator**: Opção de 2FA para usuários administrativos
- **Controle de Tentativas**: Máximo 5 tentativas com bloqueio de 30 minutos
- **Sessões Seguras**: Timeout automático e invalidação segura
- **Senhas Robustas**: Política de senhas fortes obrigatória

### **Proteção Contra Ataques**
- **CSRF Protection**: Tokens anti-falsificação em formulários
- **XSS Prevention**: Sanitização de entrada e escape de saída
- **SQL Injection**: Uso de ORM com queries parametrizadas
- **Rate Limiting**: Limitação de requisições por IP

### **Auditoria e Monitoramento**
- **Log de Auditoria**: Registro de todas as ações críticas
- **Monitoramento de Acesso**: Detecção de acessos suspeitos
- **Alertas de Segurança**: Notificações automáticas de eventos críticos
- **Análise de Comportamento**: Detecção de padrões anômalos

### **Validação e Sanitização**
- **Validação de Entrada**: Todos os dados de entrada são validados
- **Sanitização**: Limpeza de dados potencialmente perigosos
- **Upload Seguro**: Validação rigorosa de arquivos uploadados
- **Controle de Acesso**: Verificação de permissões em todas as operações

---

## 📊 Escopo do Sistema

### **Escopo Funcional**
- **Gestão Completa de Dossiês**: Criação, edição, consulta e arquivamento
- **Controle de Movimentação**: Rastreamento completo de entrada/saída
- **Gestão de Usuários**: Cadastro, permissões e auditoria de acesso
- **Relatórios Gerenciais**: Dashboards e relatórios customizados
- **Administração**: Configurações, logs e monitoramento

### **Escopo Técnico**
- **Multi-tenant**: Suporte a múltiplas escolas em uma única instância
- **API RESTful**: Interface programática para integrações
- **Responsividade**: Funciona em desktop, tablet e mobile
- **Escalabilidade**: Arquitetura preparada para crescimento
- **Backup e Recuperação**: Sistema robusto de backup automático

### **Escopo de Segurança**
- **Conformidade Regulatória**: LGPD, LAI e normas educacionais
- **Segurança de Dados**: Criptografia e controle de acesso
- **Auditoria Completa**: Rastreabilidade de todas as operações
- **Recuperação**: Planos de recuperação de desastres

### **Escopo de Integração**
- **Sistemas Educacionais**: Preparado para integração com sistemas escolares
- **APIs Governamentais**: Estrutura para conexão com órgãos públicos
- **Ferramentas de Relatório**: Exportação para Excel, PDF e outros formatos
- **Backup em Nuvem**: Integração com provedores de storage

---

## 🚀 Status do Projeto

### **✅ Funcionalidades Implementadas**
- [x] Sistema de autenticação robusto
- [x] Dashboard com estatísticas em tempo real
- [x] CRUD completo de dossiês
- [x] Upload e gestão de documentos
- [x] Sistema de permissões granular
- [x] Controle de movimentação
- [x] Relatórios e exportação
- [x] Auditoria completa
- [x] Interface responsiva
- [x] Deploy em produção com Docker
- [x] Backup automático
- [x] SSL e segurança implementados

### **🔄 Melhorias Futuras**
- [ ] Notificações por email/SMS
- [ ] API REST completa para integrações
- [ ] App mobile nativo
- [ ] Machine Learning para categorização automática
- [ ] Integração com sistemas de gestão escolar
- [ ] Dashboard avançado com BI

---

## 📁 Estrutura do Projeto

```
📦 dossie_novo/
├── 🚀 app.py                     # Aplicação principal Flask
├── 🗄️ models/                    # Modelos de dados
├── 🎮 controllers/               # Controladores de negócio
├── 🎨 templates/                 # Templates HTML
├── 📱 static/                    # Arquivos estáticos (CSS, JS, imagens)
├── 🐳 docker-compose.yml         # Orquestração Docker
├── 🐳 Dockerfile                 # Imagem Docker
├── 📋 requirements.txt           # Dependências Python
├── 🔧 scripts/                   # Scripts de automação
├── 💾 backups/                   # Sistema de backup
├── 📊 migrations/                # Migrações de banco de dados
├── 📚 step-by-step/              # Documentação detalhada
└── 📖 README.md                  # Esta documentação
```

---

## 🛠️ Instalação e Configuração

### **Pré-requisitos**
- Docker 20.10+ e Docker Compose
- Python 3.9+ (para desenvolvimento local)
- PostgreSQL 13+ (para produção)

### **Deploy com Docker (Recomendado)**
```bash
# Clonar o repositório
git clone [repository-url]
cd dossie_novo

# Configurar variáveis de ambiente
cp env-example .env
# Editar .env com suas configurações

# Iniciar os serviços
docker-compose up -d

# Acessar o sistema
# http://localhost:5000
```

### **Desenvolvimento Local**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python setup_database.py

# Executar aplicação
python app.py
```

---

## 📄 Licença e Conformidade

Este projeto é desenvolvido como parte de uma atividade acadêmica extensionista, seguindo todas as normas de segurança, privacidade e conformidade regulatória aplicáveis ao setor educacional brasileiro.

**Sistema de Controle de Dossiê Escolar** - Modernizando a gestão educacional com tecnologia, segurança e conformidade.
