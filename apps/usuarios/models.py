"""
Aplicação USUÁRIOS - Modelos
Conforme especificação CLAUDE.md - Item 3
"""

from models import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    """
    Entidade: Usuário
    Campos: Nome, CPF, email, telefone, data de nascimento, data de registro, perfil, escola, último acesso, status
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    endereco = db.Column(db.Text)
    cargo = db.Column(db.String(100))
    
    # Dados de acesso
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    
    # Controle de acesso
    status = db.Column(db.String(20), default='ativo')  # ativo, inativo, bloqueado, suspenso
    ultimo_acesso = db.Column(db.DateTime)
    tentativas_login = db.Column(db.Integer, default=0)
    bloqueado_ate = db.Column(db.DateTime)
    motivo_bloqueio = db.Column(db.Text)
    
    # Auditoria
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    usuario_cadastro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Configurações pessoais
    receber_notificacoes = db.Column(db.Boolean, default=True)
    tema_interface = db.Column(db.String(20), default='claro')  # claro, escuro
    idioma = db.Column(db.String(5), default='pt-BR')
    
    # Relacionamentos
    dossies_criados = db.relationship('Dossie', foreign_keys='Dossie.usuario_cadastro_id', backref='usuario_cadastro', lazy=True)
    movimentacoes = db.relationship('Movimentacao', foreign_keys='Movimentacao.responsavel_id', backref='responsavel', lazy=True)
    logs_auditoria = db.relationship('LogAuditoria', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
    def set_password(self, password):
        """Definir senha do usuário"""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar senha do usuário"""
        return check_password_hash(self.senha_hash, password)
    
    def to_dict(self, incluir_sensiveis=False):
        """Converter para dicionário"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cargo': self.cargo,
            'perfil_id': self.perfil_id,
            'perfil_nome': self.perfil_obj.nome if self.perfil_obj else None,
            'escola_id': self.escola_id,
            'escola_nome': self.escola.nome if self.escola else None,
            'status': self.status,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'receber_notificacoes': self.receber_notificacoes,
            'tema_interface': self.tema_interface,
            'idioma': self.idioma
        }
        
        if incluir_sensiveis:
            data.update({
                'cpf': self.cpf,
                'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
                'endereco': self.endereco,
                'tentativas_login': self.tentativas_login,
                'bloqueado_ate': self.bloqueado_ate.isoformat() if self.bloqueado_ate else None,
                'motivo_bloqueio': self.motivo_bloqueio
            })
        
        return data
    
    def is_ativo(self):
        """Verificar se usuário está ativo"""
        return self.status == 'ativo'
    
    def is_bloqueado(self):
        """Verificar se usuário está bloqueado"""
        if self.status == 'bloqueado':
            return True
        
        if self.bloqueado_ate and self.bloqueado_ate > datetime.now():
            return True
        
        return False
    
    def bloquear(self, motivo=None, tempo_minutos=30):
        """Bloquear usuário temporariamente"""
        self.status = 'bloqueado'
        self.bloqueado_ate = datetime.now() + timedelta(minutes=tempo_minutos)
        self.motivo_bloqueio = motivo
        self.tentativas_login = 0
        db.session.commit()
    
    def desbloquear(self):
        """Desbloquear usuário"""
        if self.status == 'bloqueado':
            self.status = 'ativo'
        self.bloqueado_ate = None
        self.motivo_bloqueio = None
        self.tentativas_login = 0
        db.session.commit()
    
    def ativar(self):
        """Ativar usuário"""
        self.status = 'ativo'
        self.bloqueado_ate = None
        self.motivo_bloqueio = None
        db.session.commit()
    
    def inativar(self):
        """Inativar usuário"""
        self.status = 'inativo'
        db.session.commit()
    
    def suspender(self, motivo=None):
        """Suspender usuário"""
        self.status = 'suspenso'
        self.motivo_bloqueio = motivo
        db.session.commit()
    
    def atualizar_ultimo_acesso(self):
        """Atualizar timestamp do último acesso"""
        self.ultimo_acesso = datetime.now()
        db.session.commit()
    
    def resetar_tentativas_login(self):
        """Resetar contador de tentativas de login"""
        self.tentativas_login = 0
        db.session.commit()
    
    def incrementar_tentativas_login(self):
        """Incrementar contador de tentativas de login"""
        self.tentativas_login += 1
        db.session.commit()
    
    def tem_permissao(self, recurso, acao):
        """Verificar se usuário tem permissão para uma ação"""
        from apps.core.utils import verificar_permissao
        return verificar_permissao(self.id, recurso, acao)
    
    def pode_acessar_escola(self, escola_id):
        """Verificar se usuário pode acessar dados de uma escola"""
        # Administrador Geral pode acessar qualquer escola
        if self.perfil_obj.nome == 'Administrador Geral':
            return True
        
        # Outros usuários só podem acessar sua própria escola
        return self.escola_id == escola_id
    
    def obter_estatisticas_pessoais(self):
        """Obter estatísticas pessoais do usuário"""
        stats = {
            'dossies_criados': len(self.dossies_criados),
            'movimentacoes_responsavel': len(self.movimentacoes),
            'ultimo_acesso': self.ultimo_acesso,
            'dias_desde_ultimo_acesso': (datetime.now() - self.ultimo_acesso).days if self.ultimo_acesso else None,
            'total_logins': len([log for log in self.logs_auditoria if log.acao == 'LOGIN_SUCESSO']),
            'sessoes_ativas': len([s for s in self.sessoes if s.ativa])
        }
        
        return stats
    
    def validar_cpf(self):
        """Validar CPF do usuário"""
        if not self.cpf:
            return True  # CPF é opcional
        
        # Remover formatação
        cpf = ''.join(filter(str.isdigit, self.cpf))
        
        # Verificar se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verificar se não são todos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Algoritmo de validação do CPF
        def calcular_digito(cpf_parcial):
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito verificador
        digito1 = calcular_digito(cpf[:9])
        
        # Segundo dígito verificador
        digito2 = calcular_digito(cpf[:10])
        
        return cpf[9] == str(digito1) and cpf[10] == str(digito2)
    
    def gerar_relatorio_atividades(self, data_inicio=None, data_fim=None):
        """Gerar relatório de atividades do usuário"""
        if not data_inicio:
            data_inicio = datetime.now() - timedelta(days=30)
        if not data_fim:
            data_fim = datetime.now()
        
        # Filtrar logs no período
        logs = [log for log in self.logs_auditoria 
                if data_inicio <= log.data_hora <= data_fim]
        
        # Agrupar por ação
        from collections import Counter
        acoes = Counter([log.acao for log in logs])
        
        return {
            'periodo': {
                'inicio': data_inicio.isoformat(),
                'fim': data_fim.isoformat()
            },
            'total_atividades': len(logs),
            'atividades_por_tipo': dict(acoes),
            'atividades_detalhadas': [
                {
                    'data_hora': log.data_hora.isoformat(),
                    'acao': log.acao,
                    'item_alterado': log.item_alterado,
                    'detalhes': log.detalhes
                }
                for log in sorted(logs, key=lambda x: x.data_hora, reverse=True)
            ]
        }
