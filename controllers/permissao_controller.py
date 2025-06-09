# controllers/permissao_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Perfil, Permissao, PerfilPermissao
from controllers.auth_controller import login_required

permissao_bp = Blueprint('permissao', __name__, url_prefix='/permissoes')

@permissao_bp.route('/')
@login_required
def index():
    """Lista todas as permissões"""
    permissoes = Permissao.query.order_by(Permissao.modulo, Permissao.acao).all()
    
    # Agrupar por módulo
    modulos = {}
    for perm in permissoes:
        if perm.modulo not in modulos:
            modulos[perm.modulo] = []
        modulos[perm.modulo].append(perm)
    
    return render_template('permissoes/index.html', modulos=modulos)

@permissao_bp.route('/perfis')
@login_required
def perfis():
    """Gerenciar permissões por perfil"""
    perfis = Perfil.query.all()
    permissoes = Permissao.query.order_by(Permissao.modulo, Permissao.acao).all()
    
    # Agrupar permissões por módulo
    modulos = {}
    for perm in permissoes:
        if perm.modulo not in modulos:
            modulos[perm.modulo] = []
        modulos[perm.modulo].append(perm)
    
    # Buscar permissões de cada perfil
    perfil_permissoes = {}
    for perfil in perfis:
        perms = db.session.query(Permissao).join(PerfilPermissao).filter(
            PerfilPermissao.perfil_id == perfil.id_perfil
        ).all()
        perfil_permissoes[perfil.id_perfil] = [p.id for p in perms]
    
    return render_template('permissoes/perfis.html', 
                         perfis=perfis, 
                         modulos=modulos,
                         perfil_permissoes=perfil_permissoes)

@permissao_bp.route('/perfil/<int:perfil_id>/atualizar', methods=['POST'])
@login_required
def atualizar_perfil(perfil_id):
    """Atualizar permissões de um perfil"""
    try:
        perfil = Perfil.query.get_or_404(perfil_id)
        
        # Remover permissões existentes
        PerfilPermissao.query.filter_by(perfil_id=perfil_id).delete()
        
        # Adicionar novas permissões
        permissoes_ids = request.form.getlist('permissoes')
        for perm_id in permissoes_ids:
            pp = PerfilPermissao(perfil_id=perfil_id, permissao_id=int(perm_id))
            db.session.add(pp)
        
        db.session.commit()
        flash(f'Permissões do perfil "{perfil.perfil}" atualizadas com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar permissões: {e}', 'error')
    
    return redirect(url_for('permissao.perfis'))

@permissao_bp.route('/verificar/<modulo>/<acao>')
@login_required
def verificar_permissao(modulo, acao):
    """API para verificar se usuário tem permissão"""
    from flask import session
    from models import Usuario
    
    usuario = Usuario.query.get(session.get('user_id'))
    if not usuario:
        return jsonify({'tem_permissao': False})
    
    # Admin Geral tem todas as permissões
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        return jsonify({'tem_permissao': True})
    
    # Verificar permissão específica
    tem_permissao = usuario.perfil_obj.has_permission(modulo, acao) if usuario.perfil_obj else False
    
    return jsonify({'tem_permissao': tem_permissao})

@permissao_bp.route('/usuario/<int:usuario_id>/permissoes')
@login_required
def permissoes_usuario(usuario_id):
    """Ver permissões de um usuário específico"""
    from models import Usuario
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.perfil_obj:
        permissoes = usuario.perfil_obj.get_permissoes()
        
        # Agrupar por módulo
        modulos = {}
        for perm in permissoes:
            if perm.modulo not in modulos:
                modulos[perm.modulo] = []
            modulos[perm.modulo].append(perm.acao)
    else:
        modulos = {}
    
    return render_template('permissoes/usuario.html', 
                         usuario=usuario, 
                         modulos=modulos)
