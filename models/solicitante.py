# models/solicitante.py
from . import db
from datetime import datetime

class Solicitante(db.Model):
    """
    Entidade: Solicitante
    Campos: Nome, endereço, celular, cidade, CPF, email, parentesco, data de nascimento, tipo de solicitação, status
    """
    __tablename__ = 'solicitantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)
    celular = db.Column(db.String(20))
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id_cidade'))
    cpf = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(120))
    parentesco = db.Column(db.String(50))
    data_nascimento = db.Column(db.Date)
    tipo_solicitacao = db.Column(db.String(50))
    status = db.Column(db.String(20), default='ativo')
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    observacoes = db.Column(db.Text)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)  # FK - Escola vinculada

    # Relacionamentos
    cidade = db.relationship('Cidade', backref='solicitantes')
    escola = db.relationship('Escola', backref='solicitantes')
    
    def __repr__(self):
        return f'<Solicitante {self.nome}>'

    @property
    def movimentacoes(self):
        """Retorna as movimentações do solicitante"""
        from models import Movimentacao
        return Movimentacao.query.filter_by(solicitante_id=self.id).order_by(Movimentacao.data_movimentacao.desc()).all()
    
    def validar_cpf(self):
        """Validar CPF do solicitante"""
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'celular': self.celular,
            'cidade_id': self.cidade_id,
            'cidade_nome': self.cidade.nome if self.cidade else None,
            'cpf': self.cpf,
            'email': self.email,
            'parentesco': self.parentesco,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'tipo_solicitacao': self.tipo_solicitacao,
            'status': self.status,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'observacoes': self.observacoes,
            'total_movimentacoes': len(self.movimentacoes)
        }
