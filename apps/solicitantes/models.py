"""
Aplicação SOLICITANTES - Modelos
Conforme especificação CLAUDE.md - Item 6
"""

from main import db
from datetime import datetime

class Solicitante(db.Model):
    """
    Entidade: Solicitante
    Campos conforme especificação: id_solicitante, nome, endereco, celular, cidade, data_cadastro, cpf, email, status, parentesco, data_nascimento, tipo_solicitacao
    """
    __tablename__ = 'solicitantes'

    id_solicitante = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)
    celular = db.Column(db.String(20))
    cidade = db.Column(db.String(100))  # Campo cidade como string conforme especificação
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    cpf = db.Column(db.String(14), unique=True)
    email = db.Column(db.String(120))
    status = db.Column(db.String(20), default='ativo')
    parentesco = db.Column(db.String(50))
    data_nascimento = db.Column(db.Date)
    tipo_solicitacao = db.Column(db.String(50))

    # Relacionamentos
    movimentacoes = db.relationship('Movimentacao', backref='solicitante', lazy=True)
    
    def __repr__(self):
        return f'<Solicitante {self.nome}>'

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
            'id_solicitante': self.id_solicitante,
            'nome': self.nome,
            'endereco': self.endereco,
            'celular': self.celular,
            'cidade': self.cidade,
            'cpf': self.cpf,
            'email': self.email,
            'parentesco': self.parentesco,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'tipo_solicitacao': self.tipo_solicitacao,
            'status': self.status,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'total_movimentacoes': len(self.movimentacoes)
        }
