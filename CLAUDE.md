
# CLAUDE.md

## Prompt de Desenvolvimento Completo — Sistema de Controle de Dossiê Escolar

### 📌 Contexto do Projeto

Você deve criar um **Sistema de Controle de Dossiê Escolar** para uso por uma rede de 15 escolas municipais. O sistema é um **SaaS multi-tenant**, ou seja, cada escola terá seu próprio acesso e não poderá visualizar os dados das demais. O sistema deve:

- Ser baseado em **Web** (Flask com Python).
- Ter um **banco de dados relacional**.
- Seguir **boas práticas de desenvolvimento seguro**.
- Atender à **LGPD**.
- Disponibilizar uma futura API REST para integração com apps mobile.

### ⚠️ Importante

**Todo o sistema deverá ser criado automaticamente sem a necessidade de minha intervenção manual em nenhuma etapa.**

- A IA deverá gerar **todo o código-fonte**, **estrutura de diretórios**, **configuração do ambiente**, **scripts de deploy** e **documentação** de forma automatizada.
- A IA deverá gerar o **aplicativo completo**, com todas as funcionalidades descritas neste documento, sem que o desenvolvedor precise intervir manualmente no código ou no fluxo de construção.
- O sistema gerado deve estar **pronto para ser testado e implantado** diretamente após a geração.

### 🗂️ Requisitos Gerais

- Desenvolvimento completo do sistema até que esteja operacional.
- Criação de CRUD completo de todas as entidades.
- Tela de login com autenticação segura.
- Criação de um painel administrativo por perfil.
- Criação de um sistema de permissões granular.
- Logs e auditorias de alterações e acessos.
- Responsividade e acessibilidade.
- Documentação detalhada.

### ⚙️ Tecnologias Obrigatórias

- Backend: **Python + Flask + Flask REST Framework**
- Banco de dados: **PostgreSQL**
- Frontend: **Bootstrap + HTML + CSS + JS**
- Autenticação: **Django Authentication + OAuth opcional**
- Armazenamento de arquivos: sistema local inicialmente, com opção futura para **cloud storage**.
- Logs: **Django Logging + tabela de auditoria**

### 🔒 Políticas de Acesso

- Usuário só acessa os dados da sua escola.
- Perfil **Administrador Geral** acessa todas as escolas.
- Perfis previstos:
  - **Administrador Geral** — controla todo o sistema
  - **Administrador da Escola (Diretor)** — gerencia usuários e dossiês da escola
  - **Usuário Operacional da Escola** — apenas uso operacional (cadastro e busca)
- Políticas configuráveis por escola:
  - Restrições de download
  - Períodos de retenção de dados
  - Acesso por IP restrito (configuração opcional)

### ⚙️ Funcionalidades Obrigatórias

#### 1️⃣ Autenticação e Segurança

- Tela de **login** com controle de tentativas
- Recuperação de senha por email
- Cadastro e gerenciamento de usuários
- Auditoria completa de logins e operações sensíveis
- Controle granular de permissões

#### 2️⃣ Gestão de Escolas

- Cadastro de escolas (somente pelo Administrador Geral)
- Campos:
  - Nome, endereço, cidade, UF, CNPJ, INEP, email, diretor, situação, data cadastro, data saída

#### 3️⃣ Gestão de Usuários

- Cadastro de usuários vinculados a uma escola
- Perfis atribuíveis
- Campos:
  - Nome, CPF, email, telefone, data nascimento, data registro, perfil, escola vinculada, último acesso, status

#### 4️⃣ Gestão de Dossiês

- Cadastro de dossiês
- Upload de documentos anexos
- Controle de movimentações
- Campos:
  - Local, pasta, número do dossiê, ano, nome, CPF, nome do pai, nome da mãe, status, tipo de documento, data cadastro, data arquivamento, escola vinculada, observações, foto

#### 5️⃣ Gestão de Movimentações

- Controle de movimentações de dossiês
- Campos:
  - Escola, solicitante, descrição, data solicitação, data devolução, status, dossiê relacionado, responsável movimentação, tipo documentação, observação

#### 6️⃣ Gestão de Solicitantes

- Cadastro de solicitantes
- Campos:
  - Nome, endereço, celular, cidade, CPF, email, parentesco, data nascimento, tipo solicitação, status, data cadastro

#### 7️⃣ Logs e Auditorias

- Auditoria de todas as ações relevantes (CRUD, login, alteração de permissões)
- Campos:
  - Usuário, ação, data/hora, item alterado, IP, navegador utilizado

#### 8️⃣ Outras Entidades Auxiliares

- Cidades
  - Nome, UF, país
- Perfil
  - Nome do perfil
- Logs
  - Mensagem de erro, usuário responsável, nível de erro
- Permissões customizadas
  - Recurso, permissão, usuário relacionado

### 🎛️ Políticas de Configurações

Cada escola deve poder configurar:

- Quem tem acesso a quais recursos.
- Políticas de retenção de documentos.
- Habilitar/desabilitar exportação de dados.
- Regras de segurança locais (como restrição de IP).

### 🔄 Fluxo de Desenvolvimento

1. **Coleta de Requisitos** — 5 dias
2. **Modelagem UML** — 7 dias
3. **Configuração do Ambiente** — 3 dias
4. **Desenvolvimento Backend** — 15 dias
5. **Desenvolvimento Frontend** — 10 dias
6. **Teste e Validação** — 7 dias
7. **Capacitação e Implantação** — 5 dias

### 📜 Regras de Negócio

- Cada escola visualiza **apenas seus próprios dossiês e movimentações**.
- O Administrador Geral pode acessar e auditar **todas as escolas**.
- Toda operação relevante é **logada**.
- O sistema deve estar em conformidade com a **LGPD**:
  - Consentimento explícito para dados pessoais
  - Direito ao esquecimento
  - Auditoria e transparência
  - Segurança e criptografia de dados sensíveis

### 📊 Relatórios

- Relatório de movimentações por solicitante
- Relatório de documentos não devolvidos
- Relatório de histórico de acessos
- Relatório geral de dossiês por escola, por ano, por situação

### 📦 Extras

- Documentação da API REST.
- Código deve seguir **PEP8** e as boas práticas do Django.
- Deve haver **testes automatizados** no backend.
- Documentação técnica em Markdown.
