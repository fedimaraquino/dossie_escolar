# Sistema de Controle de Dossiê Escolar - SaaS Multi-tenant

Sistema web completo para gerenciamento de dossiês escolares em redes municipais, desenvolvido conforme especificação do CLAUDE.md.

## Funcionalidades Principais

### 🏫 **Sistema Multi-tenant**
- **15 Escolas Municipais**: Cada escola acessa apenas seus dados
- **Isolamento Total**: Dados completamente separados por escola
- **Administração Centralizada**: Admin geral controla todas as escolas

### 🔐 **Segurança e Conformidade LGPD**
- **Controle de Tentativas**: Máximo 5 tentativas de login
- **Bloqueio Automático**: 30 minutos após tentativas excessivas
- **Auditoria Completa**: Log de todas as ações e acessos
- **Recuperação de Senha**: Sistema seguro por email
- **Criptografia**: Senhas e dados sensíveis protegidos

### 👥 **Gestão de Usuários e Perfis**
- **Administrador Geral**: Acesso total ao sistema
- **Administrador da Escola**: Gerencia usuários e dossiês da escola
- **Usuário Operacional**: Cadastro e busca operacional

## Tecnologias Utilizadas

- **Backend**: Python 3.x, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (pode ser alterado para PostgreSQL/MySQL)
- **Autenticação**: Werkzeug Security
- **Interface**: Font Awesome, jQuery

## Instalação e Execução

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passo a passo

1. **Clone ou baixe o projeto**
   ```bash
   cd dossie_novo
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
   
   Ou use o script de instalação:
   ```bash
   python run.py install
   ```

3. **Execute a aplicação**
   ```bash
   python app.py
   ```
   
   Ou use o script de execução:
   ```bash
   python run.py
   ```

4. **Acesse o sistema**
   - Abra seu navegador e vá para: `http://localhost:5000`
   - Login padrão:
     - **Email**: admin@escola.com
     - **Senha**: admin123

## Estrutura do Projeto

```
dossie_novo/
├── app.py                 # Aplicação principal Flask
├── models.py              # Modelos do banco de dados
├── requirements.txt       # Dependências Python
├── run.py                # Script de inicialização
├── README.md             # Este arquivo
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página inicial
│   ├── login.html        # Página de login
│   ├── dashboard.html    # Dashboard principal
│   └── alunos/           # Templates de alunos
│       ├── listar.html   # Lista de alunos
│       ├── novo.html     # Cadastro de aluno
│       └── ver.html      # Detalhes do aluno
├── static/               # Arquivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos customizados
│   ├── js/
│   │   └── main.js       # JavaScript principal
│   └── uploads/          # Pasta para uploads
└── dossie_escolar.db     # Banco de dados SQLite (criado automaticamente)
```

## Funcionalidades Implementadas

### ✅ Concluído
- [x] Sistema de autenticação
- [x] Dashboard com estatísticas
- [x] Cadastro de alunos
- [x] Listagem de alunos com busca e paginação
- [x] Visualização de detalhes do aluno
- [x] Interface responsiva
- [x] Modelos de banco de dados completos

### 🚧 Em Desenvolvimento
- [ ] CRUD completo de dossiês
- [ ] Upload e gerenciamento de documentos
- [ ] Sistema de observações
- [ ] Relatórios e exportação
- [ ] Gestão de usuários
- [ ] Log de atividades

## Uso do Sistema

### 1. Login
- Acesse a página inicial e clique em "Fazer Login"
- Use as credenciais padrão ou crie novos usuários

### 2. Dashboard
- Visualize estatísticas gerais do sistema
- Acesse rapidamente alunos e dossiês recentes
- Use as ações rápidas para navegação

### 3. Gestão de Alunos
- **Listar**: Veja todos os alunos com busca e filtros
- **Cadastrar**: Adicione novos alunos com dados completos
- **Visualizar**: Veja detalhes e dossiês de cada aluno

### 4. Controle de Dossiês
- Crie dossiês por categoria (disciplinar, acadêmico, médico, social)
- Defina prioridades e status
- Adicione documentos e observações

## Configuração

### Banco de Dados
O sistema usa SQLite por padrão. Para usar outro banco:

1. Edite `app.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
   ```

2. Instale o driver correspondente:
   ```bash
   pip install psycopg2  # Para PostgreSQL
   pip install pymysql   # Para MySQL
   ```

### Configurações de Upload
- Tamanho máximo: 16MB (configurável em `app.py`)
- Pasta de uploads: `static/uploads/`

## Segurança

- Senhas são criptografadas com Werkzeug
- Sessões seguras com chave secreta aleatória
- Validação de formulários
- Controle de acesso por rotas

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste thoroughly
5. Envie um pull request

## Suporte

Para dúvidas ou problemas:
- Verifique se todas as dependências estão instaladas
- Confirme que o Python 3.7+ está sendo usado
- Verifique se a porta 5000 está disponível

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

---

**Sistema de Controle de Dossiê Escolar** - Desenvolvido para facilitar a gestão educacional.
