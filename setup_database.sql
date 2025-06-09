-- setup_database.sql
-- Script para configurar banco PostgreSQL para Sistema de Dossiê

-- Criar banco de dados
CREATE DATABASE dossie_escola
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Portuguese_Brazil.1252'
    LC_CTYPE = 'Portuguese_Brazil.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Conectar ao banco criado
\c dossie_escola;

-- Criar usuário
CREATE USER dossie WITH PASSWORD 'fep09151';

-- Dar permissões completas
GRANT ALL PRIVILEGES ON DATABASE dossie_escola TO dossie;
GRANT ALL ON SCHEMA public TO dossie;
GRANT ALL ON ALL TABLES IN SCHEMA public TO dossie;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO dossie;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO dossie;

-- Dar permissões futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dossie;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dossie;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO dossie;

-- Verificar configuração
SELECT 'Banco criado com sucesso!' as status;
SELECT current_database() as banco_atual;
SELECT usename as usuario FROM pg_user WHERE usename = 'dossie';
