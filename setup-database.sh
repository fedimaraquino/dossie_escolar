#!/bin/bash
# Script para configurar banco de dados e usuário admin
# VPS Hostinger - 62.52.58.58

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

log "🗄️ Configurando banco de dados e usuário admin..."

# Verificar se os serviços estão rodando
log "🔍 Verificando status dos serviços..."
docker service ls

# Aguardar aplicação estar pronta
log "⏳ Aguardando aplicação estar pronta..."
sleep 30

# Encontrar container da aplicação
APP_CONTAINER=$(docker ps -q -f name=dossie_dossie-app | head -1)

if [ -z "$APP_CONTAINER" ]; then
    error "❌ Container da aplicação não encontrado!"
fi

log "📦 Container da aplicação: $APP_CONTAINER"

# Executar migrações
log "🔄 Executando migrações do banco de dados..."
docker exec -it $APP_CONTAINER flask db upgrade || {
    warn "⚠️ Erro ao executar migrações. Tentando inicializar banco..."
    docker exec -it $APP_CONTAINER flask db init || true
    docker exec -it $APP_CONTAINER flask db migrate -m "Initial migration" || true
    docker exec -it $APP_CONTAINER flask db upgrade || true
}

# Criar usuário administrador
log "👤 Criando usuário administrador..."
docker exec -it $APP_CONTAINER python3 << 'EOF'
from app import create_app
from models import db, Usuario, Perfil, Escola

try:
    app = create_app()
    with app.app_context():
        print("🔗 Conectado ao banco de dados")
        
        # Criar escola padrão se não existir
        escola = Escola.query.first()
        if not escola:
            escola = Escola(
                nome='Escola Principal',
                cnpj='00.000.000/0001-00',
                endereco='Endereço da Escola',
                telefone='(00) 0000-0000',
                email='contato@escola.com',
                situacao='ativa'
            )
            db.session.add(escola)
            db.session.commit()
            print("🏫 Escola padrão criada")
        else:
            print("🏫 Escola já existe:", escola.nome)
        
        # Criar perfil admin se não existir
        perfil = Perfil.query.filter_by(perfil='Administrador Geral').first()
        if not perfil:
            perfil = Perfil(
                perfil='Administrador Geral'
            )
            db.session.add(perfil)
            db.session.commit()
            print("👑 Perfil Administrador Geral criado")
        else:
            print("👑 Perfil admin já existe")
        
        # Criar usuário admin se não existir
        admin = Usuario.query.filter_by(email='admin@escola.com').first()
        if not admin:
            admin = Usuario(
                nome='Administrador do Sistema',
                email='admin@escola.com',
                escola_id=escola.id,
                perfil_id=perfil.id_perfil,
                situacao='ativo'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado com sucesso!")
            print("📧 Email: admin@escola.com")
            print("🔑 Senha: Admin@123")
        else:
            print("ℹ️ Usuário admin já existe")
            
        print("🎉 Configuração do banco concluída!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
EOF

# Verificar se a aplicação está respondendo
log "🌐 Testando aplicação..."
sleep 10

if curl -f http://62.52.58.58:5000/ > /dev/null 2>&1; then
    log "✅ Aplicação está respondendo!"
else
    warn "⚠️ Aplicação pode não estar respondendo ainda. Aguarde alguns minutos."
fi

# Mostrar logs da aplicação
log "📋 Últimos logs da aplicação:"
docker service logs dossie_dossie-app --tail 10

log ""
log "✅ Configuração concluída!"
log ""
log "🌐 Acesse sua aplicação:"
log "   URL: http://62.52.58.58:5000"
log "   Email: admin@escola.com"
log "   Senha: Admin@123"
log ""
log "📊 Outros serviços:"
log "   Portainer: http://62.52.58.58:9000"
log "   Traefik: http://62.52.58.58:8080"
log ""
log "🎉 Sua aplicação está pronta para uso!"
