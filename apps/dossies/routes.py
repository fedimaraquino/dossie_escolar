"""
Aplicação DOSSIÊS - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import Dossie, DocumentoDossie
from apps.auth.routes import verificar_login
from apps.core.utils import log_acao
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Criar blueprint
dossies_bp = Blueprint('dossies', __name__)

@dossies_bp.route('/')
def listar():
    """Listar dossiês"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    # Busca e filtros
    search = request.args.get('search', '')
    ano = request.args.get('ano', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    # Query base
    query = Dossie.query

    # Filtrar por escola se não for admin geral
    if usuario.perfil_obj.nome != 'Administrador Geral':
        query = query.filter_by(escola_id=usuario.escola_id)

    # Aplicar filtros
    if search:
        from main import db
        query = query.filter(
            db.or_(
                Dossie.nome.contains(search),
                Dossie.cpf.contains(search),
                Dossie.numero_dossie.contains(search),
                Dossie.nome_pai.contains(search),
                Dossie.nome_mae.contains(search)
            )
        )

    if ano:
        query = query.filter_by(ano=int(ano))

    if status:
        query = query.filter_by(status=status)

    # Ordenar por data de cadastro (mais recentes primeiro)
    query = query.order_by(Dossie.data_cadastro.desc())

    # Paginação
    dossies = query.paginate(
        page=page, per_page=15, error_out=False
    )

    # Anos disponíveis para filtro
    from main import db
    anos_disponiveis = db.session.query(Dossie.ano).distinct().order_by(Dossie.ano.desc()).all()
    anos_disponiveis = [ano[0] for ano in anos_disponiveis if ano[0]]

    return render_template('dossies/listar.html',
                         dossies=dossies,
                         search=search,
                         ano=ano,
                         status=status,
                         anos_disponiveis=anos_disponiveis)

@dossies_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    """Criar novo dossiê"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        ano = request.form.get('ano', '').strip()

        if not nome or not cpf or not ano:
            flash('Nome, CPF e ano são obrigatórios!', 'error')
            return render_template('dossies/novo.html')

        # Verificar se CPF já existe no mesmo ano
        dossie_existente = Dossie.query.filter_by(cpf=cpf, ano=int(ano)).first()
        if dossie_existente:
            flash(f'Já existe um dossiê para este CPF no ano {ano}!', 'error')
            return render_template('dossies/novo.html')

        # Gerar número do dossiê
        ultimo_numero = Dossie.query.filter_by(ano=int(ano), escola_id=usuario.escola_id).count()
        numero_dossie = f"{ano}{str(ultimo_numero + 1).zfill(4)}"

        dossie = Dossie(
            numero_dossie=numero_dossie,
            ano=int(ano),
            nome=nome,
            cpf=cpf,
            nome_pai=request.form.get('nome_pai', '').strip(),
            nome_mae=request.form.get('nome_mae', '').strip(),
            data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d') if request.form.get('data_nascimento') else None,
            local=request.form.get('local', '').strip(),
            pasta=request.form.get('pasta', '').strip(),
            tipo_documento=request.form.get('tipo_documento', 'fisico'),
            observacoes=request.form.get('observacoes', '').strip(),
            escola_id=usuario.escola_id,
            usuario_cadastro_id=usuario.id
        )

        # Validar CPF
        if not dossie.validar_cpf():
            flash('CPF inválido!', 'error')
            return render_template('dossies/novo.html')

        try:
            from main import db
            db.session.add(dossie)
            db.session.commit()

            log_acao(usuario.id, 'DOSSIE_CRIADO', 'Dossie', f'Dossiê criado: {dossie.nome} ({dossie.numero_dossie})')
            flash('Dossiê cadastrado com sucesso!', 'success')
            return redirect(url_for('dossies.ver', id=dossie.id))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao cadastrar dossiê: {str(e)}', 'error')

    return render_template('dossies/novo.html')

@dossies_bp.route('/<int:id>')
def ver(id):
    """Ver detalhes do dossiê"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    dossie = Dossie.query.get_or_404(id)

    # Verificar permissão
    if usuario.perfil_obj.nome != 'Administrador Geral':
        if dossie.escola_id != usuario.escola_id:
            flash('Acesso negado.', 'error')
            return redirect(url_for('dossies.listar'))

    return render_template('dossies/ver.html', dossie=dossie)

@dossies_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar dossiê"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    dossie = Dossie.query.get_or_404(id)

    # Verificar permissão
    if usuario.perfil_obj.nome != 'Administrador Geral':
        if dossie.escola_id != usuario.escola_id:
            flash('Acesso negado.', 'error')
            return redirect(url_for('dossies.listar'))

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()

        if not nome or not cpf:
            flash('Nome e CPF são obrigatórios!', 'error')
            return render_template('dossies/editar.html', dossie=dossie)

        # Verificar se CPF já existe em outro dossiê do mesmo ano
        dossie_existente = Dossie.query.filter(
            Dossie.cpf == cpf,
            Dossie.ano == dossie.ano,
            Dossie.id != id
        ).first()
        if dossie_existente:
            flash(f'Já existe outro dossiê para este CPF no ano {dossie.ano}!', 'error')
            return render_template('dossies/editar.html', dossie=dossie)

        # Atualizar dados
        dossie.nome = nome
        dossie.cpf = cpf
        dossie.nome_pai = request.form.get('nome_pai', '').strip()
        dossie.nome_mae = request.form.get('nome_mae', '').strip()

        if request.form.get('data_nascimento'):
            dossie.data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d')

        dossie.local = request.form.get('local', '').strip()
        dossie.pasta = request.form.get('pasta', '').strip()
        dossie.tipo_documento = request.form.get('tipo_documento', 'fisico')
        dossie.status = request.form.get('status', 'ativo')
        dossie.observacoes = request.form.get('observacoes', '').strip()

        # Validar CPF
        if not dossie.validar_cpf():
            flash('CPF inválido!', 'error')
            return render_template('dossies/editar.html', dossie=dossie)

        try:
            from main import db
            db.session.commit()

            log_acao(usuario.id, 'DOSSIE_EDITADO', 'Dossie', f'Dossiê editado: {dossie.nome} ({dossie.numero_dossie})')
            flash('Dossiê atualizado com sucesso!', 'success')
            return redirect(url_for('dossies.ver', id=dossie.id))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao atualizar dossiê: {str(e)}', 'error')

    return render_template('dossies/editar.html', dossie=dossie)

@dossies_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Excluir dossiê"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    from apps.usuarios.models import Usuario
    usuario = Usuario.query.get(session['user_id'])

    # Apenas admins podem excluir
    if usuario.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dossies.listar'))

    dossie = Dossie.query.get_or_404(id)

    # Verificar permissão
    if usuario.perfil_obj.nome != 'Administrador Geral':
        if dossie.escola_id != usuario.escola_id:
            flash('Acesso negado.', 'error')
            return redirect(url_for('dossies.listar'))

    # Verificar se há movimentações vinculadas
    if dossie.movimentacoes:
        flash('Não é possível excluir dossiê com movimentações vinculadas!', 'error')
        return redirect(url_for('dossies.ver', id=id))

    try:
        nome_dossie = f"{dossie.nome} ({dossie.numero_dossie})"
        from main import db
        db.session.delete(dossie)
        db.session.commit()

        log_acao(usuario.id, 'DOSSIE_EXCLUIDO', 'Dossie', f'Dossiê excluído: {nome_dossie}')
        flash('Dossiê excluído com sucesso!', 'success')
        return redirect(url_for('dossies.listar'))
    except Exception as e:
        from main import db
        db.session.rollback()
        flash(f'Erro ao excluir dossiê: {str(e)}', 'error')
        return redirect(url_for('dossies.ver', id=id))
