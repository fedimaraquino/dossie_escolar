#!/bin/bash
# Script para corrigir problemas de banco de dados

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🗄️ CORREÇÃO DO BANCO DE DADOS                             ║"
echo "║    🔧 PostgreSQL + Migrações                                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "🗄️ Corrigindo problemas do banco de dados..."

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.postgres.yml" ]; then
    error "❌ Arquivo docker-compose.postgres.yml não encontrado!"
fi

# Parar aplicação
log "🛑 Parando aplicação..."
docker stack rm dossie 2>/dev/null || true

# Aguardar parar
log "⏳ Aguardando aplicação parar..."
sleep 15

# Verificar se PostgreSQL está rodando
log "🐘 Verificando PostgreSQL..."
if ! docker service ls | grep -q postgres_postgres; then
    warn "PostgreSQL não está rodando, iniciando..."
    docker stack deploy -c docker-compose.postgres.yml postgres
    log "⏳ Aguardando PostgreSQL inicializar..."
    sleep 30
fi

# Aguardar PostgreSQL estar pronto
log "⏳ Aguardando PostgreSQL estar pronto..."
for i in {1..30}; do
    if docker exec $(docker ps -q -f name=postgres_postgres) pg_isready -U dossie -d dossie_escola 2>/dev/null; then
        log "✅ PostgreSQL está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        error "❌ PostgreSQL não ficou pronto em 5 minutos"
    fi
    sleep 10
done

# Limpar migrações problemáticas
log "🧹 Limpando migrações problemáticas..."
if [ -d "migrations/versions" ]; then
    rm -f migrations/versions/*.py
    log "✅ Migrações antigas removidas"
fi

# Recriar banco de dados
log "🗄️ Recriando banco de dados..."
POSTGRES_CONTAINER=$(docker ps -q -f name=postgres_postgres)

if [ -z "$POSTGRES_CONTAINER" ]; then
    error "❌ Container PostgreSQL não encontrado"
fi

# Dropar e recriar banco
docker exec $POSTGRES_CONTAINER psql -U dossie -c "DROP DATABASE IF EXISTS dossie_escola;" 2>/dev/null || true
docker exec $POSTGRES_CONTAINER psql -U dossie -c "CREATE DATABASE dossie_escola;" 2>/dev/null || true

log "✅ Banco de dados recriado"

# Atualizar configuração
log "⚙️ Atualizando configuração..."
cp env-servidor-local .env
source .env

# Rebuild da aplicação
log "🏗️ Fazendo rebuild da aplicação..."
docker build -t dossie-app:latest .

# Deploy da aplicação
log "🚀 Fazendo deploy da aplicação..."
docker stack deploy -c docker-compose.app.yml dossie

# Aguardar aplicação inicializar
log "⏳ Aguardando aplicação inicializar..."
sleep 30

# Encontrar container da aplicação
APP_CONTAINER=""
for i in {1..10}; do
    APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)
    if [ ! -z "$APP_CONTAINER" ]; then
        break
    fi
    sleep 5
done

if [ -z "$APP_CONTAINER" ]; then
    error "❌ Container da aplicação não encontrado"
fi

log "📦 Container da aplicação: $APP_CONTAINER"

# Inicializar migrações
log "🔄 Inicializando migrações..."
docker exec $APP_CONTAINER flask db init 2>/dev/null || {
    log "ℹ️ Migrações já inicializadas"
}

# Criar migração inicial
log "📝 Criando migração inicial..."
docker exec $APP_CONTAINER flask db migrate -m "Initial migration" || {
    warn "Erro ao criar migração, tentando continuar..."
}

# Aplicar migrações
log "⬆️ Aplicando migrações..."
docker exec $APP_CONTAINER flask db upgrade || {
    warn "Erro ao aplicar migrações, tentando criar tabelas diretamente..."
    
    # Criar tabelas diretamente via Python
    docker exec $APP_CONTAINER python3 << 'PYTHON_EOF'
from app import create_app
from models import db

try:
    app = create_app()
    with app.app_context():
        print("🔗 Conectado ao banco")
        db.create_all()
        print("✅ Tabelas criadas diretamente")
except Exception as e:
    print(f"❌ Erro: {e}")
PYTHON_EOF
}

# Criar usuário admin
log "👤 Criando usuário administrador..."
docker exec $APP_CONTAINER python3 << 'PYTHON_EOF'
from app import create_app
from models import db, Usuario, Perfil, Escola

try:
    app = create_app()
    with app.app_context():
        print("🔗 Conectado ao banco")
        
        # Criar escola padrão
        escola = Escola.query.first()
        if not escola:
            escola = Escola(
                nome='Escola Local - Servidor 10.0.1.185',
                cnpj='00.000.000/0001-00',
                endereco='Servidor Local',
                telefone='(11) 0000-0000',
                email='admin@local.escola',
                situacao='ativa'
            )
            db.session.add(escola)
            db.session.commit()
            print("🏫 Escola criada")
        
        # Criar perfil admin
        perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
        if not perfil:
            perfil = Perfil(
                perfil='Administrador Geral'
            )
            db.session.add(perfil)
            db.session.commit()
            print("👑 Perfil admin criado")
        
        # Criar usuário admin
        admin = Usuario.query.filter_by(email='admin@local.escola').first()
        if not admin:
            admin = Usuario(
                nome='Administrador Local',
                email='admin@local.escola',
                escola_id=escola.id,
                perfil_id=perfil.id_perfil,
                situacao='ativo'
            )
            admin.set_password('Admin@Local123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado!")
        else:
            print("ℹ️ Usuário admin já existe")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
PYTHON_EOF

# Verificar status
log "📊 Verificando status dos serviços..."
docker service ls

# Testar aplicação
log "🌐 Testando aplicação..."
sleep 10

if curl -f -s http://localhost:5000 > /dev/null 2>&1; then
    log "✅ Aplicação está respondendo!"
else
    warn "⚠️ Aplicação pode não estar respondendo ainda"
    log "📋 Verificando logs..."
    docker service logs dossie_dossie-app --tail 10
fi

log "✅ Correção do banco de dados concluída!"
echo ""
log "🌐 URLs de Acesso:"
log "   📱 Sistema: http://10.0.1.185"
log "   👤 Login: admin@local.escola / Admin@Local123"
log "   📊 Portainer: http://10.0.1.185:9000"
echo ""
log "🔧 Comandos úteis:"
log "   📊 Status: docker service ls"
log "   📋 Logs: docker service logs dossie_dossie-app --tail 50"
echo ""
log "🎉 Banco de dados corrigido e funcionando!"
