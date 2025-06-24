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

# Função para configurar diretórios de uploads
setup_upload_directories() {
    echo "Configurando diretórios de uploads..."
    
    # Criar diretórios se não existirem
    mkdir -p /app/static/uploads/fotos
    mkdir -p /app/static/uploads/dossies
    mkdir -p /app/static/uploads/diretores
    mkdir -p /app/static/uploads/anexos
    mkdir -p /app/logs
    
    # Definir permissões corretas
    chmod -R 755 /app/static/uploads
    chmod -R 755 /app/logs
    
    # Definir proprietário (se possível)
    if command -v chown >/dev/null 2>&1; then
        chown -R www-data:www-data /app/static/uploads 2>/dev/null || true
        chown -R www-data:www-data /app/logs 2>/dev/null || true
    fi
    
    echo "Diretórios de uploads configurados com sucesso!"
}

# 1. Configurar diretórios de uploads
setup_upload_directories

# 2. Aguardar o banco de dados ficar pronto
wait_for_postgres

# 3. Executar o script de criação das tabelas
# Isso garante que o esquema do banco de dados está criado ou atualizado.
echo "Executando a inicialização do banco de dados (criação de tabelas)..."
python setup_database.py

# 4. Iniciar o servidor de aplicação Gunicorn
echo "Iniciando o servidor Gunicorn..."
exec "$@" 