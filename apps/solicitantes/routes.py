"""
Aplicação SOLICITANTES - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import Solicitante
from apps.auth.routes import verificar_login
from apps.core.utils import log_acao
from datetime import datetime

# Criar blueprint
solicitantes_bp = Blueprint('solicitantes', __name__, url_prefix='/solicitantes')

@solicitantes_bp.route('/')
def listar():
    """Listar solicitantes"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    # Busca e filtros
    search = request.args.get('search', '')
    parentesco = request.args.get('parentesco', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    # Obter usuário atual e aplicar filtro de escola
    from models import Usuario
    usuario_atual = Usuario.query.get(session['user_id'])

    # Query base com filtro de escola
    query = Solicitante.query
    escola_atual_id = usuario_atual.get_escola_atual_id()
    if escola_atual_id:
        query = query.filter(Solicitante.escola_id == escola_atual_id)

    # Aplicar filtros
    if search:
        from models import db
        query = query.filter(
            db.or_(
                Solicitante.nome.contains(search),
                Solicitante.cpf.contains(search),
                Solicitante.email.contains(search)
            )
        )

    if parentesco:
        query = query.filter_by(parentesco=parentesco)

    if status:
        query = query.filter_by(status=status)

    # Ordenar por nome
    query = query.order_by(Solicitante.nome)

    # Paginação
    solicitantes = query.paginate(
        page=page, per_page=15, error_out=False
    )

    return render_template('solicitantes/listar.html',
                         solicitantes=solicitantes,
                         search=search,
                         parentesco=parentesco,
                         status=status)

@solicitantes_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    """Criar novo solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from models import Usuario, Cidade
    usuario = Usuario.query.get(session['user_id'])
    cidades = Cidade.query.order_by(Cidade.nome).all()

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()

        if not nome or not cpf:
            flash('Nome e CPF são obrigatórios!', 'error')
            return render_template('solicitantes/novo.html')

        # Verificar se CPF já existe
        solicitante_existente = Solicitante.query.filter_by(cpf=cpf).first()
        if solicitante_existente:
            flash('Já existe um solicitante com este CPF!', 'error')
            return render_template('solicitantes/novo.html')

        # Obter escola atual do usuário
        escola_atual_id = usuario.get_escola_atual_id()

        solicitante = Solicitante(
            nome=nome,
            cpf=cpf,
            endereco=request.form.get('endereco', '').strip(),
            celular=request.form.get('celular', '').strip(),
            cidade_id=int(request.form.get('cidade_id')) if request.form.get('cidade_id') else None,
            email=request.form.get('email', '').strip(),
            parentesco=request.form.get('parentesco', '').strip(),
            tipo_solicitacao=request.form.get('tipo_solicitacao', 'consulta'),
            data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d') if request.form.get('data_nascimento') else None,
            escola_id=escola_atual_id
        )

        # Validar CPF
        if not solicitante.validar_cpf():
            flash('CPF inválido!', 'error')
            return render_template('solicitantes/novo.html', cidades=cidades)

        try:
            from models import db
            db.session.add(solicitante)
            db.session.commit()

            log_acao(usuario.id, 'SOLICITANTE_CRIADO', 'Solicitante', f'Solicitante criado: {solicitante.nome}')
            flash('Solicitante cadastrado com sucesso!', 'success')
            return redirect(url_for('solicitantes.ver', id=solicitante.id))
        except Exception as e:
            from models import db
            db.session.rollback()
            flash(f'Erro ao cadastrar solicitante: {str(e)}', 'error')

    return render_template('solicitantes/novo.html', cidades=cidades)

@solicitantes_bp.route('/<int:id>')
def ver(id):
    """Ver detalhes do solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    # Verificar acesso à escola do solicitante
    from models import Usuario
    usuario_atual = Usuario.query.get(session['user_id'])

    solicitante = Solicitante.query.get_or_404(id)

    # Verificar se o usuário pode acessar este solicitante
    if not usuario_atual.can_access_escola(solicitante.escola_id):
        flash('Acesso negado a este solicitante.', 'error')
        return redirect(url_for('solicitantes.listar'))

    return render_template('solicitantes/ver.html', solicitante=solicitante)

@solicitantes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from models import Usuario, Cidade
    usuario = Usuario.query.get(session['user_id'])
    cidades = Cidade.query.order_by(Cidade.nome).all()

    solicitante = Solicitante.query.get_or_404(id)

    # Verificar se o usuário pode acessar este solicitante
    if not usuario.can_access_escola(solicitante.escola_id):
        flash('Acesso negado a este solicitante.', 'error')
        return redirect(url_for('solicitantes.listar'))

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()

        if not nome or not cpf:
            flash('Nome e CPF são obrigatórios!', 'error')
            return render_template('solicitantes/editar.html', solicitante=solicitante, cidades=cidades)

        # Verificar se CPF já existe em outro solicitante
        solicitante_existente = Solicitante.query.filter(
            Solicitante.cpf == cpf,
            Solicitante.id != id
        ).first()
        if solicitante_existente:
            flash('Já existe outro solicitante com este CPF!', 'error')
            return render_template('solicitantes/editar.html', solicitante=solicitante, cidades=cidades)

        # Atualizar dados
        solicitante.nome = nome
        solicitante.cpf = cpf
        solicitante.endereco = request.form.get('endereco', '').strip()
        solicitante.celular = request.form.get('celular', '').strip()
        solicitante.cidade_id = int(request.form.get('cidade_id')) if request.form.get('cidade_id') else None
        solicitante.email = request.form.get('email', '').strip()
        solicitante.parentesco = request.form.get('parentesco', '').strip()
        solicitante.tipo_solicitacao = request.form.get('tipo_solicitacao', 'consulta')
        solicitante.status = request.form.get('status', 'ativo')

        if request.form.get('data_nascimento'):
            solicitante.data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d')

        # Validar CPF
        if not solicitante.validar_cpf():
            flash('CPF inválido!', 'error')
            return render_template('solicitantes/editar.html', solicitante=solicitante, cidades=cidades)

        try:
            from models import db
            db.session.commit()

            log_acao(usuario.id, 'SOLICITANTE_EDITADO', 'Solicitante', f'Solicitante editado: {solicitante.nome}')
            flash('Solicitante atualizado com sucesso!', 'success')
            return redirect(url_for('solicitantes.ver', id=solicitante.id))
        except Exception as e:
            from models import db
            db.session.rollback()
            flash(f'Erro ao atualizar solicitante: {str(e)}', 'error')

    return render_template('solicitantes/editar.html', solicitante=solicitante, cidades=cidades)

@solicitantes_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Excluir solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    # Apenas admins podem excluir
    if usuario.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('solicitantes.listar'))

    solicitante = Solicitante.query.get_or_404(id)

    # Verificar se há movimentações vinculadas
    if solicitante.movimentacoes:
        flash('Não é possível excluir solicitante com movimentações vinculadas!', 'error')
        return redirect(url_for('solicitantes.ver', id=id))

    try:
        nome_solicitante = solicitante.nome
        from models import db
        db.session.delete(solicitante)
        db.session.commit()

        log_acao(usuario.id, 'SOLICITANTE_EXCLUIDO', 'Solicitante', f'Solicitante excluído: {nome_solicitante}')
        flash('Solicitante excluído com sucesso!', 'success')
        return redirect(url_for('solicitantes.listar'))
    except Exception as e:
        from models import db
        db.session.rollback()
        flash(f'Erro ao excluir solicitante: {str(e)}', 'error')
        return redirect(url_for('solicitantes.ver', id=id))

@solicitantes_bp.route('/ativar/<int:id>', methods=['POST'])
def ativar(id):
    """Ativar solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    # Apenas admins podem ativar/desativar
    if usuario.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('solicitantes.listar'))

    solicitante = Solicitante.query.get_or_404(id)

    try:
        solicitante.status = 'ativo'
        from models import db
        db.session.commit()

        log_acao(usuario.id, 'SOLICITANTE_ATIVADO', 'Solicitante', f'Solicitante ativado: {solicitante.nome}')
        flash('Solicitante ativado com sucesso!', 'success')
    except Exception as e:
        from models import db
        db.session.rollback()
        flash(f'Erro ao ativar solicitante: {str(e)}', 'error')

    return redirect(url_for('solicitantes.ver', id=id))

@solicitantes_bp.route('/desativar/<int:id>', methods=['POST'])
def desativar(id):
    """Desativar solicitante"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    # Apenas admins podem ativar/desativar
    if usuario.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('solicitantes.listar'))

    solicitante = Solicitante.query.get_or_404(id)

    try:
        solicitante.status = 'inativo'
        from models import db
        db.session.commit()

        log_acao(usuario.id, 'SOLICITANTE_DESATIVADO', 'Solicitante', f'Solicitante desativado: {solicitante.nome}')
        flash('Solicitante desativado com sucesso!', 'success')
    except Exception as e:
        from models import db
        db.session.rollback()
        flash(f'Erro ao desativar solicitante: {str(e)}', 'error')

    return redirect(url_for('solicitantes.ver', id=id))
