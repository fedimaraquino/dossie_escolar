"""
Aplicação ESCOLAS - Modelos
Conforme especificação CLAUDE.md - Item 2
"""

from models import db
from datetime import datetime

class Escola(db.Model):
    """
    Entidade: Escola
    Campos: Nome, endereço, cidade, UF, CNPJ, INEP, email, diretor, situação, data de cadastro, data de saída
    """
    __tablename__ = 'escolas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.Text)
    cidade_id = db.Column(db.Integer, db.ForeignKey('cidades.id'))
    uf = db.Column(db.String(2), nullable=False)
    cnpj = db.Column(db.String(18), unique=True)
    inep = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    diretor = db.Column(db.String(100))
    vice_diretor = db.Column(db.String(100))
    situacao = db.Column(db.String(20), default='ativa')  # ativa, inativa, suspensa
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    data_saida = db.Column(db.DateTime)
    motivo_saida = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    
    # Campos de auditoria
    usuario_cadastro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_atualizacao = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', foreign_keys='Usuario.escola_id', backref='escola', lazy=True)
    dossies = db.relationship('Dossie', backref='escola', lazy=True)
    movimentacoes = db.relationship('Movimentacao', backref='escola', lazy=True)
    configuracoes = db.relationship('ConfiguracaoEscola', backref='escola', lazy=True)
    
    def __repr__(self):
        return f'<Escola {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'cidade_id': self.cidade_id,
            'cidade_nome': self.cidade.nome if self.cidade else None,
            'uf': self.uf,
            'cnpj': self.cnpj,
            'inep': self.inep,
            'email': self.email,
            'telefone': self.telefone,
            'diretor': self.diretor,
            'vice_diretor': self.vice_diretor,
            'situacao': self.situacao,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_saida': self.data_saida.isoformat() if self.data_saida else None,
            'observacoes': self.observacoes
        }
    
    def ativar(self):
        """Ativar escola"""
        self.situacao = 'ativa'
        self.data_saida = None
        self.motivo_saida = None
        db.session.commit()
    
    def inativar(self, motivo=None):
        """Inativar escola"""
        self.situacao = 'inativa'
        self.data_saida = datetime.now()
        self.motivo_saida = motivo
        db.session.commit()
    
    def suspender(self, motivo=None):
        """Suspender escola temporariamente"""
        self.situacao = 'suspensa'
        self.motivo_saida = motivo
        db.session.commit()
    
    @property
    def total_usuarios(self):
        """Total de usuários da escola"""
        return len([u for u in self.usuarios if u.status == 'ativo'])
    
    @property
    def total_dossies(self):
        """Total de dossiês da escola"""
        return len([d for d in self.dossies if d.status == 'ativo'])
    
    @property
    def total_movimentacoes(self):
        """Total de movimentações da escola"""
        return len(self.movimentacoes)
    
    @property
    def movimentacoes_pendentes(self):
        """Movimentações pendentes da escola"""
        return len([m for m in self.movimentacoes if m.status == 'pendente'])
    
    def obter_configuracao(self, chave, valor_padrao=None):
        """Obter configuração específica da escola"""
        from apps.core.utils import obter_configuracao
        return obter_configuracao(self.id, chave, valor_padrao)
    
    def atualizar_configuracao(self, chave, valor, tipo='string', descricao=None):
        """Atualizar configuração da escola"""
        from apps.core.utils import atualizar_configuracao
        return atualizar_configuracao(self.id, chave, valor, tipo, descricao)
    
    def validar_cnpj(self):
        """Validar CNPJ da escola"""
        if not self.cnpj:
            return True  # CNPJ é opcional
        
        # Remover formatação
        cnpj = ''.join(filter(str.isdigit, self.cnpj))
        
        # Verificar se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verificar se não são todos iguais
        if cnpj == cnpj[0] * 14:
            return False
        
        # Algoritmo de validação do CNPJ
        def calcular_digito(cnpj_parcial, pesos):
            soma = sum(int(cnpj_parcial[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito verificador
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito1 = calcular_digito(cnpj[:12], pesos1)
        
        # Segundo dígito verificador
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = calcular_digito(cnpj[:13], pesos2)
        
        return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)
    
    def validar_inep(self):
        """Validar código INEP da escola"""
        if not self.inep:
            return True  # INEP é opcional
        
        # Remover formatação
        inep = ''.join(filter(str.isdigit, self.inep))
        
        # Verificar se tem 8 dígitos
        return len(inep) == 8
    
    def gerar_relatorio_resumo(self):
        """Gerar relatório resumo da escola"""
        return {
            'escola': self.to_dict(),
            'estatisticas': {
                'total_usuarios': self.total_usuarios,
                'total_dossies': self.total_dossies,
                'total_movimentacoes': self.total_movimentacoes,
                'movimentacoes_pendentes': self.movimentacoes_pendentes
            },
            'usuarios_por_perfil': self._obter_usuarios_por_perfil(),
            'dossies_por_status': self._obter_dossies_por_status(),
            'movimentacoes_por_status': self._obter_movimentacoes_por_status()
        }
    
    def _obter_usuarios_por_perfil(self):
        """Obter contagem de usuários por perfil"""
        from collections import Counter
        perfis = [u.perfil_obj.nome for u in self.usuarios if u.status == 'ativo']
        return dict(Counter(perfis))
    
    def _obter_dossies_por_status(self):
        """Obter contagem de dossiês por status"""
        from collections import Counter
        status = [d.status for d in self.dossies]
        return dict(Counter(status))
    
    def _obter_movimentacoes_por_status(self):
        """Obter contagem de movimentações por status"""
        from collections import Counter
        status = [m.status for m in self.movimentacoes]
        return dict(Counter(status))
