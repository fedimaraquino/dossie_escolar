# models/perfil.py
from . import db

class Perfil(db.Model):
    """
    Modelo para perfis de usuário do sistema
    Conforme especificação da tabela perfil
    """
    __tablename__ = 'perfil'

    id_perfil = db.Column(db.Integer, primary_key=True)
    perfil = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(200))  # Campo real para descrição

    def __repr__(self):
        return f'<Perfil {self.perfil}>'

    def to_dict(self):
        return {
            'id_perfil': self.id_perfil,
            'perfil': self.perfil,
            'descricao': self.descricao
        }

    @property
    def id(self):
        """Compatibilidade com código existente"""
        return self.id_perfil

    @property
    def nome(self):
        """Compatibilidade com código existente"""
        return self.perfil



    def get_descricao_padrao(self):
        """Retorna descrição padrão baseada no nome do perfil"""
        descricoes = {
            'Administrador Geral': 'Acesso total ao sistema',
            'Administrador da Escola': 'Administrador de uma escola específica',
            'Operador': 'Operações básicas de dossiês',
            'Consulta': 'Apenas consulta aos dossiês'
        }
        return descricoes.get(self.perfil, 'Perfil personalizado')

    def get_permissoes(self):
        """Retorna lista de permissões do perfil"""
        from .permissao import PerfilPermissao, Permissao

        permissoes = db.session.query(Permissao).join(PerfilPermissao).filter(
            PerfilPermissao.perfil_id == self.id_perfil
        ).all()

        return permissoes

    def has_permission(self, modulo, acao):
        """Verifica se o perfil tem uma permissão específica"""
        from .permissao import PerfilPermissao, Permissao

        # Admin Geral tem todas as permissões
        if self.perfil == 'Administrador Geral':
            return True

        # Verificar permissão específica
        permissao = db.session.query(Permissao).join(PerfilPermissao).filter(
            PerfilPermissao.perfil_id == self.id_perfil,
            Permissao.modulo == modulo,
            Permissao.acao == acao
        ).first()

        return permissao is not None

    def can_create(self, modulo):
        """Verifica se pode criar registros no módulo"""
        return self.has_permission(modulo, 'criar')

    def can_edit(self, modulo):
        """Verifica se pode editar registros no módulo"""
        return self.has_permission(modulo, 'editar')

    def can_delete(self, modulo):
        """Verifica se pode excluir registros no módulo"""
        return self.has_permission(modulo, 'excluir')

    def can_view(self, modulo):
        """Verifica se pode visualizar registros no módulo"""
        return self.has_permission(modulo, 'visualizar')
