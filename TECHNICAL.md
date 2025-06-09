# Documentação Técnica - Sistema de Controle de Dossiê Escolar

## Arquitetura do Sistema

### Backend (Flask)
- **Framework**: Flask 3.1.1
- **ORM**: SQLAlchemy 2.0.41
- **Autenticação**: Werkzeug Security
- **Banco de Dados**: SQLite (padrão), compatível com PostgreSQL/MySQL

### Frontend
- **Framework CSS**: Bootstrap 5.1.3
- **Ícones**: Font Awesome 6.0.0
- **JavaScript**: jQuery 3.6.0 + JavaScript vanilla
- **Responsividade**: Mobile-first design

## Estrutura do Banco de Dados

### Tabelas Principais

#### usuarios
- `id` (PK): Identificador único
- `nome`: Nome completo do usuário
- `email`: Email único para login
- `senha`: Hash da senha (Werkzeug)
- `tipo`: Tipo de usuário (admin, professor, secretaria)
- `ativo`: Status do usuário
- `data_cadastro`: Data de criação

#### alunos
- `id` (PK): Identificador único
- `nome`: Nome completo do aluno
- `matricula`: Matrícula única
- `data_nascimento`: Data de nascimento
- `cpf`: CPF do aluno
- `rg`: RG do aluno
- `endereco`: Endereço completo
- `telefone`: Telefone de contato
- `email`: Email do aluno
- `nome_responsavel`: Nome do responsável
- `telefone_responsavel`: Telefone do responsável
- `turma`: Turma atual
- `ano_letivo`: Ano letivo
- `ativo`: Status do aluno
- `data_cadastro`: Data de criação

#### dossies
- `id` (PK): Identificador único
- `aluno_id` (FK): Referência ao aluno
- `titulo`: Título do dossiê
- `descricao`: Descrição detalhada
- `tipo`: Categoria (disciplinar, academico, medico, social)
- `status`: Status atual (aberto, em_andamento, resolvido, arquivado)
- `prioridade`: Nível de prioridade (baixa, media, alta, urgente)
- `data_criacao`: Data de criação
- `data_atualizacao`: Data da última atualização
- `usuario_criacao_id` (FK): Usuário que criou

#### documentos
- `id` (PK): Identificador único
- `dossie_id` (FK): Referência ao dossiê
- `nome`: Nome do documento
- `nome_arquivo`: Nome do arquivo no sistema
- `tipo_arquivo`: Tipo/extensão do arquivo
- `tamanho`: Tamanho em bytes
- `descricao`: Descrição do documento
- `data_upload`: Data do upload
- `usuario_upload_id` (FK): Usuário que fez upload

#### observacoes
- `id` (PK): Identificador único
- `dossie_id` (FK): Referência ao dossiê
- `conteudo`: Conteúdo da observação
- `tipo`: Tipo (geral, importante, privada)
- `data_criacao`: Data de criação
- `usuario_id` (FK): Usuário que criou

#### log_atividades
- `id` (PK): Identificador único
- `usuario_id` (FK): Usuário que executou a ação
- `acao`: Descrição da ação
- `tabela`: Tabela afetada
- `registro_id`: ID do registro afetado
- `detalhes`: Detalhes adicionais
- `ip_address`: Endereço IP
- `data_acao`: Data/hora da ação

## Rotas da Aplicação

### Autenticação
- `GET /` - Página inicial
- `GET /login` - Formulário de login
- `POST /login` - Processar login
- `GET /logout` - Logout

### Dashboard
- `GET /dashboard` - Dashboard principal

### Alunos
- `GET /alunos` - Listar alunos
- `GET /alunos/novo` - Formulário novo aluno
- `POST /alunos/novo` - Criar aluno
- `GET /alunos/<id>` - Ver detalhes do aluno

### Dossiês (a implementar)
- `GET /dossies` - Listar dossiês
- `GET /dossies/novo` - Formulário novo dossiê
- `POST /dossies/novo` - Criar dossiê
- `GET /dossies/<id>` - Ver dossiê
- `PUT /dossies/<id>` - Atualizar dossiê

### Documentos (a implementar)
- `POST /documentos/upload` - Upload de documento
- `GET /documentos/<id>` - Download de documento
- `DELETE /documentos/<id>` - Excluir documento

## Segurança

### Autenticação
- Senhas criptografadas com `werkzeug.security`
- Sessões seguras com chave secreta
- Decorator `@login_required` para rotas protegidas

### Validação
- Validação de formulários no frontend e backend
- Sanitização de dados de entrada
- Verificação de tipos de arquivo para upload

### Controle de Acesso
- Sistema de tipos de usuário
- Logs de atividade para auditoria
- Validação de permissões por rota

## Configuração de Desenvolvimento

### Variáveis de Ambiente
```bash
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///dossie_escolar.db
```

### Dependências
```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Werkzeug==3.1.3
```

## Deploy em Produção

### Configurações Recomendadas
1. **Servidor Web**: Nginx + Gunicorn
2. **Banco de Dados**: PostgreSQL
3. **SSL**: Certificado HTTPS
4. **Backup**: Backup automático do banco

### Exemplo de Deploy
```bash
# Instalar dependências
pip install gunicorn

# Executar com Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Monitoramento

### Logs
- Logs de aplicação em `app.log`
- Logs de acesso do servidor web
- Logs de erro para debugging

### Métricas
- Número de usuários ativos
- Quantidade de dossiês por período
- Performance de queries do banco

## Backup e Recuperação

### Backup do Banco SQLite
```bash
# Backup
sqlite3 dossie_escolar.db ".backup backup.db"

# Restauração
sqlite3 dossie_escolar.db ".restore backup.db"
```

### Backup de Arquivos
- Pasta `static/uploads/` contém todos os documentos
- Backup regular recomendado

## Extensões Futuras

### Funcionalidades Planejadas
1. **Relatórios Avançados**: Gráficos e estatísticas
2. **Notificações**: Email e SMS
3. **API REST**: Para integração com outros sistemas
4. **Mobile App**: Aplicativo móvel
5. **Workflow**: Sistema de aprovação de dossiês

### Integrações Possíveis
- Sistema acadêmico da escola
- Sistema de biblioteca
- Plataforma de comunicação com pais
- Sistema de presença

## Troubleshooting

### Problemas Comuns
1. **Erro de importação**: Verificar se todas as dependências estão instaladas
2. **Banco não criado**: Executar `db.create_all()` no contexto da aplicação
3. **Porta ocupada**: Alterar porta no `app.run()`
4. **Permissões de arquivo**: Verificar permissões da pasta `uploads/`

### Debug
- Ativar modo debug: `app.run(debug=True)`
- Verificar logs no terminal
- Usar ferramentas de desenvolvimento do navegador
