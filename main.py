"""
Sistema de Controle de Dossiê Escolar - Aplicação Principal
Arquitetura Modular conforme CLAUDE.md
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import secrets

# Configuração da aplicação principal
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dossie_escolar_modular.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Criar pasta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar banco de dados
db = SQLAlchemy(app)

def create_app():
    """Factory function para criar a aplicação"""
    
    # Registrar blueprints das aplicações modulares
    from apps.auth.routes import auth_bp
    from apps.escolas.routes import escolas_bp
    from apps.usuarios.routes import usuarios_bp
    from apps.dossies.routes import dossies_bp
    from apps.movimentacoes.routes import movimentacoes_bp
    from apps.solicitantes.routes import solicitantes_bp
    from apps.logs.routes import logs_bp
    from apps.core.routes import core_bp
    from apps.relatorios.routes import relatorios_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(escolas_bp, url_prefix='/escolas')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(dossies_bp, url_prefix='/dossies')
    app.register_blueprint(movimentacoes_bp, url_prefix='/movimentacoes')
    app.register_blueprint(solicitantes_bp, url_prefix='/solicitantes')
    app.register_blueprint(logs_bp, url_prefix='/logs')
    app.register_blueprint(core_bp, url_prefix='/core')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    
    return app

# Rota principal
@app.route('/')
def index():
    try:
        from apps.auth.routes import verificar_login
        if verificar_login():
            from apps.core.routes import dashboard
            return dashboard()
        else:
            from apps.auth.routes import login_page
            return login_page()
    except ImportError:
        return render_template('index_simples.html')

def init_database():
    """Inicializar banco de dados e dados padrão"""
    with app.app_context():
        # Importar todos os modelos para criar as tabelas
        from apps.core.models import Cidade, Perfil, ConfiguracaoEscola
        from apps.escolas.models import Escola
        from apps.usuarios.models import Usuario
        from apps.dossies.models import Dossie, DocumentoDossie
        from apps.movimentacoes.models import Movimentacao
        from apps.solicitantes.models import Solicitante
        from apps.logs.models import LogAuditoria, LogSistema
        
        # Criar todas as tabelas
        db.create_all()
        
        # Criar dados iniciais
        from apps.core.utils import criar_dados_iniciais
        criar_dados_iniciais()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("📊 Dados iniciais criados!")
        print("🔑 Login: admin@sistema.com / admin123")

if __name__ == '__main__':
    # Criar aplicação
    app = create_app()

    # Inicializar banco de dados dentro do contexto da aplicação
    with app.app_context():
        init_database()

    # Executar aplicação
    print("🚀 Iniciando Sistema de Controle de Dossiê Escolar")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Login padrão: admin@sistema.com / admin123")
    print("-" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
