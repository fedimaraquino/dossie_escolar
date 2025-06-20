#!/bin/bash

# Script de Deploy para EasyPanel - Hostinger
# Sistema de Controle de Dossiê Escolar

set -e

echo "🚀 Iniciando deploy no EasyPanel..."

# Verificar se está no diretório correto
if [ ! -f "docker-compose.easypanel.yml" ]; then
    echo "❌ Erro: docker-compose.easypanel.yml não encontrado"
    echo "Execute este script no diretório raiz do projeto"
    exit 1
fi

# Verificar se o arquivo de ambiente existe
if [ ! -f "env-easypanel-production" ]; then
    echo "❌ Erro: env-easypanel-production não encontrado"
    echo "Crie o arquivo com as variáveis de ambiente antes de continuar"
    exit 1
fi

# Gerar SECRET_KEY se não estiver definida
if ! grep -q "SECRET_KEY=" env-easypanel-production || grep -q "sua_chave_secreta_super_forte_aqui_32_chars" env-easypanel-production; then
    echo "🔑 Gerando SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" env-easypanel-production
    echo "✅ SECRET_KEY gerada: $SECRET_KEY"
fi

# Verificar se PostgreSQL password está configurada
if grep -q "sua_senha_postgres_super_forte_aqui" env-easypanel-production; then
    echo "❌ Erro: Configure a senha do PostgreSQL no arquivo env-easypanel-production"
    exit 1
fi

# Fazer backup dos arquivos existentes
echo "📦 Fazendo backup..."
mkdir -p backups
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml backups/docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
fi

# Usar o docker-compose específico para EasyPanel
echo "🔧 Configurando para EasyPanel..."
cp docker-compose.easypanel.yml docker-compose.yml

# Carregar variáveis de ambiente
echo "🔄 Carregando variáveis de ambiente..."
set -a
source env-easypanel-production
set +a

# Fazer build da imagem
echo "🏗️ Fazendo build da aplicação..."
docker-compose build --no-cache

# Verificar se os volumes existem
echo "📁 Verificando volumes..."
docker volume create dossie_novo_app_uploads 2>/dev/null || true
docker volume create dossie_novo_app_logs 2>/dev/null || true
docker volume create dossie_novo_postgres_data 2>/dev/null || true

# Subir os serviços
echo "🚀 Subindo os serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
docker-compose ps

# Verificar logs
echo "📋 Verificando logs da aplicação..."
docker-compose logs --tail=20 dossie-app

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "🌐 Aplicação disponível em:"
echo "   - https://dossie.easistemas.dev.br"
echo ""
echo "📊 Para monitorar:"
echo "   - Logs: docker-compose logs -f dossie-app"
echo "   - Status: docker-compose ps"
echo ""
echo "🔧 Para resolver problemas:"
echo "   - Reiniciar: docker-compose restart dossie-app"
echo "   - Rebuild: docker-compose build --no-cache && docker-compose up -d"
echo "" 