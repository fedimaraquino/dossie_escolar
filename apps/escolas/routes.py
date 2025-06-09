"""
Aplicação ESCOLAS - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import Escola
from apps.auth.routes import verificar_login
from apps.core.utils import log_acao

# Criar blueprint
escolas_bp = Blueprint('escolas', __name__)

@escolas_bp.route('/')
def listar():
    """Listar escolas"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    # Apenas Admin Geral pode listar escolas
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect('/')
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Escola.query
    if search:
        query = query.filter(Escola.nome.contains(search))
    
    escolas = query.order_by(Escola.nome).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('escolas/listar.html', escolas=escolas, search=search)

@escolas_bp.route('/nova', methods=['GET', 'POST'])
def nova():
    """Criar nova escola"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect('/')

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip()

        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/nova.html')

        # Verificar se já existe escola com mesmo nome
        escola_existente = Escola.query.filter_by(nome=nome).first()
        if escola_existente:
            flash('Já existe uma escola com este nome!', 'error')
            return render_template('escolas/nova.html')

        escola = Escola(
            nome=nome,
            endereco=request.form.get('endereco', '').strip(),
            uf=uf,
            cnpj=request.form.get('cnpj', '').strip(),
            inep=request.form.get('inep', '').strip(),
            email=request.form.get('email', '').strip(),
            telefone=request.form.get('telefone', '').strip(),
            diretor=request.form.get('diretor', '').strip(),
            vice_diretor=request.form.get('vice_diretor', '').strip(),
            observacoes=request.form.get('observacoes', '').strip(),
            usuario_cadastro_id=usuario.id
        )

        # Validar CNPJ se fornecido
        if escola.cnpj and not escola.validar_cnpj():
            flash('CNPJ inválido!', 'error')
            return render_template('escolas/nova.html')

        # Validar INEP se fornecido
        if escola.inep and not escola.validar_inep():
            flash('Código INEP inválido!', 'error')
            return render_template('escolas/nova.html')

        try:
            from main import db
            db.session.add(escola)
            db.session.commit()

            # Aplicar configurações padrão
            from apps.core.utils import aplicar_configuracoes_padrao
            aplicar_configuracoes_padrao(escola.id)

            log_acao(usuario.id, 'ESCOLA_CRIADA', 'Escola', f'Escola criada: {escola.nome}')
            flash('Escola cadastrada com sucesso!', 'success')
            return redirect(url_for('escolas.listar'))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao cadastrar escola: {str(e)}', 'error')

    # Buscar cidades para o formulário
    from apps.core.models import Cidade
    cidades = Cidade.query.filter_by(ativo=True).order_by(Cidade.nome).all()

    return render_template('escolas/nova.html', cidades=cidades)

@escolas_bp.route('/<int:id>')
def ver(id):
    """Ver detalhes da escola"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    
    escola = Escola.query.get_or_404(id)
    
    # Verificar permissão
    if not usuario.pode_acessar_escola(escola.id):
        flash('Acesso negado.', 'error')
        return redirect('/')
    
    return render_template('escolas/ver.html', escola=escola)

@escolas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar escola"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect('/')

    escola = Escola.query.get_or_404(id)

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip()

        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/editar.html', escola=escola)

        # Verificar se já existe outra escola com mesmo nome
        escola_existente = Escola.query.filter(Escola.nome == nome, Escola.id != id).first()
        if escola_existente:
            flash('Já existe outra escola com este nome!', 'error')
            return render_template('escolas/editar.html', escola=escola)

        # Atualizar dados
        escola.nome = nome
        escola.endereco = request.form.get('endereco', '').strip()
        escola.uf = uf
        escola.cnpj = request.form.get('cnpj', '').strip()
        escola.inep = request.form.get('inep', '').strip()
        escola.email = request.form.get('email', '').strip()
        escola.telefone = request.form.get('telefone', '').strip()
        escola.diretor = request.form.get('diretor', '').strip()
        escola.vice_diretor = request.form.get('vice_diretor', '').strip()
        escola.observacoes = request.form.get('observacoes', '').strip()
        escola.situacao = request.form.get('situacao', 'ativa')

        # Validar CNPJ se fornecido
        if escola.cnpj and not escola.validar_cnpj():
            flash('CNPJ inválido!', 'error')
            return render_template('escolas/editar.html', escola=escola)

        # Validar INEP se fornecido
        if escola.inep and not escola.validar_inep():
            flash('Código INEP inválido!', 'error')
            return render_template('escolas/editar.html', escola=escola)

        try:
            from main import db
            db.session.commit()

            log_acao(usuario.id, 'ESCOLA_EDITADA', 'Escola', f'Escola editada: {escola.nome}')
            flash('Escola atualizada com sucesso!', 'success')
            return redirect(url_for('escolas.ver', id=escola.id))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao atualizar escola: {str(e)}', 'error')

    # Buscar cidades para o formulário
    from apps.core.models import Cidade
    cidades = Cidade.query.filter_by(ativo=True).order_by(Cidade.nome).all()

    return render_template('escolas/editar.html', escola=escola, cidades=cidades)

@escolas_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Excluir escola"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    if usuario.perfil_obj.nome != 'Administrador Geral':
        flash('Acesso negado.', 'error')
        return redirect('/')

    escola = Escola.query.get_or_404(id)

    # Verificar se há usuários vinculados
    if escola.usuarios:
        flash('Não é possível excluir escola com usuários vinculados!', 'error')
        return redirect(url_for('escolas.ver', id=id))

    # Verificar se há dossiês vinculados
    if escola.dossies:
        flash('Não é possível excluir escola com dossiês vinculados!', 'error')
        return redirect(url_for('escolas.ver', id=id))

    try:
        nome_escola = escola.nome
        from main import db
        db.session.delete(escola)
        db.session.commit()

        log_acao(usuario.id, 'ESCOLA_EXCLUIDA', 'Escola', f'Escola excluída: {nome_escola}')
        flash('Escola excluída com sucesso!', 'success')
        return redirect(url_for('escolas.listar'))
    except Exception as e:
        from main import db
        db.session.rollback()
        flash(f'Erro ao excluir escola: {str(e)}', 'error')
        return redirect(url_for('escolas.ver', id=id))

@escolas_bp.route('/api')
def api_listar():
    """API para listar escolas"""
    if not verificar_login():
        return jsonify({'error': 'Não autorizado'}), 401

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    if usuario.perfil_obj.nome == 'Administrador Geral':
        escolas = Escola.query.filter_by(situacao='ativa').all()
    else:
        escolas = [usuario.escola]

    return jsonify([escola.to_dict() for escola in escolas])
