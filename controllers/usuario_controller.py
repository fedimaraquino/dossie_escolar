# controllers/usuario_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import datetime
from models import db, Usuario, Escola, Perfil
from .auth_controller import login_required, admin_required
from utils.logs import log_acao, AcoesAuditoria

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/')
@login_required
def listar():
    """Lista usuários"""
    search = request.args.get('search', '')
    escola_id = request.args.get('escola', '')
    perfil_id = request.args.get('perfil', '')
    situacao = request.args.get('situacao', '')
    page = request.args.get('page', 1, type=int)

    # Obter usuário atual
    usuario_atual = Usuario.query.get(session['user_id'])

    # Aplicar filtro de escola baseado no usuário
    from utils.escola_utils import get_escolas_para_filtro

    query = Usuario.query

    # Se não for admin geral, filtrar apenas usuários da escola atual
    if not usuario_atual.is_admin_geral():
        escola_atual_id = usuario_atual.get_escola_atual_id()
        query = query.filter(Usuario.escola_id == escola_atual_id)
    # Admin Geral vê todos os usuários por padrão (sem filtro automático)

    if search:
        query = query.filter(
            db.or_(
                Usuario.nome.contains(search),
                Usuario.email.contains(search),
                Usuario.cpf.contains(search)
            )
        )

    if escola_id and usuario_atual.is_admin_geral():
        query = query.filter(Usuario.escola_id == escola_id)

    if perfil_id:
        query = query.filter(Usuario.perfil_id == perfil_id)

    if situacao:
        query = query.filter(Usuario.situacao == situacao)

    usuarios = query.paginate(page=page, per_page=10, error_out=False)

    escola_filtro = None
    if escola_id:
        escola_filtro = Escola.query.get(escola_id)

    perfil_filtro = None
    if perfil_id:
        perfil_filtro = Perfil.query.get(perfil_id)

    # Escolas disponíveis baseadas no perfil
    escolas = get_escolas_para_filtro(usuario_atual)
    perfis = Perfil.query.all()

    return render_template('usuarios/listar.html',
                         usuarios=usuarios,
                         search=search,
                         escola_filtro=escola_filtro,
                         perfil_filtro=perfil_filtro,
                         escolas=escolas,
                         perfis=perfis,
                         situacao=situacao)

@usuario_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastra novo usuário"""
    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.is_admin_escola():
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        cpf = request.form.get('cpf', '').strip()
        
        if not nome or not email:
            flash('Nome e email são obrigatórios!', 'error')
            return render_template('usuarios/cadastrar.html', 
                                 escolas=Escola.query.all(), 
                                 perfis=Perfil.query.all())

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado no sistema!', 'error')
            return render_template('usuarios/cadastrar.html', 
                                 escolas=Escola.query.all(), 
                                 perfis=Perfil.query.all())

        usuario = Usuario(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=request.form.get('telefone', '').strip(),
            escola_id=request.form.get('escola_id'),
            perfil_id=request.form.get('perfil_id'),
            situacao=request.form.get('situacao', 'ativo'),
            data_nascimento=datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date() if request.form.get('data_nascimento') else None
        )

        senha_padrao = request.form.get('senha', '123456')
        usuario.set_password(senha_padrao)

        try:
            db.session.add(usuario)
            db.session.flush()  # Para obter o ID do usuário

            # Processar upload da foto
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and foto.filename:
                    from controllers.foto_controller import allowed_file, resize_image
                    from werkzeug.utils import secure_filename
                    import os
                    import uuid

                    if allowed_file(foto.filename):
                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"user_{usuario.id}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar usuário com o nome da foto
                        usuario.set_foto(filename)

            db.session.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('usuario.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar usuário: {str(e)}', 'error')

    escolas = Escola.query.all()
    perfis = Perfil.query.all()
    return render_template('usuarios/cadastrar.html', escolas=escolas, perfis=perfis)

@usuario_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    """Visualiza detalhes do usuário"""
    usuario = Usuario.query.get_or_404(id)
    return render_template('usuarios/ver.html', usuario=usuario)

@usuario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita usuário"""
    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.is_admin_escola():
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))

    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nome = request.form.get('nome', '').strip()
        usuario.email = request.form.get('email', '').strip()
        usuario.cpf = request.form.get('cpf', '').strip()
        usuario.telefone = request.form.get('telefone', '').strip()
        usuario.escola_id = request.form.get('escola_id')
        usuario.perfil_id = request.form.get('perfil_id')
        usuario.situacao = request.form.get('situacao', 'ativo')
        
        if request.form.get('data_nascimento'):
            usuario.data_nascimento = datetime.strptime(request.form.get('data_nascimento'), '%Y-%m-%d').date()
        
        nova_senha = request.form.get('nova_senha', '').strip()
        if nova_senha:
            usuario.set_password(nova_senha)

        if not usuario.nome or not usuario.email:
            flash('Nome e email são obrigatórios!', 'error')
            return render_template('usuarios/editar.html',
                                 usuario=usuario,
                                 escolas=Escola.query.all(),
                                 perfis=Perfil.query.all())

        try:
            # Processar upload da foto
            if 'foto' in request.files:
                foto = request.files['foto']

                if foto and foto.filename:
                    from controllers.foto_controller import allowed_file, resize_image
                    import os
                    import uuid

                    if allowed_file(foto.filename):
                        # Remover foto anterior se existir
                        if usuario.foto:
                            old_photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos', usuario.foto)
                            if os.path.exists(old_photo_path):
                                try:
                                    os.remove(old_photo_path)
                                except:
                                    pass  # Não falhar se não conseguir remover

                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"user_{usuario.id}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar usuário com o nome da foto
                        usuario.set_foto(filename)

                        # Atualizar sessão se for o próprio usuário
                        if session.get('user_id') == usuario.id:
                            session['user_foto_url'] = usuario.get_foto_url()
                    else:
                        flash('Tipo de arquivo não permitido para foto!', 'error')

            db.session.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('usuario.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'error')

    escolas = Escola.query.all()
    perfis = Perfil.query.all()
    return render_template('usuarios/editar.html', 
                         usuario=usuario, 
                         escolas=escolas, 
                         perfis=perfis)

@usuario_bp.route('/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir(id):
    """Exclui usuário"""
    usuario_logado = Usuario.query.get(session['user_id'])
    usuario = Usuario.query.get_or_404(id)
    
    if usuario.id == usuario_logado.id:
        flash('Não é possível excluir seu próprio usuário!', 'error')
        return redirect(url_for('usuario.listar'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário "{usuario.nome}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir usuário: {str(e)}', 'error')

    return redirect(url_for('usuario.listar'))

@usuario_bp.route('/resetar-senha/<int:id>', methods=['POST'])
@login_required
def resetar_senha(id):
    """Reseta a senha do usuário"""
    from flask import jsonify

    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.is_admin_escola():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    usuario = Usuario.query.get_or_404(id)

    try:
        usuario.set_password('123456')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Senha resetada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@usuario_bp.route('/bloquear/<int:id>', methods=['POST'])
@login_required
def bloquear(id):
    """Bloqueia usuário"""
    from flask import jsonify

    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.is_admin_escola():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    usuario = Usuario.query.get_or_404(id)

    if usuario.id == usuario_logado.id:
        return jsonify({'success': False, 'message': 'Não é possível bloquear seu próprio usuário'}), 400

    try:
        usuario.situacao = 'bloqueado'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário bloqueado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@usuario_bp.route('/desbloquear/<int:id>', methods=['POST'])
@login_required
def desbloquear(id):
    """Desbloqueia usuário"""
    from flask import jsonify

    usuario_logado = Usuario.query.get(session['user_id'])
    if not usuario_logado.is_admin_escola():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

    usuario = Usuario.query.get_or_404(id)

    try:
        usuario.situacao = 'ativo'
        usuario.tentativas_login = 0  # Reset tentativas
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário desbloqueado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@usuario_bp.route('/perfil')
@login_required
def perfil():
    """Visualizar perfil do usuário logado"""
    usuario = Usuario.query.get_or_404(session['user_id'])
    return render_template('usuarios/perfil.html', usuario=usuario)

@usuario_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Editar perfil do usuário logado"""
    usuario = Usuario.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        try:
            # Campos que o usuário pode editar
            usuario.nome = request.form.get('nome')
            usuario.email = request.form.get('email')
            usuario.telefone = request.form.get('telefone')
            usuario.endereco = request.form.get('endereco')

            # Validar email único
            email_existente = Usuario.query.filter(
                Usuario.email == usuario.email,
                Usuario.id != usuario.id
            ).first()

            if email_existente:
                flash('Este email já está sendo usado por outro usuário!', 'error')
                return render_template('usuarios/editar_perfil.html', usuario=usuario)

            # Processar upload da foto
            if 'foto' in request.files:
                foto = request.files['foto']

                if foto and foto.filename:
                    from controllers.foto_controller import allowed_file, resize_image
                    import os
                    import uuid

                    if allowed_file(foto.filename):
                        # Remover foto anterior se existir
                        if usuario.foto:
                            old_photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos', usuario.foto)
                            if os.path.exists(old_photo_path):
                                try:
                                    os.remove(old_photo_path)
                                except:
                                    pass

                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"user_{usuario.id}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar usuário com o nome da foto
                        usuario.set_foto(filename)

                        # Atualizar sessão
                        session['user_foto_url'] = usuario.get_foto_url()
                    else:
                        flash('Tipo de arquivo não permitido para foto!', 'error')

            # Log da ação
            log_acao(AcoesAuditoria.USUARIO_EDITADO, 'Usuario', f'Perfil atualizado: {usuario.nome}')

            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('usuario.perfil'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')

    return render_template('usuarios/editar_perfil.html', usuario=usuario)

@usuario_bp.route('/trocar-escola', methods=['GET', 'POST'])
@login_required
def trocar_escola():
    """Permite ao Administrador Geral trocar de escola de trabalho"""
    from models import Escola

    # Verificar se o usuário pode trocar de escola
    usuario_atual = Usuario.query.get(session['user_id'])

    if not usuario_atual.can_switch_escola():
        flash('Você não tem permissão para trocar de escola!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nova_escola_id = request.form.get('escola_id')

        if not nova_escola_id:
            flash('Selecione uma escola!', 'error')
            return redirect(url_for('usuario.trocar_escola'))

        try:
            nova_escola_id = int(nova_escola_id)
            nova_escola = Escola.query.get(nova_escola_id)

            if not nova_escola:
                flash('Escola não encontrada!', 'error')
                return redirect(url_for('usuario.trocar_escola'))

            if not usuario_atual.can_access_escola(nova_escola_id):
                flash('Você não tem acesso a esta escola!', 'error')
                return redirect(url_for('usuario.trocar_escola'))

            # Atualizar escola atual na sessão
            session['escola_atual_id'] = nova_escola_id
            session['escola_atual_nome'] = nova_escola.nome

            # Log da ação
            from utils.logs import log_acao, AcoesAuditoria
            log_acao(AcoesAuditoria.ALTERACAO, 'Usuario',
                    f'Trocou escola de trabalho para: {nova_escola.nome}')

            flash(f'Escola alterada para: {nova_escola.nome}', 'success')
            return redirect(url_for('dashboard'))

        except ValueError:
            flash('ID de escola inválido!', 'error')
        except Exception as e:
            flash(f'Erro ao trocar escola: {str(e)}', 'error')

    # Buscar escolas acessíveis
    escolas = usuario_atual.get_escolas_acessiveis()
    escola_atual_id = session.get('escola_atual_id', usuario_atual.escola_id)

    return render_template('usuarios/trocar_escola.html',
                         escolas=escolas,
                         escola_atual_id=escola_atual_id,
                         usuario=usuario_atual)

@usuario_bp.route('/perfil/senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário logado"""
    if request.method == 'POST':
        usuario = Usuario.query.get_or_404(session['user_id'])

        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Verificar senha atual
        if not usuario.check_password(senha_atual):
            flash('Senha atual incorreta!', 'error')
            return render_template('usuarios/alterar_senha.html')

        # Verificar se as senhas coincidem
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return render_template('usuarios/alterar_senha.html')

        # Validar tamanho da senha
        if len(nova_senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('usuarios/alterar_senha.html')

        try:
            # Atualizar senha
            usuario.set_password(nova_senha)

            # Log da ação
            log_acao(AcoesAuditoria.USUARIO_EDITADO, 'Usuario', f'Senha alterada: {usuario.nome}')

            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('usuario.perfil'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'error')

    return render_template('usuarios/alterar_senha.html')
