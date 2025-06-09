"""
Modelos do Sistema de Controle de Dossiê Escolar
Conforme especificação no CLAUDE.md
"""

from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

def create_complete_models(db):
    """Função para criar todos os modelos conforme especificação"""
    
    class Escola(db.Model):
        __tablename__ = 'escolas'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(200), nullable=False)
        endereco = db.Column(db.Text)
        cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'))
        uf = db.Column(db.String(2))
        cnpj = db.Column(db.String(18), unique=True)
        inep = db.Column(db.String(20), unique=True)
        email = db.Column(db.String(120))
        diretor = db.Column(db.String(100))
        situacao = db.Column(db.String(20), default='ativa')  # ativa, inativa
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        data_saida = db.Column(db.DateTime)
        
        # Relacionamentos
        usuarios = db.relationship('Usuario', backref='escola', lazy=True)
        dossies = db.relationship('Dossie', backref='escola', lazy=True)
        movimentacoes = db.relationship('Movimentacao', backref='escola', lazy=True)
        
        def __repr__(self):
            return f'<Escola {self.nome}>'

    class Cidade(db.Model):
        __tablename__ = 'cidades'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        uf = db.Column(db.String(2), nullable=False)
        pais = db.Column(db.String(50), default='Brasil')
        
        # Relacionamentos
        escolas = db.relationship('Escola', backref='cidade', lazy=True)
        solicitantes = db.relationship('Solicitante', backref='cidade', lazy=True)
        
        def __repr__(self):
            return f'<Cidade {self.nome}/{self.uf}>'

    class Perfil(db.Model):
        __tablename__ = 'perfis'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(50), nullable=False, unique=True)
        descricao = db.Column(db.Text)
        nivel_acesso = db.Column(db.Integer, default=1)  # 1=baixo, 5=alto
        
        # Relacionamentos
        usuarios = db.relationship('Usuario', backref='perfil_obj', lazy=True)
        
        def __repr__(self):
            return f'<Perfil {self.nome}>'

    class Usuario(db.Model):
        __tablename__ = 'usuarios'
        
        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        cpf = db.Column(db.String(14), unique=True)
        email = db.Column(db.String(120), unique=True, nullable=False)
        telefone = db.Column(db.String(20))
        data_nascimento = db.Column(db.Date)
        data_registro = db.Column(db.DateTime, default=datetime.now)
        perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        ultimo_acesso = db.Column(db.DateTime)
        status = db.Column(db.String(20), default='ativo')  # ativo, inativo, bloqueado
        senha_hash = db.Column(db.String(255), nullable=False)
        tentativas_login = db.Column(db.Integer, default=0)
        bloqueado_ate = db.Column(db.DateTime)
        token_recuperacao = db.Column(db.String(100))
        token_expiracao = db.Column(db.DateTime)
        
        # Relacionamentos
        dossies_criados = db.relationship('Dossie', foreign_keys='Dossie.usuario_cadastro_id', backref='usuario_cadastro', lazy=True)
        movimentacoes = db.relationship('Movimentacao', backref='responsavel', lazy=True)
        logs = db.relationship('LogAuditoria', backref='usuario', lazy=True)
        permissoes = db.relationship('PermissaoCustomizada', backref='usuario', lazy=True)
        
        def set_password(self, password):
            self.senha_hash = generate_password_hash(password)
        
        def check_password(self, password):
            return check_password_hash(self.senha_hash, password)
        
        def gerar_token_recuperacao(self):
            self.token_recuperacao = str(uuid.uuid4())
            self.token_expiracao = datetime.now() + timedelta(hours=24)
        
        def __repr__(self):
            return f'<Usuario {self.nome}>'

    class Dossie(db.Model):
        __tablename__ = 'dossies'
        
        id = db.Column(db.Integer, primary_key=True)
        local = db.Column(db.String(100))
        pasta = db.Column(db.String(50))
        numero_dossie = db.Column(db.String(50), nullable=False)
        ano = db.Column(db.Integer, nullable=False)
        nome = db.Column(db.String(100), nullable=False)
        cpf = db.Column(db.String(14))
        nome_pai = db.Column(db.String(100))
        nome_mae = db.Column(db.String(100))
        status = db.Column(db.String(20), default='ativo')  # ativo, arquivado, emprestado
        tipo_documento = db.Column(db.String(50))
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        data_arquivamento = db.Column(db.DateTime)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        observacoes = db.Column(db.Text)
        foto_path = db.Column(db.String(255))
        usuario_cadastro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        
        # Relacionamentos
        movimentacoes = db.relationship('Movimentacao', backref='dossie', lazy=True)
        documentos = db.relationship('DocumentoDossie', backref='dossie', lazy=True)
        
        def __repr__(self):
            return f'<Dossie {self.numero_dossie}/{self.ano} - {self.nome}>'

    class Solicitante(db.Model):
        __tablename__ = 'solicitantes'

        id = db.Column(db.Integer, primary_key=True)
        nome = db.Column(db.String(100), nullable=False)
        endereco = db.Column(db.Text)
        celular = db.Column(db.String(20))
        cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'))
        cpf = db.Column(db.String(14), unique=True)
        email = db.Column(db.String(120))
        parentesco = db.Column(db.String(50))
        data_nascimento = db.Column(db.Date)
        tipo_solicitacao = db.Column(db.String(50))
        status = db.Column(db.String(20), default='ativo')
        data_cadastro = db.Column(db.DateTime, default=datetime.now)
        
        # Relacionamentos
        movimentacoes = db.relationship('Movimentacao', backref='solicitante', lazy=True)
        
        def __repr__(self):
            return f'<Solicitante {self.nome}>'

    class Movimentacao(db.Model):
        __tablename__ = 'movimentacoes'
        
        id = db.Column(db.Integer, primary_key=True)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        solicitante_id = db.Column(db.Integer, db.ForeignKey('solicitantes.id'), nullable=False)
        descricao = db.Column(db.Text, nullable=False)
        data_solicitacao = db.Column(db.DateTime, default=datetime.now)
        data_devolucao = db.Column(db.DateTime)
        status = db.Column(db.String(20), default='pendente')  # pendente, aprovada, devolvida, cancelada
        dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
        responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        tipo_documentacao = db.Column(db.String(50))
        observacao = db.Column(db.Text)
        
        def __repr__(self):
            return f'<Movimentacao {self.id} - {self.status}>'

    class DocumentoDossie(db.Model):
        __tablename__ = 'documentos_dossie'
        
        id = db.Column(db.Integer, primary_key=True)
        dossie_id = db.Column(db.Integer, db.ForeignKey('dossies.id'), nullable=False)
        nome = db.Column(db.String(200), nullable=False)
        nome_arquivo = db.Column(db.String(255), nullable=False)
        tipo_arquivo = db.Column(db.String(50))
        tamanho = db.Column(db.Integer)
        data_upload = db.Column(db.DateTime, default=datetime.now)
        usuario_upload_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        
        def __repr__(self):
            return f'<DocumentoDossie {self.nome}>'

    class LogAuditoria(db.Model):
        __tablename__ = 'logs_auditoria'
        
        id = db.Column(db.Integer, primary_key=True)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        acao = db.Column(db.String(100), nullable=False)
        data_hora = db.Column(db.DateTime, default=datetime.now)
        item_alterado = db.Column(db.String(100))
        ip_address = db.Column(db.String(45))
        navegador = db.Column(db.String(200))
        detalhes = db.Column(db.Text)
        
        def __repr__(self):
            return f'<LogAuditoria {self.acao} - {self.data_hora}>'

    class LogSistema(db.Model):
        __tablename__ = 'logs_sistema'
        
        id = db.Column(db.Integer, primary_key=True)
        mensagem_erro = db.Column(db.Text, nullable=False)
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
        nivel_erro = db.Column(db.String(20), default='INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        data_hora = db.Column(db.DateTime, default=datetime.now)
        
        def __repr__(self):
            return f'<LogSistema {self.nivel_erro} - {self.data_hora}>'

    class PermissaoCustomizada(db.Model):
        __tablename__ = 'permissoes_customizadas'
        
        id = db.Column(db.Integer, primary_key=True)
        recurso = db.Column(db.String(100), nullable=False)
        permissao = db.Column(db.String(50), nullable=False)  # create, read, update, delete
        usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        concedida = db.Column(db.Boolean, default=True)
        data_concessao = db.Column(db.DateTime, default=datetime.now)
        
        def __repr__(self):
            return f'<PermissaoCustomizada {self.recurso}:{self.permissao}>'

    class ConfiguracaoEscola(db.Model):
        __tablename__ = 'configuracoes_escola'
        
        id = db.Column(db.Integer, primary_key=True)
        escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
        chave = db.Column(db.String(100), nullable=False)
        valor = db.Column(db.Text)
        tipo = db.Column(db.String(20), default='string')  # string, boolean, integer, json
        descricao = db.Column(db.Text)
        
        def __repr__(self):
            return f'<ConfiguracaoEscola {self.chave}>'

    return (Escola, Cidade, Perfil, Usuario, Dossie, Solicitante, 
            Movimentacao, DocumentoDossie, LogAuditoria, LogSistema, 
            PermissaoCustomizada, ConfiguracaoEscola)
