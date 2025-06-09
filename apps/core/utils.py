"""
Aplicação CORE - Utilitários e Funções Auxiliares
"""

from main import db
from .models import Cidade, Perfil, ConfiguracaoEscola, CONFIGURACOES_PADRAO
from datetime import datetime

def criar_dados_iniciais():
    """Criar dados iniciais do sistema"""
    
    # Criar perfis padrão conforme CLAUDE.md
    perfis_padrao = [
        {
            'nome': 'Administrador Geral',
            'descricao': 'Controla todo o sistema - acesso a todas as escolas',
            'nivel_acesso': 5
        },
        {
            'nome': 'Administrador da Escola',
            'descricao': 'Gerencia usuários e dossiês da escola específica',
            'nivel_acesso': 4
        },
        {
            'nome': 'Usuário Operacional da Escola',
            'descricao': 'Apenas uso operacional (cadastro e busca)',
            'nivel_acesso': 2
        }
    ]
    
    for perfil_data in perfis_padrao:
        if not Perfil.query.filter_by(nome=perfil_data['nome']).first():
            perfil = Perfil(**perfil_data)
            db.session.add(perfil)
            print(f"✅ Perfil criado: {perfil_data['nome']}")
    
    # Criar cidades padrão
    cidades_padrao = [
        {'nome': 'São Paulo', 'uf': 'SP'},
        {'nome': 'Rio de Janeiro', 'uf': 'RJ'},
        {'nome': 'Belo Horizonte', 'uf': 'MG'},
        {'nome': 'Salvador', 'uf': 'BA'},
        {'nome': 'Brasília', 'uf': 'DF'},
        {'nome': 'Fortaleza', 'uf': 'CE'},
        {'nome': 'Manaus', 'uf': 'AM'},
        {'nome': 'Curitiba', 'uf': 'PR'},
        {'nome': 'Recife', 'uf': 'PE'},
        {'nome': 'Porto Alegre', 'uf': 'RS'}
    ]
    
    for cidade_data in cidades_padrao:
        if not Cidade.query.filter_by(nome=cidade_data['nome'], uf=cidade_data['uf']).first():
            cidade = Cidade(**cidade_data)
            db.session.add(cidade)
            print(f"✅ Cidade criada: {cidade_data['nome']}/{cidade_data['uf']}")
    
    db.session.commit()
    
    # Criar escola padrão se não existir
    from apps.escolas.models import Escola
    if not Escola.query.first():
        cidade_sp = Cidade.query.filter_by(nome='São Paulo', uf='SP').first()
        escola_padrao = Escola(
            nome='Escola Municipal Exemplo',
            endereco='Rua das Flores, 123 - Centro',
            cidade_id=cidade_sp.id if cidade_sp else None,
            uf='SP',
            cnpj='12.345.678/0001-90',
            inep='12345678',
            email='escola@exemplo.gov.br',
            diretor='João Silva',
            situacao='ativa'
        )
        db.session.add(escola_padrao)
        db.session.commit()
        print("✅ Escola padrão criada")
        
        # Aplicar configurações padrão para a escola
        aplicar_configuracoes_padrao(escola_padrao.id)
    
    # Criar usuário admin padrão
    from apps.usuarios.models import Usuario
    perfil_admin = Perfil.query.filter_by(nome='Administrador Geral').first()
    escola_padrao = Escola.query.first()
    
    if not Usuario.query.filter_by(email='admin@sistema.com').first():
        admin = Usuario(
            nome='Administrador do Sistema',
            cpf='000.000.000-00',
            email='admin@sistema.com',
            perfil_id=perfil_admin.id,
            escola_id=escola_padrao.id
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado: admin@sistema.com / admin123")

def aplicar_configuracoes_padrao(escola_id):
    """Aplicar configurações padrão para uma escola"""
    
    for chave, config in CONFIGURACOES_PADRAO.items():
        # Verificar se a configuração já existe
        config_existente = ConfiguracaoEscola.query.filter_by(
            escola_id=escola_id, 
            chave=chave
        ).first()
        
        if not config_existente:
            nova_config = ConfiguracaoEscola(
                escola_id=escola_id,
                chave=chave,
                valor=config['valor'],
                tipo=config['tipo'],
                descricao=config['descricao']
            )
            db.session.add(nova_config)
    
    db.session.commit()
    print(f"✅ Configurações padrão aplicadas para escola ID: {escola_id}")

def obter_configuracao(escola_id, chave, valor_padrao=None):
    """Obter valor de uma configuração específica da escola"""
    
    config = ConfiguracaoEscola.query.filter_by(
        escola_id=escola_id,
        chave=chave,
        ativo=True
    ).first()
    
    if config:
        return config.get_valor_tipado()
    
    return valor_padrao

def atualizar_configuracao(escola_id, chave, valor, tipo='string', descricao=None):
    """Atualizar ou criar uma configuração da escola"""
    
    config = ConfiguracaoEscola.query.filter_by(
        escola_id=escola_id,
        chave=chave
    ).first()
    
    if config:
        config.valor = str(valor)
        config.tipo = tipo
        config.data_atualizacao = datetime.now()
        if descricao:
            config.descricao = descricao
    else:
        config = ConfiguracaoEscola(
            escola_id=escola_id,
            chave=chave,
            valor=str(valor),
            tipo=tipo,
            descricao=descricao or f'Configuração {chave}'
        )
        db.session.add(config)
    
    db.session.commit()
    return config

def verificar_permissao(usuario_id, recurso, acao):
    """Verificar se usuário tem permissão para uma ação específica"""
    
    from .models import PermissaoCustomizada
    from apps.usuarios.models import Usuario
    
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return False
    
    # Administrador Geral tem acesso total
    if usuario.perfil_obj.nome == 'Administrador Geral':
        return True
    
    # Verificar permissão customizada
    permissao = PermissaoCustomizada.query.filter_by(
        usuario_id=usuario_id,
        recurso=recurso,
        permissao=acao,
        concedida=True
    ).first()
    
    if permissao:
        return True
    
    # Verificar permissões baseadas no perfil
    permissoes_perfil = {
        'Administrador da Escola': ['create', 'read', 'update', 'delete'],
        'Usuário Operacional da Escola': ['create', 'read']
    }
    
    perfil_permissoes = permissoes_perfil.get(usuario.perfil_obj.nome, [])
    return acao in perfil_permissoes

def log_acao(usuario_id, acao, item_alterado=None, detalhes=None, ip_address=None):
    """Registrar log de auditoria"""
    
    from apps.logs.models import LogAuditoria
    
    log = LogAuditoria(
        usuario_id=usuario_id,
        acao=acao,
        item_alterado=item_alterado,
        detalhes=detalhes,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()
    
    return log

def obter_estatisticas_gerais():
    """Obter estatísticas gerais do sistema"""
    
    from apps.escolas.models import Escola
    from apps.usuarios.models import Usuario
    from apps.dossies.models import Dossie
    from apps.movimentacoes.models import Movimentacao
    
    stats = {
        'total_escolas': Escola.query.filter_by(situacao='ativa').count(),
        'total_usuarios': Usuario.query.filter_by(status='ativo').count(),
        'total_dossies': Dossie.query.filter_by(status='ativo').count(),
        'total_movimentacoes': Movimentacao.query.count(),
        'escolas_ativas': Escola.query.filter_by(situacao='ativa').count(),
        'usuarios_ativos': Usuario.query.filter_by(status='ativo').count(),
        'dossies_ativos': Dossie.query.filter_by(status='ativo').count(),
        'movimentacoes_pendentes': Movimentacao.query.filter_by(status='pendente').count()
    }
    
    return stats
