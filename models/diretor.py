# models/diretor.py
from . import db
from datetime import datetime

class Diretor(db.Model):
    """
    Modelo para Diretores das escolas
    Gerencia informações dos diretores escolares
    """
    __tablename__ = 'diretores'

    id_diretor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    celular = db.Column(db.String(20))
    cidade = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    cpf = db.Column(db.String(14), unique=True)
    status = db.Column(db.String(20), default='ativo')  # ativo/inativo
    admissao = db.Column(db.Date)
    tipo_mandato = db.Column(db.String(50))  # Cargo ou mandato
    foto = db.Column(db.String(255))  # Nome do arquivo da foto

    def __repr__(self):
        return f'<Diretor {self.nome}>'

    def to_dict(self):
        return {
            'id_diretor': self.id_diretor,
            'nome': self.nome,
            'endereco': self.endereco,
            'celular': self.celular,
            'cidade': self.cidade,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'cpf': self.cpf,
            'status': self.status,
            'admissao': self.admissao.isoformat() if self.admissao else None,
            'tipo_mandato': self.tipo_mandato,
            'foto': self.foto,
            'foto_url': self.get_foto_url()
        }

    @property
    def id(self):
        """Propriedade para compatibilidade com admin"""
        return self.id_diretor

    def get_status_badge(self):
        """Retorna classe CSS para badge do status"""
        return 'success' if self.status == 'ativo' else 'secondary'

    def get_status_display(self):
        """Retorna texto formatado do status"""
        return self.status.title()

    def is_ativo(self):
        """Verifica se o diretor está ativo"""
        return self.status == 'ativo'

    def get_foto_url(self):
        """Retorna a URL da foto do diretor ou uma foto padrão"""
        if self.foto:
            return f"/static/uploads/diretores/{self.foto}"
        return "/static/img/default-director.svg"

    def has_foto(self):
        """Verifica se o diretor tem foto"""
        return bool(self.foto)

    def set_foto(self, filename):
        """Define o nome do arquivo da foto"""
        self.foto = filename

    def remove_foto(self):
        """Remove a foto do diretor"""
        import os
        if self.foto:
            foto_path = f"static/uploads/diretores/{self.foto}"
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                except:
                    pass
        self.foto = None

    def format_cpf(self):
        """Retorna CPF formatado"""
        if self.cpf and len(self.cpf) == 11:
            return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
        return self.cpf

    def format_celular(self):
        """Retorna celular formatado"""
        if self.celular:
            # Remove caracteres não numéricos
            numbers = ''.join(filter(str.isdigit, self.celular))
            if len(numbers) == 11:
                return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"
            elif len(numbers) == 10:
                return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
        return self.celular

    def get_tempo_mandato(self):
        """Calcula tempo de mandato"""
        if self.admissao:
            from datetime import date
            hoje = date.today()
            delta = hoje - self.admissao
            anos = delta.days // 365
            meses = (delta.days % 365) // 30
            
            if anos > 0:
                return f"{anos} ano(s) e {meses} mês(es)"
            else:
                return f"{meses} mês(es)"
        return "Não informado"

    @staticmethod
    def get_tipos_mandato():
        """Retorna lista de tipos de mandato disponíveis"""
        return [
            'Diretor Efetivo',
            'Diretor Substituto',
            'Diretor Interino',
            'Vice-Diretor',
            'Coordenador Pedagógico',
            'Administrador Escolar'
        ]

    @staticmethod
    def get_status_options():
        """Retorna opções de status"""
        return [
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('licenca', 'Em Licença'),
            ('aposentado', 'Aposentado')
        ]

    def validate_cpf(self):
        """Valida CPF"""
        if not self.cpf:
            return True  # CPF é opcional
        
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, self.cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não são todos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Verifica primeiro dígito
        if int(cpf[9]) != calcular_digito(cpf[:9]):
            return False
        
        # Verifica segundo dígito
        if int(cpf[10]) != calcular_digito(cpf[:10]):
            return False
        
        return True
