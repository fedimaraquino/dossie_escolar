-- configurar_banco.sql
-- Execute este script no pgAdmin4 para configurar o banco

-- 1. CRIAR BANCO DE DADOS (se não existir)
-- IMPORTANTE: Execute este comando conectado ao banco 'postgres'
CREATE DATABASE dossie_escola
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Portuguese_Brazil.1252'
    LC_CTYPE = 'Portuguese_Brazil.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- 2. CRIAR USUÁRIO (se não existir)
-- Execute conectado ao banco 'postgres'
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dossie') THEN
        CREATE USER dossie WITH PASSWORD 'fep09151';
    END IF;
END
$$;

-- 3. CONCEDER PERMISSÕES NO BANCO
-- Execute conectado ao banco 'postgres'
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;
GRANT CONNECT ON DATABASE dossie_escola TO dossie;

-- 4. CONECTAR AO BANCO dossie_escola E CONCEDER PERMISSÕES NO SCHEMA
-- IMPORTANTE: A partir daqui, conecte ao banco 'dossie_escola'
\c dossie_escola;

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO dossie;
GRANT CREATE ON SCHEMA public TO dossie;

-- Conceder permissões em tabelas existentes e futuras
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dossie;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dossie;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO dossie;

-- Permissões para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dossie;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dossie;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO dossie;

-- 5. VERIFICAR CONFIGURAÇÃO
SELECT 
    'Banco configurado com sucesso!' as status,
    current_database() as banco_atual,
    current_user as usuario_atual;

-- Verificar se usuário dossie existe
SELECT 
    rolname as usuario,
    rolcanlogin as pode_logar,
    rolcreatedb as pode_criar_db,
    rolsuper as super_usuario
FROM pg_roles 
WHERE rolname = 'dossie';

-- Verificar permissões no banco
SELECT 
    datname as banco,
    datacl as permissoes
FROM pg_database 
WHERE datname = 'dossie_escola';

-- Mensagem final
SELECT 'Configuração concluída! Execute: python test_postgresql.py' as proximo_passo;
