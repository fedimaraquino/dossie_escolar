"""
Sistema de Controle de Dossiê Escolar
Aplicação organizada por entidades
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import secrets

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dossie_escolar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db = SQLAlchemy(app)

# Modelos básicos
class Perfil(db.Model):
    __tablename__ = 'perfis'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    nivel_acesso = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<Perfil {self.nome}>'

class Cidade(db.Model):
    __tablename__ = 'cidades'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)

    def __repr__(self):
        return f'<Cidade {self.nome}/{self.uf}>'

class Escola(db.Model):
    __tablename__ = 'escolas'

    id = db.Column(db.Integer, primary_key=True)  # id_escola na especificação
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text)
    id_cidade = db.Column(db.Integer, db.ForeignKey('cidades.id'))  # FK - Cidade associada
    situacao = db.Column(db.String(20), default='ativa')  # Situação da escola (ativa/inativa)
    inep = db.Column(db.String(20))  # Código INEP
    email = db.Column(db.String(120))  # Email institucional
    uf = db.Column(db.String(2), nullable=False)  # Unidade federativa (estado)
    cnpj = db.Column(db.String(18))  # CNPJ da escola
    diretor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # FK - Diretor responsável
    data_cadastro = db.Column(db.DateTime, default=datetime.now)  # Data de inclusão no sistema
    data_saida = db.Column(db.DateTime)  # Data de desativação

    # Campos extras mantidos para compatibilidade
    telefone = db.Column(db.String(20))
    diretor = db.Column(db.String(100))  # Nome do diretor (texto)
    vice_diretor = db.Column(db.String(100))
    observacoes = db.Column(db.Text)

    # Relacionamentos
    cidade = db.relationship('Cidade', backref='escolas')
    diretor_obj = db.relationship('Usuario', foreign_keys=[diretor_id], backref='escolas_dirigidas')

    def __repr__(self):
        return f'<Escola {self.nome}>'

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)  # id_usuario na especificação
    nome = db.Column(db.String(100), nullable=False)  # Nome completo
    cpf = db.Column(db.String(14))  # CPF
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email
    telefone = db.Column(db.String(20))  # Telefone (corrigindo "tefenone")
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)  # FK - Escola vinculada
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)  # FK - Perfil de permissão
    situacao = db.Column(db.String(20), default='ativo')  # Status (ativo/inativo)
    ultimo_acesso = db.Column(db.DateTime)  # Data/hora do último login
    data_nascimento = db.Column(db.Date)  # Data de nascimento
    data_registro = db.Column(db.DateTime, default=datetime.now)  # Data de cadastro

    # Campos extras mantidos para compatibilidade
    senha_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='ativo')  # Mantido para compatibilidade
    data_cadastro = db.Column(db.DateTime, default=datetime.now)  # Mantido para compatibilidade

    # Relacionamentos
    perfil_obj = db.relationship('Perfil', backref='usuarios')
    escola = db.relationship('Escola', foreign_keys=[escola_id], backref='usuarios')

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

# Rotas
@app.route('/')
def index():
    # Redirecionar direto para login se não estiver logado
    if 'user_id' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha):
            session['user_id'] = usuario.id
            session['user_nome'] = usuario.nome
            session['user_perfil'] = usuario.perfil_obj.nome
            session['escola_id'] = usuario.escola_id
            
            usuario.ultimo_acesso = datetime.now()
            db.session.commit()
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos!', 'error')
    
    return render_template('login_modular.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['user_id'])

    # Adicionar dados do usuário na sessão para o template
    session['user_nome'] = usuario.nome
    session['user_perfil'] = usuario.perfil_obj.nome

    # Estatísticas básicas
    stats = {
        'total_escolas': Escola.query.count(),
        'total_usuarios': Usuario.query.count(),
        'total_dossies': 0,  # Placeholder
        'total_movimentacoes': 0  # Placeholder
    }

    return render_template('dashboard_novo.html', usuario=usuario, stats=stats)

# Aplicações modulares (rotas básicas)
@app.route('/escolas/')
def escolas_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    # Busca com paginação
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = Escola.query
    if search:
        query = query.filter(
            db.or_(
                Escola.nome.contains(search),
                Escola.cnpj.contains(search),
                Escola.inep.contains(search)
            )
        )

    escolas = query.paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('escolas/listar.html', escolas=escolas, search=search)

@app.route('/escolas/nova', methods=['GET', 'POST'])
def escolas_nova():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip()

        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/nova.html')

        escola = Escola(
            nome=nome,
            endereco=request.form.get('endereco', '').strip(),
            uf=uf,
            cnpj=request.form.get('cnpj', '').strip(),
            inep=request.form.get('inep', '').strip(),
            email=request.form.get('email', '').strip(),
            telefone=request.form.get('telefone', '').strip(),
            diretor=request.form.get('diretor', '').strip(),
            vice_diretor=request.form.get('vice_diretor', '').strip(),
            observacoes=request.form.get('observacoes', '').strip(),
            id_cidade=request.form.get('id_cidade') if request.form.get('id_cidade') else None,
            diretor_id=request.form.get('diretor_id') if request.form.get('diretor_id') else None
        )

        try:
            db.session.add(escola)
            db.session.commit()
            flash('Escola cadastrada com sucesso!', 'success')
            return redirect(url_for('escolas_listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar escola: {str(e)}', 'error')

    return render_template('escolas/nova.html')

@app.route('/escolas/ver/<int:id>')
def escolas_ver(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    escola = Escola.query.get_or_404(id)
    return render_template('escolas/ver.html', escola=escola)

@app.route('/escolas/editar/<int:id>', methods=['GET', 'POST'])
def escolas_editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    escola = Escola.query.get_or_404(id)

    if request.method == 'POST':
        escola.nome = request.form.get('nome', '').strip()
        escola.endereco = request.form.get('endereco', '').strip()
        escola.uf = request.form.get('uf', '').strip()
        escola.cnpj = request.form.get('cnpj', '').strip()
        escola.inep = request.form.get('inep', '').strip()
        escola.email = request.form.get('email', '').strip()
        escola.telefone = request.form.get('telefone', '').strip()
        escola.diretor = request.form.get('diretor', '').strip()
        escola.vice_diretor = request.form.get('vice_diretor', '').strip()
        escola.observacoes = request.form.get('observacoes', '').strip()
        escola.id_cidade = request.form.get('id_cidade') if request.form.get('id_cidade') else None
        escola.diretor_id = request.form.get('diretor_id') if request.form.get('diretor_id') else None
        escola.situacao = request.form.get('situacao', 'ativa')

        if not escola.nome or not escola.uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/editar_novo.html', escola=escola)

        try:
            db.session.commit()
            flash('Escola atualizada com sucesso!', 'success')
            return redirect('/escolas/')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar escola: {str(e)}', 'error')

    return render_template('escolas/editar_novo.html', escola=escola)

@app.route('/escolas/excluir/<int:id>', methods=['POST'])
def escolas_excluir(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    escola = Escola.query.get_or_404(id)

    try:
        db.session.delete(escola)
        db.session.commit()
        flash(f'Escola "{escola.nome}" excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir escola: {str(e)}', 'error')

    return redirect('/escolas/')

@app.route('/escolas/configuracoes/<int:id>')
def escolas_configuracoes(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get(session['user_id'])
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    escola = Escola.query.get_or_404(id)
    return render_template('escolas/configuracoes.html', escola=escola)

@app.route('/usuarios/')
def usuarios_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Busca com paginação
    search = request.args.get('search', '')
    escola_id = request.args.get('escola', '')
    perfil_id = request.args.get('perfil', '')
    situacao = request.args.get('situacao', '')
    page = request.args.get('page', 1, type=int)

    query = Usuario.query
    if search:
        query = query.filter(
            db.or_(
                Usuario.nome.contains(search),
                Usuario.email.contains(search),
                Usuario.cpf.contains(search)
            )
        )

    if escola_id:
        query = query.filter(Usuario.escola_id == escola_id)

    if perfil_id:
        query = query.filter(Usuario.perfil_id == perfil_id)

    if situacao:
        query = query.filter(Usuario.situacao == situacao)

    usuarios = query.paginate(
        page=page, per_page=10, error_out=False
    )

    escola_filtro = None
    if escola_id:
        escola_filtro = Escola.query.get(escola_id)

    perfil_filtro = None
    if perfil_id:
        perfil_filtro = Perfil.query.get(perfil_id)

    # Buscar dados para filtros
    escolas = Escola.query.all()
    perfis = Perfil.query.all()

    return render_template('usuarios/listar.html',
                         usuarios=usuarios,
                         search=search,
                         escola_filtro=escola_filtro,
                         perfil_filtro=perfil_filtro,
                         escolas=escolas,
                         perfis=perfis,
                         situacao=situacao)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
def usuarios_novo():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario_logado = Usuario.query.get(session['user_id'])
    if usuario_logado.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        cpf = request.form.get('cpf', '').strip()

        if not nome or not email:
            flash('Nome e email são obrigatórios!', 'error')
            return render_template('usuarios/cadastrar.html', escolas=Escola.query.all(), perfis=Perfil.query.all())

        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado no sistema!', 'error')
            return render_template('usuarios/cadastrar.html', escolas=Escola.query.all(), perfis=Perfil.query.all())

        usuario = Usuario(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=request.form.get('telefone', '').strip(),
            escola_id=request.form.get('escola_id'),
            perfil_id=request.form.get('perfil_id'),
            situacao=request.form.get('situacao', 'ativo'),
            data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date() if request.form.get('data_nascimento') else None
        )

        # Senha padrão
        senha_padrao = request.form.get('senha', '123456')
        usuario.set_password(senha_padrao)

        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect('/usuarios/')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')

    escolas = Escola.query.all()
    perfis = Perfil.query.all()
    return render_template('usuarios/cadastrar.html', escolas=escolas, perfis=perfis)

@app.route('/usuarios/ver/<int:id>')
def usuarios_ver(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario = Usuario.query.get_or_404(id)
    return render_template('usuarios/ver.html', usuario=usuario)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def usuarios_editar(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario_logado = Usuario.query.get(session['user_id'])
    if usuario_logado.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nome = request.form.get('nome', '').strip()
        usuario.email = request.form.get('email', '').strip()
        usuario.cpf = request.form.get('cpf', '').strip()
        usuario.telefone = request.form.get('telefone', '').strip()
        usuario.escola_id = request.form.get('escola_id')
        usuario.perfil_id = request.form.get('perfil_id')
        usuario.situacao = request.form.get('situacao', 'ativo')

        if request.form.get('data_nascimento'):
            usuario.data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date()

        # Alterar senha se fornecida
        nova_senha = request.form.get('nova_senha', '').strip()
        if nova_senha:
            usuario.set_password(nova_senha)

        if not usuario.nome or not usuario.email:
            flash('Nome e email são obrigatórios!', 'error')
            return render_template('usuarios/editar.html', usuario=usuario, escolas=Escola.query.all(), perfis=Perfil.query.all())

        try:
            db.session.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect('/usuarios/')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'error')

    escolas = Escola.query.all()
    perfis = Perfil.query.all()
    return render_template('usuarios/editar.html', usuario=usuario, escolas=escolas, perfis=perfis)

@app.route('/usuarios/excluir/<int:id>', methods=['POST'])
def usuarios_excluir(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    usuario_logado = Usuario.query.get(session['user_id'])
    if usuario_logado.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.get_or_404(id)

    # Não permitir excluir o próprio usuário
    if usuario.id == usuario_logado.id:
        flash('Não é possível excluir seu próprio usuário!', 'error')
        return redirect('/usuarios/')

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário "{usuario.nome}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'error')

    return redirect('/usuarios/')

@app.route('/dossies/')
def dossies_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Busca com paginação
    search = request.args.get('search', '')
    ano = request.args.get('ano', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    # Criar modelo Dossie básico para demonstração
    class DossieDemo:
        def __init__(self, id, numero_dossie, nome, cpf, ano, local, pasta, status, data_cadastro, tipo_documento='fisico', data_nascimento=None):
            self.id = id
            self.numero_dossie = numero_dossie
            self.nome = nome
            self.cpf = cpf
            self.ano = ano
            self.local = local
            self.pasta = pasta
            self.status = status
            self.data_cadastro = data_cadastro
            self.tipo_documento = tipo_documento
            self.data_nascimento = data_nascimento

    # Dados de demonstração
    dossies_demo = [
        DossieDemo(1, '20240001', 'João Silva Santos', '123.456.789-00', 2024, 'Arquivo A', 'Pasta 001', 'ativo', datetime.now()),
        DossieDemo(2, '20240002', 'Maria Oliveira', '987.654.321-00', 2024, 'Arquivo B', 'Pasta 002', 'emprestado', datetime.now()),
        DossieDemo(3, '20230001', 'Pedro Costa', '456.789.123-00', 2023, 'Arquivo A', 'Pasta 003', 'arquivado', datetime.now()),
    ]

    # Simular paginação
    class PaginacaoDemo:
        def __init__(self, items, total=3, pages=1, page=1):
            self.items = items
            self.total = total
            self.pages = pages
            self.page = page
            self.has_prev = False
            self.has_next = False
            self.prev_num = None
            self.next_num = None

        def iter_pages(self):
            return [1]

    dossies = PaginacaoDemo(dossies_demo)
    anos_disponiveis = [2024, 2023, 2022]

    return render_template('dossies/listar.html',
                         dossies=dossies,
                         search=search,
                         ano=ano,
                         status=status,
                         anos_disponiveis=anos_disponiveis)

@app.route('/movimentacoes/')
def movimentacoes_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('aplicacoes/movimentacoes.html')

@app.route('/solicitantes/')
def solicitantes_listar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('aplicacoes/solicitantes.html')

@app.route('/relatorios/')
def relatorios_index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('aplicacoes/relatorios.html')

@app.route('/logs/auditoria')
def logs_auditoria():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('aplicacoes/logs.html')

def criar_dados_iniciais():
    """Criar dados iniciais do sistema"""
    
    # Criar perfis padrão
    perfis_padrao = [
        {'nome': 'Administrador Geral', 'descricao': 'Controla todo o sistema', 'nivel_acesso': 5},
        {'nome': 'Administrador da Escola', 'descricao': 'Gerencia escola específica', 'nivel_acesso': 4},
        {'nome': 'Usuário Operacional', 'descricao': 'Uso operacional básico', 'nivel_acesso': 2}
    ]
    
    for perfil_data in perfis_padrao:
        if not Perfil.query.filter_by(nome=perfil_data['nome']).first():
            perfil = Perfil(**perfil_data)
            db.session.add(perfil)
    
    # Criar cidade padrão
    if not Cidade.query.first():
        cidade = Cidade(nome='São Paulo', uf='SP')
        db.session.add(cidade)
        db.session.commit()

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
    
    # Criar usuário admin padrão
    perfil_admin = Perfil.query.filter_by(nome='Administrador Geral').first()
    escola_padrao = Escola.query.first()
    
    if not Usuario.query.filter_by(email='admin@sistema.com').first():
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
    with app.app_context():
        db.create_all()
        criar_dados_iniciais()
        
        print("🚀 Sistema Modular Simples Iniciado")
        print("🌐 Acesse: http://localhost:5000")
        print("👤 Login: admin@sistema.com / admin123")
        print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
