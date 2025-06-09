# controllers/perfil_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Perfil
from .auth_controller import login_required, admin_required

perfil_bp = Blueprint('perfil', __name__, url_prefix='/perfis')

@perfil_bp.route('/')
@admin_required
def listar():
    """Lista todos os perfis"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)

    query = Perfil.query
    
    if search:
        query = query.filter(Perfil.perfil.contains(search))

    perfis = query.order_by(Perfil.perfil).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('perfis/listar.html', 
                         perfis=perfis, 
                         search=search)

@perfil_bp.route('/novo', methods=['GET', 'POST'])
@admin_required
def novo():
    """Cadastra novo perfil"""
    if request.method == 'POST':
        perfil_nome = request.form.get('perfil', '').strip()
        descricao = request.form.get('descricao', '').strip()

        if not perfil_nome:
            flash('Nome do perfil é obrigatório!', 'error')
            return render_template('perfis/novo.html')

        # Verificar se já existe
        if Perfil.query.filter_by(perfil=perfil_nome).first():
            flash('Perfil já cadastrado!', 'error')
            return render_template('perfis/novo.html')

        perfil = Perfil(
            perfil=perfil_nome,
            descricao=descricao if descricao else None
        )

        try:
            db.session.add(perfil)
            db.session.commit()
            flash('Perfil cadastrado com sucesso!', 'success')
            return redirect(url_for('perfil.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar perfil: {str(e)}', 'error')

    return render_template('perfis/novo.html')

@perfil_bp.route('/ver/<int:id>')
@admin_required
def ver(id):
    """Visualiza detalhes do perfil"""
    perfil = Perfil.query.get_or_404(id)
    
    # Contar usuários com este perfil
    from models import Usuario
    usuarios_count = Usuario.query.filter_by(perfil_id=perfil.id_perfil).count()
    
    return render_template('perfis/ver.html', perfil=perfil, usuarios_count=usuarios_count)

@perfil_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    """Edita dados do perfil"""
    perfil = Perfil.query.get_or_404(id)

    if request.method == 'POST':
        perfil_nome = request.form.get('perfil', '').strip()
        descricao = request.form.get('descricao', '').strip()

        if not perfil_nome:
            flash('Nome do perfil é obrigatório!', 'error')
            return render_template('perfis/editar.html', perfil=perfil)

        # Verificar se já existe outro perfil com mesmo nome
        perfil_existente = Perfil.query.filter_by(perfil=perfil_nome).first()
        if perfil_existente and perfil_existente.id_perfil != perfil.id_perfil:
            flash('Já existe outro perfil com este nome!', 'error')
            return render_template('perfis/editar.html', perfil=perfil)

        perfil.perfil = perfil_nome
        perfil.descricao = descricao if descricao else None

        try:
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('perfil.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')

    return render_template('perfis/editar.html', perfil=perfil)

@perfil_bp.route('/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir(id):
    """Exclui perfil"""
    perfil = Perfil.query.get_or_404(id)
    
    # Verificar se há usuários vinculados
    from models import Usuario
    usuarios_vinculados = Usuario.query.filter_by(perfil_id=perfil.id_perfil).count()
    
    if usuarios_vinculados > 0:
        flash(f'Não é possível excluir o perfil "{perfil.perfil}" pois há {usuarios_vinculados} usuário(s) vinculado(s).', 'error')
        return redirect(url_for('perfil.listar'))

    # Não permitir excluir perfis padrão do sistema
    perfis_sistema = ['Administrador Geral', 'Administrador da Escola', 'Operador', 'Consulta']
    if perfil.perfil in perfis_sistema:
        flash(f'Não é possível excluir o perfil "{perfil.perfil}" pois é um perfil padrão do sistema.', 'error')
        return redirect(url_for('perfil.listar'))

    try:
        db.session.delete(perfil)
        db.session.commit()
        flash(f'Perfil "{perfil.perfil}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir perfil: {str(e)}', 'error')

    return redirect(url_for('perfil.listar'))

@perfil_bp.route('/usuarios/<int:id>')
@admin_required
def usuarios(id):
    """Lista usuários de um perfil específico"""
    perfil = Perfil.query.get_or_404(id)
    
    from models import Usuario
    usuarios = Usuario.query.filter_by(perfil_id=perfil.id_perfil).order_by(Usuario.nome).all()
    
    return render_template('perfis/usuarios.html', perfil=perfil, usuarios=usuarios)
