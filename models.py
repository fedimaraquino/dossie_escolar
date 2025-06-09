from datetime import datetime, date

def create_models(db):
    """Função para criar os modelos com a instância do SQLAlchemy"""
    
    class Usuario(db.Model):
        __tablename__ = 'usuarios'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        senha = db.Column(db.String(255), nullable=False)
        tipo = db.Column(db.String(20), nullable=False, default='usuario')  # admin, professor, secretaria
        ativo = db.Column(db.Boolean, default=True)
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        def __repr__(self):
            return f'<Usuario {self.nome}>'

    class Aluno(db.Model):
        __tablename__ = 'alunos'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        matricula = db.Column(db.String(20), unique=True, nullable=False)
        data_nascimento = db.Column(db.Date, nullable=False)
        cpf = db.Column(db.String(14), unique=True)
        rg = db.Column(db.String(20))
        endereco = db.Column(db.Text)
        telefone = db.Column(db.String(20))
        email = db.Column(db.String(120))
        nome_responsavel = db.Column(db.String(100))
        telefone_responsavel = db.Column(db.String(20))
        turma = db.Column(db.String(20))
        ano_letivo = db.Column(db.String(10))
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
        titulo = db.Column(db.String(200), nullable=False)
        descricao = db.Column(db.Text)
        tipo = db.Column(db.String(50), nullable=False)  # disciplinar, academico, medico, social
        status = db.Column(db.String(20), default='aberto')  # aberto, em_andamento, resolvido, arquivado
        prioridade = db.Column(db.String(20), default='media')  # baixa, media, alta, urgente
        data_criacao = db.Column(db.DateTime, default=datetime.now)
        data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
        usuario_criacao_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        
        # Relacionamentos
        documentos = db.relationship('Documento', backref='dossie', lazy=True, cascade='all, delete-orphan')
        observacoes = db.relationship('Observacao', backref='dossie', lazy=True, cascade='all, delete-orphan')
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
    
    return Usuario, Aluno, Dossie, Documento, Observacao, LogAtividade
