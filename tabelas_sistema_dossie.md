# 📊 Estrutura de Tabelas do Projeto - Sistema de Gestão de Dossiês Escolares

Abaixo estão listadas todas as tabelas definidas no projeto até o momento, com seus respectivos campos.

---

## 🏫 Tabela: **escolas**

| Campo           | Descrição                         |
|----------------|-----------------------------------|
| id_escola      | PK - Identificador único da escola |
| nome           | Nome da escola                    |
| endereco       | Endereço da escola                |
| id_cidade      | FK - Cidade associada             |
| situacao       | Situação da escola (ativa/inativa) |
| inep           | Código INEP                       |
| email          | Email institucional               |
| uf             | Unidade federativa (estado)       |
| cnpj           | CNPJ da escola                    |
| diretor_id     | FK - Diretor responsável          |
| data_cadastro  | Data de inclusão no sistema       |
| data_saida     | Data de desativação               |

---

## 👤 Tabela: **usuarios**

| Campo            | Descrição                       |
|------------------|---------------------------------|
| id_usuario       | PK - Identificador do usuário   |
| nome             | Nome completo                   |
| cpf              | CPF                             |
| email            | Email                           |
| tefenone         | Telefone *(possível erro de digitação)* |
| escola_id        | FK - Escola vinculada           |
| perfil_id        | FK - Perfil de permissão        |
| situacao         | Status (ativo/inativo)          |
| ultimo_acesso    | Data/hora do último login       |
| data_nascimento  | Data de nascimento              |
| data_registro    | Data de cadastro                |

---

## 📁 Tabela: **dossies**

| Campo            | Descrição                       |
|------------------|---------------------------------|
| id_dossie        | PK - Identificador              |
| local            | Local físico armazenado         |
| pasta            | Número da pasta física          |
| n_dossie         | Número do dossiê                |
| ano              | Ano do dossiê                   |
| nome             | Nome do aluno                   |
| dt_cadastro      | Data de cadastro                |
| cpf              | CPF do aluno                    |
| n_pai            | Nome do pai                     |
| n_mae            | Nome da mãe                     |
| id_escola        | FK - Escola vinculada           |
| status           | Status do dossiê                |
| foto             | Caminho da foto digital         |
| observacao       | Campo de observações            |
| dt_arquivo       | Data de arquivamento            |
| tipo_documento   | Tipo de documento contido       |

---

## 🔁 Tabela: **movimentacoes**

| Campo                   | Descrição                  |
|-------------------------|----------------------------|
| id_movimentacao         | PK - Identificador         |
| id_escola               | FK - Escola envolvida      |
| id_solicitante          | FK - Solicitante envolvido |
| descricao               | Descrição da movimentação  |
| dt_solicitacao          | Data da solicitação        |
| dt_devolucao            | Data da devolução          |
| observacao              | Observações gerais         |
| status                  | Status atual               |
| id_dossie               | FK - Dossiê movimentado    |
| responsavel_movimentacao | Responsável pela operação |
| tipo_documentacao       | Tipo de documentação       |

---

## 📨 Tabela: **solicitantes**

| Campo            | Descrição                       |
|------------------|---------------------------------|
| id_solicitante   | PK - Identificador              |
| nome             | Nome completo                   |
| endereco         | Endereço                        |
| celular          | Celular                         |
| cidade           | Cidade                          |
| data_cadastro    | Data de inclusão                |
| cpf              | CPF                             |
| email            | Email                           |
| status           | Ativo/Inativo                   |
| parentesco       | Grau de parentesco              |
| data_nascimento  | Data de nascimento              |
| tipo_solicitacao | Tipo de solicitação             |

---

## 🕵️ Tabela: **auditorias**

| Campo         | Descrição                          |
|---------------|------------------------------------|
| id_auditoria  | PK - Identificador do log          |
| idusuario     | FK - Usuário que realizou a ação   |
| acao          | Ação realizada                     |
| dt_acesso     | Data e hora do acesso              |
| item_alterado | Recurso afetado                    |
| ip_acesso     | IP do dispositivo                  |
| navegador     | Navegador utilizado                |

---

## 🌍 Tabela: **cidades**

| Campo      | Descrição          |
|------------|--------------------|
| id_cidade  | PK - Identificador |
| nome       | Nome da cidade     |
| uf         | Unidade Federativa |
| pais       | País               |

---

## 🛡️ Tabela: **perfil**

| Campo      | Descrição             |
|------------|-----------------------|
| id_perfil  | PK - Identificador    |
| perfil     | Nome do perfil        |

---

## 👨‍🏫 Tabela: **diretores**

| Campo          | Descrição              |
|----------------|------------------------|
| id_diretor     | PK - Identificador     |
| nome           | Nome completo          |
| endereco       | Endereço               |
| celular        | Número de celular      |
| cidade         | Cidade                 |
| data_cadastro  | Data de cadastro       |
| cpf            | CPF                    |
| status         | Ativo/Inativo          |
| admissao       | Data de admissão       |
| tipo_mandato   | Cargo ou mandato       |

---

## 📝 Tabela: **logs**

| Campo             | Descrição                         |
|-------------------|-----------------------------------|
| id_logs           | PK - Identificador do log         |
| mensagem_erro     | Mensagem detalhada do erro        |
| usuario_responsavel | FK - Usuário envolvido          |
| situacao_dossie   | Estado do dossiê envolvido        |

---

## 🔒 Tabela: **permissoes**

| Campo           | Descrição                          |
|-----------------|------------------------------------|
| id_permissoes   | PK - Identificador                 |
| id_usuario      | FK - Usuário autorizado            |
| recurso         | Nome do recurso                    |
| permissao       | Tipo de permissão (ex.: leitura)   |
| mensagem_erro   | Mensagem de erro em negação        |
| data_hora       | Data/hora do registro              |
| usuario_id      | FK - Concedente                    |
| nivel_erro      | Nível de erro (se aplicável)       |