from datetime import datetime, date
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash

def create_models(db):
    """Função para criar os modelos com a instância do SQLAlchemy"""
    
    class Usuario(db.Model):
        __tablename__ = 'usuarios'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        senha_hash = db.Column(db.String(255), nullable=False)
        tipo = db.Column(db.String(20), nullable=False, default='usuario')  # admin, professor, secretaria
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        ultimo_acesso = db.Column(db.DateTime)
        foto_url = db.Column(db.String(255))
        
        def set_senha(self, senha):
            self.senha_hash = generate_password_hash(senha)
            
        def check_senha(self, senha):
            return check_password_hash(self.senha_hash, senha)
        
        def __repr__(self):
            return f'<Usuario {self.nome}>'

    class Escola(db.Model):
        __tablename__ = 'escolas'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(200), nullable=False)
        cnpj = db.Column(db.String(18), unique=True)
        endereco = db.Column(db.Text)
        telefone = db.Column(db.String(20))
        email = db.Column(db.String(120))
        diretor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        # Relacionamentos
        diretor = db.relationship('Usuario', backref='escola_diretor')
        turmas = db.relationship('Turma', backref='escola', lazy=True)
        
        def __repr__(self):
            return f'<Escola {self.nome}>'

    class Turma(db.Model):
        __tablename__ = 'turmas'
        
        id = db.Column(db.Integer, primary_key=True)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        nome = db.Column(db.String(50), nullable=False)
        serie = db.Column(db.String(20), nullable=False)
        turno = db.Column(db.String(20), nullable=False)  # manha, tarde, noite, integral
        ano_letivo = db.Column(db.String(10), nullable=False)
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        # Relacionamentos
        alunos = db.relationship('Aluno', backref='turma', lazy=True)
        
        def __repr__(self):
            return f'<Turma {self.nome}>'

    class Aluno(db.Model):
        __tablename__ = 'alunos'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        matricula = db.Column(db.String(20), unique=True, nullable=False)
        data_nascimento = db.Column(db.Date, nullable=False)
        cpf = db.Column(db.String(14), unique=True)
        rg = db.Column(db.String(20))
        nome_mae = db.Column(db.String(100))
        nome_pai = db.Column(db.String(100))
        endereco = db.Column(db.Text)
        telefone = db.Column(db.String(20))
        email = db.Column(db.String(120))
        turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'))
        data_matricula = db.Column(db.Date, nullable=False)
        situacao = db.Column(db.String(20), default='ativo')  # ativo, inativo, transferido, formado
        observacoes = db.Column(db.Text)
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        # Relacionamentos
        dossies = db.relationship('Dossie', backref='aluno', lazy=True, cascade='all, delete-orphan')
        
        def __repr__(self):
            return f'<Aluno {self.nome}>'
        
        @property
        def idade(self):
            today = date.today()
            return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

    class Dossie(db.Model):
        __tablename__ = 'dossies'
        
        id = db.Column(db.Integer, primary_key=True)
        aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        titulo = db.Column(db.String(200), nullable=False)
        descricao = db.Column(db.Text)
        tipo = db.Column(db.String(50), nullable=False)  # disciplinar, academico, medico, social
        status = db.Column(db.String(20), default='aberto')  # aberto, em_andamento, resolvido, arquivado
        prioridade = db.Column(db.String(20), default='media')  # baixa, media, alta, urgente
        data_criacao = db.Column(db.DateTime, default=datetime.now)
        data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
        usuario_criacao_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        
        # Relacionamentos
        escola = db.relationship('Escola', backref='dossies')
        documentos = db.relationship('Documento', backref='dossie', lazy=True, cascade='all, delete-orphan')
        observacoes = db.relationship('Observacao', backref='dossie', lazy=True, cascade='all, delete-orphan')
        movimentacoes = db.relationship('Movimentacao', backref='dossie', lazy=True, cascade='all, delete-orphan')
        usuario_criacao = db.relationship('Usuario', backref='dossies_criados')
        
        def __repr__(self):
            return f'<Dossie {self.titulo}>'

    class Documento(db.Model):
        __tablename__ = 'documentos'
        
        id = db.Column(db.Integer, primary_key=True)
        dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
        nome = db.Column(db.String(200), nullable=False)
        nome_arquivo = db.Column(db.String(255), nullable=False)
        tipo_arquivo = db.Column(db.String(50))
        tamanho = db.Column(db.Integer)
        descricao = db.Column(db.Text)
        data_upload = db.Column(db.DateTime, default=datetime.now)
        usuario_upload_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        versao = db.Column(db.Integer, default=1)
        hash_arquivo = db.Column(db.String(64))  # Para verificação de integridade
        
        # Relacionamentos
        usuario_upload = db.relationship('Usuario', backref='documentos_enviados')
        
        def __repr__(self):
            return f'<Documento {self.nome}>'

    class Observacao(db.Model):
        __tablename__ = 'observacoes'
        
        id = db.Column(db.Integer, primary_key=True)
        dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
        conteudo = db.Column(db.Text, nullable=False)
        tipo = db.Column(db.String(50), default='geral')  # geral, importante, privada
        data_criacao = db.Column(db.DateTime, default=datetime.now)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        
        # Relacionamentos
        usuario = db.relationship('Usuario', backref='observacoes')
        
        def __repr__(self):
            return f'<Observacao {self.id}>'

    class Movimentacao(db.Model):
        __tablename__ = 'movimentacoes'
        
        id = db.Column(db.Integer, primary_key=True)
        dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
        tipo = db.Column(db.String(50), nullable=False)  # emprestimo, devolucao, consulta
        data_movimentacao = db.Column(db.DateTime, default=datetime.now)
        data_prevista_devolucao = db.Column(db.DateTime)
        data_devolucao = db.Column(db.DateTime)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        solicitante_id = db.Column(db.Integer, db.ForeignKey('solicitantes.id'))
        status = db.Column(db.String(20), default='pendente')  # pendente, concluida, atrasada
        observacoes = db.Column(db.Text)
        
        # Relacionamentos
        usuario = db.relationship('Usuario', backref='movimentacoes')
        solicitante = db.relationship('Solicitante', backref='movimentacoes')
        
        def __repr__(self):
            return f'<Movimentacao {self.tipo}>'

    class Solicitante(db.Model):
        __tablename__ = 'solicitantes'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        cpf = db.Column(db.String(14), unique=True)
        rg = db.Column(db.String(20))
        endereco = db.Column(db.Text)
        telefone = db.Column(db.String(20))
        email = db.Column(db.String(120))
        tipo = db.Column(db.String(50), nullable=False)  # professor, coordenador, diretor, outro
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        def __repr__(self):
            return f'<Solicitante {self.nome}>'

    class LogAtividade(db.Model):
        __tablename__ = 'log_atividades'
        
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        acao = db.Column(db.String(100), nullable=False)
        tabela = db.Column(db.String(50))
        registro_id = db.Column(db.Integer)
        detalhes = db.Column(db.Text)
        ip_address = db.Column(db.String(45))
        data_acao = db.Column(db.DateTime, default=datetime.now)
        
        # Relacionamentos
        usuario = db.relationship('Usuario', backref='atividades')
        
        def __repr__(self):
            return f'<LogAtividade {self.acao}>'

    # Eventos para logging automático
    @event.listens_for(Usuario, 'after_insert')
    @event.listens_for(Usuario, 'after_update')
    @event.listens_for(Usuario, 'after_delete')
    def log_usuario_event(mapper, connection, target):
        if hasattr(target, 'id'):
            action = 'insert' if mapper.class_ == Usuario else 'update' if target.id else 'delete'
            db.session.add(LogAtividade(
                usuario_id=target.id,
                acao=f'{action}_usuario',
                tabela='usuarios',
                registro_id=target.id,
                detalhes=f'Usuário {target.nome}'
            ))

    @event.listens_for(Dossie, 'after_insert')
    @event.listens_for(Dossie, 'after_update')
    @event.listens_for(Dossie, 'after_delete')
    def log_dossie_event(mapper, connection, target):
        if hasattr(target, 'id'):
            action = 'insert' if mapper.class_ == Dossie else 'update' if target.id else 'delete'
            db.session.add(LogAtividade(
                usuario_id=target.usuario_criacao_id,
                acao=f'{action}_dossie',
                tabela='dossies',
                registro_id=target.id,
                detalhes=f'Dossiê {target.titulo}'
            ))

    @event.listens_for(Movimentacao, 'after_insert')
    @event.listens_for(Movimentacao, 'after_update')
    @event.listens_for(Movimentacao, 'after_delete')
    def log_movimentacao_event(mapper, connection, target):
        if hasattr(target, 'id'):
            action = 'insert' if mapper.class_ == Movimentacao else 'update' if target.id else 'delete'
            db.session.add(LogAtividade(
                usuario_id=target.usuario_id,
                acao=f'{action}_movimentacao',
                tabela='movimentacoes',
                registro_id=target.id,
                detalhes=f'Movimentação {target.tipo}'
            ))
    
    return Usuario, Escola, Turma, Aluno, Dossie, Documento, Observacao, Movimentacao, Solicitante, LogAtividade
