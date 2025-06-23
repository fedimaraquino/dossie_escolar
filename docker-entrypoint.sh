#!/bin/sh

# Fail on any error
set -e

# Função para verificar se o Postgres está pronto
wait_for_postgres() {
    echo "Aguardando o PostgreSQL iniciar..."
    
    # O nome 'dossie_db' vem do nome do serviço no docker-compose
    # O pg_isready é uma ferramenta do cliente postgres
    until pg_isready -h dossie_db -p 5432 -U "dossie_user"; do
        echo "PostgreSQL indisponível - aguardando 2 segundos..."
        sleep 2
    done
    
    echo "PostgreSQL iniciado com sucesso!"
}

# 1. Aguardar o banco de dados ficar pronto
wait_for_postgres

# 2. Executar o script de criação das tabelas
# Isso garante que o esquema do banco de dados está criado ou atualizado.
echo "Executando a inicialização do banco de dados (criação de tabelas)..."
python setup_database.py

# 3. Executar as migrações do banco de dados (se houver)
# echo "Aplicando migrações do banco de dados..."
# flask db upgrade

# 4. Iniciar o servidor de aplicação Gunicorn
echo "Iniciando o servidor Gunicorn..."
exec "$@" 