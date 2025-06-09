"""
Sistema de Controle de Dossiê Escolar
Conforme especificação no CLAUDE.md
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from functools import wraps
import secrets
import uuid
from sqlalchemy import or_, and_

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dossie_escolar_completo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Importar e criar modelos
from models_completo import create_complete_models
(Escola, Cidade, Perfil, Usuario, Dossie, Solicitante, 
 Movimentacao, DocumentoDossie, LogAuditoria, LogSistema, 
 PermissaoCustomizada, ConfiguracaoEscola) = create_complete_models(db)

# Decorators de segurança
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.perfil_obj.nome != 'Administrador Geral':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def escola_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            abort(403)
        
        # Administrador Geral pode acessar tudo
        if usuario.perfil_obj.nome == 'Administrador Geral':
            return f(*args, **kwargs)
        
        # Outros usuários só acessam dados da sua escola
        session['escola_id'] = usuario.escola_id
        return f(*args, **kwargs)
    return decorated_function

def log_acao(acao, item_alterado=None, detalhes=None):
    """Função para registrar logs de auditoria"""
    if 'user_id' in session:
        log = LogAuditoria(
            usuario_id=session['user_id'],
            acao=acao,
            item_alterado=item_alterado,
            ip_address=request.remote_addr,
            navegador=request.headers.get('User-Agent'),
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()

# Rotas de autenticação
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index_completo.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Verificar se está bloqueado
            if usuario.bloqueado_ate and usuario.bloqueado_ate > datetime.now():
                flash(f'Usuário bloqueado até {usuario.bloqueado_ate.strftime("%d/%m/%Y %H:%M")}', 'error')
                return render_template('login_completo.html')
            
            if usuario.check_password(senha):
                # Login bem-sucedido
                usuario.tentativas_login = 0
                usuario.ultimo_acesso = datetime.now()
                usuario.bloqueado_ate = None
                db.session.commit()
                
                session['user_id'] = usuario.id
                session['user_nome'] = usuario.nome
                session['user_perfil'] = usuario.perfil_obj.nome
                session['escola_id'] = usuario.escola_id
                
                log_acao('LOGIN_SUCESSO', 'Usuario', f'Login realizado com sucesso')
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Senha incorreta
                usuario.tentativas_login += 1
                if usuario.tentativas_login >= 5:
                    usuario.bloqueado_ate = datetime.now() + timedelta(minutes=30)
                    flash('Muitas tentativas incorretas. Usuário bloqueado por 30 minutos.', 'error')
                else:
                    flash(f'Senha incorreta. Tentativas restantes: {5 - usuario.tentativas_login}', 'error')
                
                db.session.commit()
                log_acao('LOGIN_FALHA', 'Usuario', f'Tentativa de login falhada para {email}')
        else:
            flash('Email não encontrado!', 'error')
            log_acao('LOGIN_FALHA', 'Usuario', f'Tentativa de login com email inexistente: {email}')
    
    return render_template('login_completo.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_acao('LOGOUT', 'Usuario', 'Logout realizado')
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
@escola_access_required
def dashboard():
    usuario = Usuario.query.get(session['user_id'])
    
    # Estatísticas baseadas na escola do usuário (ou todas se for admin geral)
    if usuario.perfil_obj.nome == 'Administrador Geral':
        total_escolas = Escola.query.count()
        total_usuarios = Usuario.query.count()
        total_dossies = Dossie.query.count()
        total_movimentacoes = Movimentacao.query.count()
        escola_filter = None
    else:
        total_escolas = 1
        total_usuarios = Usuario.query.filter_by(escola_id=usuario.escola_id).count()
        total_dossies = Dossie.query.filter_by(escola_id=usuario.escola_id).count()
        total_movimentacoes = Movimentacao.query.filter_by(escola_id=usuario.escola_id).count()
        escola_filter = usuario.escola_id
    
    # Dossiês recentes
    if escola_filter:
        dossies_recentes = Dossie.query.filter_by(escola_id=escola_filter).order_by(Dossie.data_cadastro.desc()).limit(5).all()
        movimentacoes_recentes = Movimentacao.query.filter_by(escola_id=escola_filter).order_by(Movimentacao.data_solicitacao.desc()).limit(5).all()
    else:
        dossies_recentes = Dossie.query.order_by(Dossie.data_cadastro.desc()).limit(5).all()
        movimentacoes_recentes = Movimentacao.query.order_by(Movimentacao.data_solicitacao.desc()).limit(5).all()
    
    return render_template('dashboard_completo.html',
                         total_escolas=total_escolas,
                         total_usuarios=total_usuarios,
                         total_dossies=total_dossies,
                         total_movimentacoes=total_movimentacoes,
                         dossies_recentes=dossies_recentes,
                         movimentacoes_recentes=movimentacoes_recentes,
                         usuario=usuario)

# Rotas de Escolas (apenas para Administrador Geral)
@app.route('/escolas')
@admin_required
def listar_escolas():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Escola.query
    if search:
        query = query.filter(or_(
            Escola.nome.contains(search),
            Escola.cnpj.contains(search),
            Escola.inep.contains(search)
        ))
    
    escolas = query.order_by(Escola.nome).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('escolas/listar.html', escolas=escolas, search=search)

@app.route('/escolas/nova', methods=['GET', 'POST'])
@admin_required
def nova_escola():
    if request.method == 'POST':
        escola = Escola(
            nome=request.form['nome'],
            endereco=request.form['endereco'],
            uf=request.form['uf'],
            cnpj=request.form['cnpj'],
            inep=request.form['inep'],
            email=request.form['email'],
            diretor=request.form['diretor']
        )
        
        try:
            db.session.add(escola)
            db.session.commit()
            log_acao('CREATE', 'Escola', f'Escola criada: {escola.nome}')
            flash('Escola cadastrada com sucesso!', 'success')
            return redirect(url_for('listar_escolas'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar escola!', 'error')
    
    return render_template('escolas/nova.html')

# Rotas de Usuários
@app.route('/usuarios')
@login_required
@escola_access_required
def listar_usuarios():
    usuario_logado = Usuario.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Usuario.query
    
    # Filtrar por escola se não for admin geral
    if usuario_logado.perfil_obj.nome != 'Administrador Geral':
        query = query.filter_by(escola_id=usuario_logado.escola_id)
    
    if search:
        query = query.filter(or_(
            Usuario.nome.contains(search),
            Usuario.email.contains(search),
            Usuario.cpf.contains(search)
        ))
    
    usuarios = query.order_by(Usuario.nome).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('usuarios/listar.html', usuarios=usuarios, search=search)

def criar_dados_iniciais():
    """Criar dados iniciais do sistema"""
    
    # Criar perfis padrão
    perfis_padrao = [
        {'nome': 'Administrador Geral', 'descricao': 'Acesso total ao sistema', 'nivel_acesso': 5},
        {'nome': 'Administrador da Escola', 'descricao': 'Gerencia usuários e dossiês da escola', 'nivel_acesso': 4},
        {'nome': 'Usuário Operacional', 'descricao': 'Uso operacional (cadastro e busca)', 'nivel_acesso': 2}
    ]
    
    for perfil_data in perfis_padrao:
        if not Perfil.query.filter_by(nome=perfil_data['nome']).first():
            perfil = Perfil(**perfil_data)
            db.session.add(perfil)
    
    # Criar cidade padrão
    if not Cidade.query.first():
        cidade = Cidade(nome='São Paulo', uf='SP', pais='Brasil')
        db.session.add(cidade)
    
    # Criar escola padrão
    if not Escola.query.first():
        escola = Escola(
            nome='Escola Municipal Exemplo',
            endereco='Rua das Flores, 123',
            uf='SP',
            cnpj='12.345.678/0001-90',
            inep='12345678',
            email='escola@exemplo.com',
            diretor='João Silva'
        )
        db.session.add(escola)
    
    db.session.commit()
    
    # Criar usuário admin padrão
    perfil_admin = Perfil.query.filter_by(nome='Administrador Geral').first()
    escola_padrao = Escola.query.first()
    
    if not Usuario.query.filter_by(email='admin@sistema.com').first():
        admin = Usuario(
            nome='Administrador do Sistema',
            email='admin@sistema.com',
            cpf='000.000.000-00',
            perfil_id=perfil_admin.id,
            escola_id=escola_padrao.id
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado: admin@sistema.com / admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Criar dados iniciais
        criar_dados_iniciais()

    app.run(debug=True, host='0.0.0.0', port=5000)
