"""
Aplicação USUÁRIOS - Rotas
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from .models import Usuario
from apps.auth.routes import verificar_login
from apps.core.utils import log_acao

# Criar blueprint
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/')
def listar():
    """Listar usuários"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    usuario_logado = Usuario.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Usuario.query
    
    # Filtrar por escola se não for admin geral
    if usuario_logado.perfil_obj.nome != 'Administrador Geral':
        query = query.filter_by(escola_id=usuario_logado.escola_id)
    
    if search:
        query = query.filter(Usuario.nome.contains(search))
    
    usuarios = query.order_by(Usuario.nome).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('usuarios/listar.html', usuarios=usuarios, search=search)

@usuarios_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    """Criar novo usuário"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    usuario_logado = Usuario.query.get(session['user_id'])

    # Verificar permissão
    if usuario_logado.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect('/')

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        perfil_id = request.form.get('perfil_id')
        escola_id = request.form.get('escola_id')

        if not nome or not email or not perfil_id or not escola_id:
            flash('Nome, email, perfil e escola são obrigatórios!', 'error')
            return render_template('usuarios/novo.html')

        # Verificar se email já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('Já existe um usuário com este email!', 'error')
            return render_template('usuarios/novo.html')

        # Verificar se CPF já existe (se fornecido)
        cpf = request.form.get('cpf', '').strip()
        if cpf:
            cpf_existente = Usuario.query.filter_by(cpf=cpf).first()
            if cpf_existente:
                flash('Já existe um usuário com este CPF!', 'error')
                return render_template('usuarios/novo.html')

        usuario = Usuario(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=request.form.get('telefone', '').strip(),
            cargo=request.form.get('cargo', '').strip(),
            endereco=request.form.get('endereco', '').strip(),
            perfil_id=int(perfil_id),
            escola_id=int(escola_id),
            usuario_cadastro_id=usuario_logado.id
        )

        # Validar CPF se fornecido
        if usuario.cpf and not usuario.validar_cpf():
            flash('CPF inválido!', 'error')
            return render_template('usuarios/novo.html')

        # Definir senha padrão
        senha_padrao = request.form.get('senha', '123456')
        usuario.set_password(senha_padrao)

        try:
            from main import db
            db.session.add(usuario)
            db.session.commit()

            log_acao(usuario_logado.id, 'USUARIO_CRIADO', 'Usuario', f'Usuário criado: {usuario.nome}')
            flash(f'Usuário cadastrado com sucesso! Senha: {senha_padrao}', 'success')
            return redirect(url_for('usuarios.listar'))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')

    # Buscar dados para formulário
    from apps.core.models import Perfil
    from apps.escolas.models import Escola

    # Filtrar perfis baseado no usuário logado
    if usuario_logado.perfil_obj.nome == 'Administrador Geral':
        perfis = Perfil.query.filter_by(ativo=True).all()
        escolas = Escola.query.filter_by(situacao='ativa').all()
    else:
        # Admin da escola só pode criar usuários de nível inferior
        perfis = Perfil.query.filter(
            Perfil.ativo == True,
            Perfil.nivel_acesso < usuario_logado.perfil_obj.nivel_acesso
        ).all()
        escolas = [usuario_logado.escola]

    return render_template('usuarios/novo.html', perfis=perfis, escolas=escolas)

@usuarios_bp.route('/<int:id>')
def ver(id):
    """Ver detalhes do usuário"""
    if not verificar_login():
        return redirect(url_for('auth.login'))
    
    usuario_logado = Usuario.query.get(session['user_id'])
    usuario = Usuario.query.get_or_404(id)
    
    # Verificar permissão
    if not usuario_logado.pode_acessar_escola(usuario.escola_id):
        flash('Acesso negado.', 'error')
        return redirect('/')
    
    return render_template('usuarios/ver.html', usuario=usuario)

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Editar usuário"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    usuario_logado = Usuario.query.get(session['user_id'])
    usuario = Usuario.query.get_or_404(id)

    # Verificar permissão
    if usuario_logado.perfil_obj.nome == 'Usuário Operacional':
        if usuario.id != usuario_logado.id:
            flash('Acesso negado.', 'error')
            return redirect('/')
    elif usuario_logado.perfil_obj.nome == 'Administrador da Escola':
        if usuario.escola_id != usuario_logado.escola_id:
            flash('Acesso negado.', 'error')
            return redirect('/')

    if request.method == 'POST':
        # Validações
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not nome or not email:
            flash('Nome e email são obrigatórios!', 'error')
            return render_template('usuarios/editar.html', usuario=usuario)

        # Verificar se email já existe em outro usuário
        usuario_existente = Usuario.query.filter(Usuario.email == email, Usuario.id != id).first()
        if usuario_existente:
            flash('Já existe outro usuário com este email!', 'error')
            return render_template('usuarios/editar.html', usuario=usuario)

        # Atualizar dados
        usuario.nome = nome
        usuario.email = email
        usuario.telefone = request.form.get('telefone', '').strip()
        usuario.cargo = request.form.get('cargo', '').strip()

        # Apenas admins podem alterar perfil e escola
        if usuario_logado.perfil_obj.nome in ['Administrador Geral', 'Administrador da Escola']:
            perfil_id = request.form.get('perfil_id')
            escola_id = request.form.get('escola_id')

            if perfil_id:
                usuario.perfil_id = int(perfil_id)
            if escola_id:
                usuario.escola_id = int(escola_id)

            # Status
            usuario.status = request.form.get('status', 'ativo')

        # Alterar senha se fornecida
        nova_senha = request.form.get('nova_senha', '').strip()
        if nova_senha:
            usuario.set_password(nova_senha)

        try:
            from main import db
            db.session.commit()

            log_acao(usuario_logado.id, 'USUARIO_EDITADO', 'Usuario', f'Usuário editado: {usuario.nome}')
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios.ver', id=usuario.id))
        except Exception as e:
            from main import db
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'error')

    # Buscar dados para formulário
    from apps.core.models import Perfil
    from apps.escolas.models import Escola

    # Filtrar perfis baseado no usuário logado
    if usuario_logado.perfil_obj.nome == 'Administrador Geral':
        perfis = Perfil.query.filter_by(ativo=True).all()
        escolas = Escola.query.filter_by(situacao='ativa').all()
    elif usuario_logado.perfil_obj.nome == 'Administrador da Escola':
        perfis = Perfil.query.filter(
            Perfil.ativo == True,
            Perfil.nivel_acesso < usuario_logado.perfil_obj.nivel_acesso
        ).all()
        escolas = [usuario_logado.escola]
    else:
        perfis = []
        escolas = []

    return render_template('usuarios/editar.html', usuario=usuario, perfis=perfis, escolas=escolas)

@usuarios_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Excluir usuário"""
    if not verificar_login():
        return redirect(url_for('auth.login'))

    usuario_logado = Usuario.query.get(session['user_id'])
    usuario = Usuario.query.get_or_404(id)

    # Verificar permissão
    if usuario_logado.perfil_obj.nome not in ['Administrador Geral', 'Administrador da Escola']:
        flash('Acesso negado.', 'error')
        return redirect('/')

    if usuario_logado.perfil_obj.nome == 'Administrador da Escola':
        if usuario.escola_id != usuario_logado.escola_id:
            flash('Acesso negado.', 'error')
            return redirect('/')

    # Não permitir excluir a si mesmo
    if usuario.id == usuario_logado.id:
        flash('Não é possível excluir seu próprio usuário!', 'error')
        return redirect(url_for('usuarios.ver', id=id))

    try:
        nome_usuario = usuario.nome
        from main import db
        db.session.delete(usuario)
        db.session.commit()

        log_acao(usuario_logado.id, 'USUARIO_EXCLUIDO', 'Usuario', f'Usuário excluído: {nome_usuario}')
        flash('Usuário excluído com sucesso!', 'success')
        return redirect(url_for('usuarios.listar'))
    except Exception as e:
        from main import db
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'error')
        return redirect(url_for('usuarios.ver', id=id))

@usuarios_bp.route('/api')
def api_listar():
    """API para listar usuários"""
    if not verificar_login():
        return jsonify({'error': 'Não autorizado'}), 401

    usuario_logado = Usuario.query.get(session['user_id'])

    if usuario_logado.perfil_obj.nome == 'Administrador Geral':
        usuarios = Usuario.query.filter_by(status='ativo').all()
    else:
        usuarios = Usuario.query.filter_by(escola_id=usuario_logado.escola_id, status='ativo').all()

    return jsonify([usuario.to_dict() for usuario in usuarios])
