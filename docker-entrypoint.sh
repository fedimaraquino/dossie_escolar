#!/bin/sh

# Fail on any error
set -e

# Função para verificar se o Postgres está pronto
wait_for_postgres() {
    echo "Aguardando o PostgreSQL iniciar..."
    
    # Adicionando comandos de diagnóstico de rede
    echo "--- INÍCIO DO DIAGNÓSTICO DE REDE ---"
    ping -c 4 dossie_db || echo "Ping para dossie_db FALHOU"
    echo "Tentando conexão na porta 5432 com netcat..."
    nc -z -v -w 5 dossie_db 5432
    echo "--- FIM DO DIAGNÓSTICO DE REDE ---"

    # O nome 'dossie_db' vem do nome do serviço no docker-compose/easypanel
    # O pg_isready é uma ferramenta do cliente postgres
    until pg_isready -h dossie_db -p 5432 -U "${POSTGRES_USER:-dossie_user}"; do
        echo "PostgreSQL indisponível - aguardando..."
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