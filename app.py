"""
Sistema de Controle de Dossiê Escolar
Aplicação robusta e segura para 15 escolas
Organizada por entidades para facilitar manutenção
"""

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_migrate import Migrate
from datetime import datetime
import secrets
import os

# Configuração da aplicação
def create_app():
    """Factory para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações de segurança
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dossie-escolar-secret-key-2024'

    # Configuração do banco de dados com suporte a PostgreSQL
    database_url = os.environ.get('DATABASE_URL') or 'postgresql://dossie:fep09151@localhost/dossie_escola'

    # Testar PostgreSQL e fallback para SQLite
    if 'postgresql://' in database_url:
        try:
            from sqlalchemy import create_engine
            engine = create_engine(database_url)
            with engine.connect():
                pass  # Teste de conexão
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            print("✅ Conectado ao PostgreSQL")
        except Exception as e:
            print(f"⚠️  PostgreSQL indisponível, usando SQLite: {e}")
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dossie_escolar.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Configurações de upload
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    
    # Inicializar banco de dados
    from models import db
    db.init_app(app)

    # Inicializar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Registrar blueprints (controladores)
    from controllers import auth_bp, escola_bp, usuario_bp, dossie_bp, movimentacao_bp, cidade_bp, perfil_bp, anexo_bp
    from controllers.permissao_controller import permissao_bp
    from controllers.diretor_controller import diretor_bp
    from controllers.solicitante_controller import solicitante_bp
    from admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(escola_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(dossie_bp)
    app.register_blueprint(movimentacao_bp)
    app.register_blueprint(cidade_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(anexo_bp)
    app.register_blueprint(diretor_bp)
    app.register_blueprint(permissao_bp)
    app.register_blueprint(solicitante_bp)
    app.register_blueprint(admin_bp)
    
    # Rotas principais
    @app.route('/')
    def index():
        """Página inicial - redireciona para dashboard ou login"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal do sistema"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        from models import Usuario, Escola, Dossie, Movimentacao
        
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))
        
        # Estatísticas para o dashboard
        if usuario.is_admin_geral():
            # Admin geral vê estatísticas globais
            stats = {
                'total_escolas': Escola.query.count(),
                'total_usuarios': Usuario.query.count(),
                'total_dossies': Dossie.query.count(),
                'total_movimentacoes': Movimentacao.query.count(),
                'escolas_ativas': Escola.query.filter_by(situacao='ativa').count(),
                'usuarios_ativos': Usuario.query.filter_by(status='ativo').count(),
                'dossies_ativos': Dossie.query.filter_by(status='ativo').count(),
                'movimentacoes_pendentes': Movimentacao.query.filter_by(status='pendente').count()
            }
        else:
            # Usuários da escola veem apenas dados da sua escola
            stats = {
                'total_escolas': 1,
                'total_usuarios': Usuario.query.filter_by(escola_id=usuario.escola_id).count(),
                'total_dossies': Dossie.query.filter_by(escola_id=usuario.escola_id).count(),
                'total_movimentacoes': Movimentacao.query.join(Dossie).filter(Dossie.escola_id == usuario.escola_id).count(),
                'escolas_ativas': 1 if usuario.escola.is_ativa else 0,
                'usuarios_ativos': Usuario.query.filter_by(escola_id=usuario.escola_id, situacao='ativo').count(),
                'dossies_ativos': Dossie.query.filter_by(escola_id=usuario.escola_id, situacao='ativo').count(),
                'movimentacoes_pendentes': Movimentacao.query.join(Dossie).filter(
                    Dossie.escola_id == usuario.escola_id,
                    Movimentacao.status == 'pendente'
                ).count()
            }
        
        return render_template('dashboard_novo.html', usuario=usuario, stats=stats)
    
    # Filtros personalizados para templates
    @app.template_filter('age')
    def calculate_age(birthdate):
        """Calcula idade a partir da data de nascimento"""
        if birthdate:
            today = datetime.now().date()
            return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return None
    
    @app.template_filter('format_cpf')
    def format_cpf(cpf):
        """Formata CPF para exibição"""
        if cpf and len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @app.template_filter('format_cnpj')
    def format_cnpj(cnpj):
        """Formata CNPJ para exibição"""
        if cnpj and len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    # Handlers de erro
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from models import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    # Context processor para variáveis globais
    @app.context_processor
    def inject_globals():
        """Injeta variáveis globais nos templates"""
        return {
            'current_year': datetime.now().year,
            'app_name': 'Sistema de Controle de Dossiê Escolar',
            'app_version': '2.0.0'
        }
    
    # Funções de permissão para templates
    @app.context_processor
    def inject_permission_functions():
        from utils.permissions import has_permission, can_access_menu
        from models import Usuario

        def get_current_user():
            if 'user_id' in session:
                return Usuario.query.get(session['user_id'])
            return None

        def can_view(usuario, modulo):
            if not usuario:
                return False
            return has_permission(usuario, modulo, 'visualizar')

        def can_create(usuario, modulo):
            if not usuario:
                return False
            return has_permission(usuario, modulo, 'criar')

        def can_edit(usuario, modulo):
            if not usuario:
                return False
            return has_permission(usuario, modulo, 'editar')

        def can_delete(usuario, modulo):
            if not usuario:
                return False
            return has_permission(usuario, modulo, 'excluir')

        def can_access_menu_func(usuario, menu_tipo):
            if not usuario:
                return False
            return can_access_menu(usuario, menu_tipo)

        def is_admin_geral(usuario):
            if not usuario or not usuario.perfil_obj:
                return False
            return usuario.perfil_obj.perfil == 'Administrador Geral'

        return dict(
            get_current_user=get_current_user,
            can_view=can_view,
            can_create=can_create,
            can_edit=can_edit,
            can_delete=can_delete,
            can_access_menu=can_access_menu_func,
            has_permission=has_permission,
            is_admin_geral=is_admin_geral
        )

    return app

def init_database(app):
    """Inicializa o banco de dados com dados padrão"""
    with app.app_context():
        from models import db, Perfil, Cidade, Escola, Usuario
        
        # Criar tabelas
        db.create_all()
        
        # Criar perfis padrão
        if not Perfil.query.first():
            perfis = [
                Perfil(perfil='Administrador Geral'),
                Perfil(perfil='Administrador da Escola'),
                Perfil(perfil='Operador'),
                Perfil(perfil='Consulta')
            ]
            for perfil in perfis:
                db.session.add(perfil)
            db.session.commit()
            print("✅ Perfis criados")
        
        # Criar cidade padrão
        if not Cidade.query.first():
            cidade = Cidade(nome='São Paulo', uf='SP', codigo_ibge='3550308')
            db.session.add(cidade)
            db.session.commit()
            print("✅ Cidade padrão criada")
        
        # Criar escola padrão
        if not Escola.query.first():
            cidade_padrao = Cidade.query.first()
            escola = Escola(
                nome='Escola Municipal Exemplo',
                endereco='Rua das Flores, 123',
                uf='SP',
                cnpj='12.345.678/0001-90',
                inep='12345678',
                email='escola@exemplo.gov.br',
                diretor='João Silva',
                id_cidade=cidade_padrao.id if cidade_padrao else None
            )
            db.session.add(escola)
            db.session.commit()
            print("✅ Escola padrão criada")
        
        # Criar usuário administrador
        if not Usuario.query.filter_by(email='admin@sistema.com').first():
            perfil_admin = Perfil.query.filter_by(nome='Administrador Geral').first()
            escola_padrao = Escola.query.first()
            
            admin = Usuario(
                nome='Administrador do Sistema',
                email='admin@sistema.com',
                cpf='000.000.000-00',
                telefone='(11) 99999-9999',
                perfil_id=perfil_admin.id,
                escola_id=escola_padrao.id,
                situacao='ativo',
                data_nascimento=datetime(1980, 1, 1).date()
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado: admin@sistema.com / admin123")

if __name__ == '__main__':
    app = create_app()
    
    # Inicializar banco de dados
    init_database(app)
    
    print("🚀 Sistema de Controle de Dossiê Escolar Iniciado")
    print("🌐 Acesse: http://localhost:5000")
    print("👤 Login: admin@sistema.com / admin123")
    print("📁 Aplicação organizada por entidades")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
