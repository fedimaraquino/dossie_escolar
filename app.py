"""
Sistema de Controle de Dossiê Escolar
Aplicação robusta e segura para 15 escolas
Organizada por entidades para facilitar manutenção
"""

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import secrets
import os
from sqlalchemy import func
from werkzeug.security import generate_password_hash

# Importar db dos modelos
from models import db

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
            print("Conectado ao PostgreSQL")
        except Exception as e:
            print(f"PostgreSQL indisponivel, usando SQLite: {e}")
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

    # Configurações de segurança de sessão
    app.config['SESSION_COOKIE_SECURE'] = False  # Permitir HTTP para desenvolvimento
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Não acessível via JavaScript
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Proteção CSRF
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora de timeout

    # Inicializar banco de dados
    db.init_app(app)

    # Inicializar Rate Limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Inicializar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Registrar blueprints (controladores)
    with app.app_context():
        from controllers import auth_bp, escola_bp, usuario_bp, dossie_bp, movimentacao_bp, cidade_bp, perfil_bp, anexo_bp
        from controllers.permissao_controller import permissao_bp
        from controllers.diretor_controller import diretor_bp
        from controllers.solicitante_controller import solicitantes_bp
        from controllers.configuracao_controller import config_bp
        from controllers.foto_controller import foto_bp
        from controllers.relatorio_controller import relatorio_bp
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
    app.register_blueprint(solicitantes_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(foto_bp)
    app.register_blueprint(relatorio_bp)
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
        """Dashboard otimizado do sistema"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        from models import Usuario, Escola, Dossie, Movimentacao
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))

        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)
        escola_atual_id = session.get('escola_atual_id') or usuario.escola_id
        escola_atual = Escola.query.get(escola_atual_id)
        escola_nome = escola_atual.nome if escola_atual else 'Escola Atual'

        # Indicadores principais
        stats = {
            'total_dossies': Dossie.query.filter_by(id_escola=escola_atual_id).count(),
            'dossies_ativos': Dossie.query.filter_by(id_escola=escola_atual_id, status='ativo').count(),
            'dossies_pendentes': Dossie.query.filter_by(id_escola=escola_atual_id, status='pendente').count(),
            'movimentacoes_mes': Movimentacao.query.join(Dossie).filter(
                Dossie.id_escola == escola_atual_id,
                Movimentacao.data_movimentacao >= inicio_mes
            ).count()
        }

        # Alertas
        alertas = {
            'dossies_pendentes': stats['dossies_pendentes'],
            'movimentacoes_atrasadas': Movimentacao.query.join(Dossie).filter(
                Dossie.id_escola == escola_atual_id,
                Movimentacao.status == 'pendente',
                Movimentacao.data_prevista_devolucao != None,
                Movimentacao.data_prevista_devolucao < hoje
            ).count()
        }

        # Gráficos
        graficos = {'evolucao_mensal': [], 'tipos_movimentacao': [], 'status_dossies': []}
        for i in range(5, -1, -1):
            mes_inicio = (hoje.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            count = Dossie.query.filter(
                Dossie.id_escola == escola_atual_id,
                Dossie.dt_cadastro >= mes_inicio,
                Dossie.dt_cadastro <= mes_fim
            ).count()
            graficos['evolucao_mensal'].append({
                'mes': mes_inicio.strftime('%b/%Y'),
                'count': count
            })
        tipos_mov = db.session.query(
            Movimentacao.tipo_movimentacao,
            func.count(Movimentacao.id)
        ).join(Dossie).filter(Dossie.id_escola == escola_atual_id).group_by(Movimentacao.tipo_movimentacao).all()
        graficos['tipos_movimentacao'] = [
            {'tipo': tipo or 'Outro', 'count': count} for tipo, count in tipos_mov
        ]
        status_counts = db.session.query(
            Dossie.status,
            func.count(Dossie.id_dossie)
        ).filter(Dossie.id_escola == escola_atual_id).group_by(Dossie.status).all()
        graficos['status_dossies'] = [
            {'status': status.title(), 'count': count} for status, count in status_counts
        ]

        return render_template('dashboard.html',
            usuario=usuario,
            stats=stats,
            alertas=alertas,
            graficos=graficos,
            escola_nome=escola_nome,
            current_date=datetime.now()
        )

    @app.route('/dashboard/avancado')
    def dashboard_avancado():
        """Dashboard avançado (mais lento)"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        from models import Usuario, Escola, Dossie, Movimentacao, Perfil

        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))
        
        # Estatísticas avançadas para o dashboard
        from datetime import datetime, timedelta
        from sqlalchemy import func, extract

        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)
        inicio_ano = hoje.replace(month=1, day=1)

        # Obter escola atual
        escola_atual_id = usuario.get_escola_atual_id()

        if usuario.is_admin_geral():
            # Admin geral vê estatísticas da escola atual selecionada
            stats = {
                # Totais básicos
                'total_escolas': Escola.query.count(),
                'total_usuarios': Usuario.query.count(),
                'total_dossies': Dossie.query.count(),
                'total_movimentacoes': Movimentacao.query.count(),

                # Status específicos
                'escolas_ativas': Escola.query.filter_by(situacao='ativa').count(),
                'usuarios_ativos': Usuario.query.filter_by(situacao='ativo').count(),
                'dossies_ativos': Dossie.query.filter_by(situacao='ativo').count(),
                'movimentacoes_pendentes': Movimentacao.query.filter_by(status='pendente').count(),

                # Dados para gráficos - Dossiês por mês (últimos 6 meses)
                'dossies_por_mes': [],

                # Movimentações por tipo
                'movimentacoes_por_tipo': [],

                # Usuários por perfil
                'usuarios_por_perfil': [],

                # Atividade recente (últimos 30 dias)
                'dossies_mes_atual': Dossie.query.filter(Dossie.dt_cadastro >= inicio_mes).count(),
                'movimentacoes_mes_atual': Movimentacao.query.filter(Movimentacao.data_movimentacao >= inicio_mes).count(),
                'usuarios_mes_atual': Usuario.query.filter(Usuario.data_cadastro >= inicio_mes).count(),

                # Crescimento anual
                'dossies_ano_atual': Dossie.query.filter(Dossie.dt_cadastro >= inicio_ano).count(),
                'movimentacoes_ano_atual': Movimentacao.query.filter(Movimentacao.data_movimentacao >= inicio_ano).count()
            }

            # Dados para gráfico de dossiês por mês (últimos 6 meses)
            for i in range(6):
                mes_inicio = (hoje.replace(day=1) - timedelta(days=i*30)).replace(day=1)
                mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                count = Dossie.query.filter(
                    Dossie.dt_cadastro >= mes_inicio,
                    Dossie.dt_cadastro <= mes_fim
                ).count()
                stats['dossies_por_mes'].insert(0, {
                    'mes': mes_inicio.strftime('%b/%Y'),
                    'count': count
                })

            # Movimentações por tipo
            tipos_mov = db.session.query(
                Movimentacao.tipo_movimentacao,
                func.count(Movimentacao.id).label('count')
            ).group_by(Movimentacao.tipo_movimentacao).all()

            stats['movimentacoes_por_tipo'] = [{'tipo': tipo, 'count': count} for tipo, count in tipos_mov]

            # Usuários por perfil
            usuarios_perfil = db.session.query(
                Perfil.perfil,
                func.count(Usuario.id).label('count')
            ).join(Usuario).group_by(Perfil.perfil).all()

            stats['usuarios_por_perfil'] = [{'perfil': perfil, 'count': count} for perfil, count in usuarios_perfil]

        else:
            # Usuários da escola veem apenas dados da sua escola
            stats = {
                'total_escolas': 1,
                'total_usuarios': Usuario.query.filter_by(escola_id=usuario.escola_id).count(),
                'total_dossies': Dossie.query.filter_by(escola_id=usuario.escola_id).count(),
                'total_movimentacoes': Movimentacao.query.join(Dossie).filter(Dossie.escola_id == usuario.escola_id).count(),
                'escolas_ativas': 1 if usuario.escola.situacao == 'ativa' else 0,
                'usuarios_ativos': Usuario.query.filter_by(escola_id=usuario.escola_id, situacao='ativo').count(),
                'dossies_ativos': Dossie.query.filter_by(escola_id=usuario.escola_id, situacao='ativo').count(),
                'movimentacoes_pendentes': Movimentacao.query.join(Dossie).filter(
                    Dossie.escola_id == usuario.escola_id,
                    Movimentacao.status == 'pendente'
                ).count(),

                # Dados específicos da escola
                'dossies_por_mes': [],
                'movimentacoes_por_tipo': [],
                'dossies_mes_atual': Dossie.query.filter(
                    Dossie.id_escola == usuario.escola_id,
                    Dossie.dt_cadastro >= inicio_mes
                ).count(),
                'movimentacoes_mes_atual': Movimentacao.query.join(Dossie).filter(
                    Dossie.id_escola == usuario.escola_id,
                    Movimentacao.data_movimentacao >= inicio_mes
                ).count()
            }

            # Dados para gráficos da escola específica
            for i in range(6):
                mes_inicio = (hoje.replace(day=1) - timedelta(days=i*30)).replace(day=1)
                mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                count = Dossie.query.filter(
                    Dossie.id_escola == usuario.escola_id,
                    Dossie.dt_cadastro >= mes_inicio,
                    Dossie.dt_cadastro <= mes_fim
                ).count()
                stats['dossies_por_mes'].insert(0, {
                    'mes': mes_inicio.strftime('%b/%Y'),
                    'count': count
                })

            # Movimentações por tipo da escola
            tipos_mov = db.session.query(
                Movimentacao.tipo_movimentacao,
                func.count(Movimentacao.id).label('count')
            ).join(Dossie).filter(
                Dossie.id_escola == usuario.escola_id
            ).group_by(Movimentacao.tipo_movimentacao).all()

            stats['movimentacoes_por_tipo'] = [{'tipo': tipo, 'count': count} for tipo, count in tipos_mov]
        
        return render_template('dashboard_novo.html', usuario=usuario, stats=stats, current_date=datetime.now())
    
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
    
    def situacao_badge(status):
        cores = {
            'ativo': 'success',
            'inativo': 'secondary',
            'arquivado': 'warning',
            'pendente': 'danger',
            'emprestado': 'info'
        }
        return cores.get(status, 'secondary')

    def situacao_label(status):
        labels = {
            'ativo': 'Ativo',
            'inativo': 'Inativo',
            'arquivado': 'Arquivado',
            'pendente': 'Pendente',
            'emprestado': 'Emprestado'
        }
        return labels.get(status, status.title())

    app.jinja_env.filters['situacao_badge'] = situacao_badge
    app.jinja_env.filters['situacao_label'] = situacao_label

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
    with app.app_context():
        # Imports necessários para esta função
        from models import Perfil, Cidade, Escola, Usuario, db
        from werkzeug.security import generate_password_hash
        
        db.create_all()

        # --- Etapa 1: Perfis ---
        if not Perfil.query.filter_by(perfil='Administrador Geral').first():
            print("👤 Criando perfis padrão...")
            perfis = [
                {'perfil': 'Administrador Geral', 'descricao': 'Acesso total ao sistema.'},
                {'perfil': 'Diretor', 'descricao': 'Acesso de gerenciamento da sua escola.'},
                {'perfil': 'Secretário', 'descricao': 'Acesso operacional da sua escola.'},
                {'perfil': 'Convidado', 'descricao': 'Acesso de apenas leitura.'}
            ]
            for p_info in perfis:
                db.session.add(Perfil(**p_info))
            db.session.commit()
            print("✅ Perfis criados")

        # --- Etapa 2: Cidade ---
        cidade = Cidade.query.filter_by(nome='São Paulo', uf='SP').first()
        if not cidade:
            print("🏙️ Criando cidade padrão...")
            cidade = Cidade(nome='São Paulo', uf='SP')
            db.session.add(cidade)
            db.session.commit()
            cidade = Cidade.query.filter_by(nome='São Paulo', uf='SP').first() # Recarregar para ter o ID
            print("✅ Cidade padrão criada")

        # --- Etapa 3: Escola ---
        escola = Escola.query.filter_by(nome='Escola Matriz').first()
        if not escola:
            print("🏫 Criando escola padrão...")
            escola = Escola(nome='Escola Matriz', uf='SP', id_cidade=cidade.id)
            db.session.add(escola)
            db.session.commit()
            escola = Escola.query.filter_by(nome='Escola Matriz').first() # Recarregar para ter o ID
            print("✅ Escola padrão criada")

        # --- Etapa 4: Usuário Administrador ---
        if not Usuario.query.filter_by(email='admin@sistema.com').first():
            print("👮 Criando usuário administrador...")
            perfil_admin = Perfil.query.filter_by(perfil='Administrador Geral').first()
            
            if perfil_admin and escola:
                usuario_admin = Usuario(
                    nome='Administrador do Sistema',
                    email='admin@sistema.com',
                    escola_id=escola.id,
                    perfil_id=perfil_admin.id,
                    situacao='ativo',
                    # Definindo a senha diretamente com hash para evitar a validação complexa no primeiro login
                    senha_hash=generate_password_hash('Admin@123')
                )
                db.session.add(usuario_admin)
                db.session.commit()
                print("✅ Usuário administrador criado")
            else:
                print("❌ ERRO CRÍTICO: Perfil de admin ou escola padrão não encontrados. Usuário admin não foi criado.")

# Criar instância da aplicação para Gunicorn
app = create_app()

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database(app)
    
    print("Sistema de Controle de Dossie Escolar Iniciado")
    print("Acesse: http://localhost:5000")
    print("Login: admin@sistema.com / admin123")
    print("Aplicacao organizada por entidades")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
