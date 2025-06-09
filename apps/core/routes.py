"""
Aplicação CORE - Rotas e Views
Dashboard e funcionalidades centrais
"""

from flask import Blueprint, render_template, session, request, jsonify
from .utils import obter_estatisticas_gerais, obter_configuracao
from .models import Cidade, Perfil

# Criar blueprint
core_bp = Blueprint('core', __name__)

def dashboard():
    """Dashboard principal do sistema"""
    
    if 'user_id' not in session:
        from apps.auth.routes import login_page
        return login_page()
    
    # Obter dados do usuário logado
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    if not usuario:
        from apps.auth.routes import logout
        return logout()
    
    # Obter estatísticas baseadas no perfil do usuário
    if usuario.perfil_obj.nome == 'Administrador Geral':
        # Admin geral vê todas as estatísticas
        stats = obter_estatisticas_gerais()
        escola_filter = None
    else:
        # Outros usuários veem apenas da sua escola
        from apps.escolas.models import Escola
        from apps.dossies.models import Dossie
        from apps.movimentacoes.models import Movimentacao
        
        stats = {
            'total_escolas': 1,
            'total_usuarios': Usuario.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'total_dossies': Dossie.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'total_movimentacoes': Movimentacao.query.filter_by(escola_id=usuario.escola_id).count(),
            'escolas_ativas': 1,
            'usuarios_ativos': Usuario.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'dossies_ativos': Dossie.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'movimentacoes_pendentes': Movimentacao.query.filter_by(escola_id=usuario.escola_id, status='pendente').count()
        }
        escola_filter = usuario.escola_id
    
    # Obter dados recentes
    if escola_filter:
        from apps.dossies.models import Dossie
        from apps.movimentacoes.models import Movimentacao
        
        dossies_recentes = Dossie.query.filter_by(escola_id=escola_filter).order_by(Dossie.data_cadastro.desc()).limit(5).all()
        movimentacoes_recentes = Movimentacao.query.filter_by(escola_id=escola_filter).order_by(Movimentacao.data_solicitacao.desc()).limit(5).all()
    else:
        from apps.dossies.models import Dossie
        from apps.movimentacoes.models import Movimentacao
        
        dossies_recentes = Dossie.query.order_by(Dossie.data_cadastro.desc()).limit(5).all()
        movimentacoes_recentes = Movimentacao.query.order_by(Movimentacao.data_solicitacao.desc()).limit(5).all()
    
    return render_template('dashboard_modular.html',
                         usuario=usuario,
                         stats=stats,
                         dossies_recentes=dossies_recentes,
                         movimentacoes_recentes=movimentacoes_recentes)

@core_bp.route('/api/estatisticas')
def api_estatisticas():
    """API para obter estatísticas em tempo real"""
    
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.perfil_obj.nome == 'Administrador Geral':
        stats = obter_estatisticas_gerais()
    else:
        # Estatísticas da escola do usuário
        from apps.dossies.models import Dossie
        from apps.movimentacoes.models import Movimentacao
        
        stats = {
            'total_usuarios': Usuario.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'total_dossies': Dossie.query.filter_by(escola_id=usuario.escola_id, status='ativo').count(),
            'total_movimentacoes': Movimentacao.query.filter_by(escola_id=usuario.escola_id).count(),
            'movimentacoes_pendentes': Movimentacao.query.filter_by(escola_id=usuario.escola_id, status='pendente').count()
        }
    
    return jsonify(stats)

@core_bp.route('/cidades')
def listar_cidades():
    """Listar cidades para formulários"""
    
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    uf = request.args.get('uf')
    
    query = Cidade.query.filter_by(ativo=True)
    if uf:
        query = query.filter_by(uf=uf)
    
    cidades = query.order_by(Cidade.nome).all()
    
    return jsonify([cidade.to_dict() for cidade in cidades])

@core_bp.route('/perfis')
def listar_perfis():
    """Listar perfis para formulários"""
    
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    # Administrador Geral pode ver todos os perfis
    if usuario.perfil_obj.nome == 'Administrador Geral':
        perfis = Perfil.query.filter_by(ativo=True).order_by(Perfil.nivel_acesso.desc()).all()
    else:
        # Outros usuários veem apenas perfis de nível inferior
        perfis = Perfil.query.filter(
            Perfil.ativo == True,
            Perfil.nivel_acesso < usuario.perfil_obj.nivel_acesso
        ).order_by(Perfil.nivel_acesso.desc()).all()
    
    return jsonify([perfil.to_dict() for perfil in perfis])

@core_bp.route('/configuracoes/<int:escola_id>')
def obter_configuracoes_escola(escola_id):
    """Obter configurações de uma escola"""
    
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    # Verificar permissão
    if usuario.perfil_obj.nome != 'Administrador Geral' and usuario.escola_id != escola_id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    from .models import ConfiguracaoEscola
    configuracoes = ConfiguracaoEscola.query.filter_by(escola_id=escola_id, ativo=True).all()
    
    return jsonify([config.to_dict() for config in configuracoes])

@core_bp.route('/notificacoes')
def obter_notificacoes():
    """Obter notificações do usuário"""
    
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    from apps.usuarios.models import Usuario
    from apps.movimentacoes.models import Movimentacao
    from datetime import datetime, timedelta
    
    usuario = Usuario.query.get(session['user_id'])
    notificacoes = []
    
    # Movimentações pendentes há mais de 7 dias
    data_limite = datetime.now() - timedelta(days=7)
    
    if usuario.perfil_obj.nome == 'Administrador Geral':
        movimentacoes_pendentes = Movimentacao.query.filter(
            Movimentacao.status == 'pendente',
            Movimentacao.data_solicitacao < data_limite
        ).count()
    else:
        movimentacoes_pendentes = Movimentacao.query.filter(
            Movimentacao.escola_id == usuario.escola_id,
            Movimentacao.status == 'pendente',
            Movimentacao.data_solicitacao < data_limite
        ).count()
    
    if movimentacoes_pendentes > 0:
        notificacoes.append({
            'tipo': 'warning',
            'titulo': 'Movimentações Pendentes',
            'mensagem': f'{movimentacoes_pendentes} movimentações pendentes há mais de 7 dias',
            'url': '/movimentacoes?status=pendente'
        })
    
    # Usuários bloqueados
    if usuario.perfil_obj.nome in ['Administrador Geral', 'Administrador da Escola']:
        usuarios_bloqueados = Usuario.query.filter(
            Usuario.bloqueado_ate > datetime.now()
        )
        
        if usuario.perfil_obj.nome != 'Administrador Geral':
            usuarios_bloqueados = usuarios_bloqueados.filter_by(escola_id=usuario.escola_id)
        
        count_bloqueados = usuarios_bloqueados.count()
        
        if count_bloqueados > 0:
            notificacoes.append({
                'tipo': 'danger',
                'titulo': 'Usuários Bloqueados',
                'mensagem': f'{count_bloqueados} usuários estão bloqueados',
                'url': '/usuarios?status=bloqueado'
            })
    
    return jsonify(notificacoes)
