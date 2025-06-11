# controllers/dossie_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, Dossie, Escola, Usuario
from utils.logs import log_acao, AcoesAuditoria
from .auth_controller import login_required

dossie_bp = Blueprint('dossie', __name__, url_prefix='/dossies')

@dossie_bp.route('/')
@login_required
def listar():
    """Lista dossiês"""
    search = request.args.get('search', '')
    escola_id = request.args.get('escola', '')
    situacao = request.args.get('situacao', '')
    ano = request.args.get('ano', '')
    page = request.args.get('page', 1, type=int)

    # Verificar permissões
    usuario = Usuario.query.get(session['user_id'])
    query = Dossie.query

    # Usar escola atual da sessão (para Admin Geral) ou escola do usuário
    escola_atual_id = session.get('escola_atual_id', usuario.escola_id)

    # Se não for admin geral, filtrar apenas dossiês da escola do usuário
    if not usuario.is_admin_geral():
        query = query.filter(Dossie.escola_id == usuario.escola_id)
    else:
        # Admin Geral vê dossiês da escola atual selecionada
        if escola_atual_id:
            query = query.filter(Dossie.escola_id == escola_atual_id)
    
    if search:
        query = query.filter(
            db.or_(
                Dossie.numero_dossie.contains(search),
                Dossie.nome_aluno.contains(search),
                Dossie.cpf_aluno.contains(search),
                Dossie.nome_mae.contains(search),
                Dossie.nome_pai.contains(search)
            )
        )
    
    if escola_id and usuario.is_admin_geral():
        query = query.filter(Dossie.escola_id == escola_id)
    
    if situacao:
        query = query.filter(Dossie.status == situacao)
    
    if ano:
        query = query.filter(
            db.or_(
                Dossie.ano_ingresso == int(ano),
                Dossie.ano_conclusao == int(ano)
            )
        )

    dossies = query.paginate(page=page, per_page=15, error_out=False)

    escola_filtro = None
    if escola_id:
        escola_filtro = Escola.query.get(escola_id)

    escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]

    return render_template('dossies/listar.html', 
                         dossies=dossies, 
                         search=search, 
                         escola_filtro=escola_filtro,
                         escolas=escolas,
                         situacao=situacao,
                         ano=ano)

@dossie_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastra novo dossiê"""
    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        n_dossie = request.form.get('n_dossie', '').strip()
        nome = request.form.get('nome', '').strip()

        if not n_dossie or not nome:
            flash('Número do dossiê e nome do aluno são obrigatórios!', 'error')
            escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]
            return render_template('dossies/novo.html', escolas=escolas)

        # Verificar se número do dossiê já existe
        if Dossie.query.filter_by(n_dossie=n_dossie).first():
            flash('Número de dossiê já existe no sistema!', 'error')
            escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]
            return render_template('dossies/novo.html', escolas=escolas)

        # Para Admin Geral, usar escola atual da sessão ou permitir seleção
        if usuario.is_admin_geral():
            id_escola = request.form.get('id_escola') or session.get('escola_atual_id', usuario.escola_id)
        else:
            id_escola = usuario.escola_id

        dossie = Dossie(
            n_dossie=n_dossie,
            nome=nome,
            cpf=request.form.get('cpf', '').strip(),
            n_mae=request.form.get('n_mae', '').strip(),
            n_pai=request.form.get('n_pai', '').strip(),
            id_escola=id_escola,
            ano=int(request.form.get('ano')) if request.form.get('ano') else None,
            status=request.form.get('status', 'ativo'),
            local=request.form.get('local', '').strip(),
            pasta=request.form.get('pasta', '').strip(),
            tipo_documento=request.form.get('tipo_documento', '').strip(),
            observacao=request.form.get('observacao', '').strip(),
            usuario_cadastro_id=usuario.id
        )

        try:
            db.session.add(dossie)
            db.session.flush()  # Para obter o ID do dossiê

            # Processar upload da foto
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and foto.filename:
                    from controllers.foto_controller import allowed_file, resize_image
                    import os
                    import uuid

                    if allowed_file(foto.filename):
                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"dossie_{dossie.id_dossie}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join('static', 'uploads', 'dossies')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar dossiê com o nome da foto
                        dossie.set_foto(filename)

            db.session.commit()

            # Processar anexos se houver (método simplificado)
            anexos_enviados = 0

            # Verificar se há arquivos de anexo
            files = request.files.getlist('anexos_files[]')
            nomes_personalizados = request.form.getlist('anexos_nomes[]')

            if files and len(files) > 0 and files[0].filename:
                from models import Anexo
                import os
                from werkzeug.utils import secure_filename

                # Criar pasta de upload se não existir
                upload_folder = 'uploads/anexos'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                for i, file in enumerate(files):
                    if file and file.filename:
                        nome_personalizado = nomes_personalizados[i] if i < len(nomes_personalizados) else ''

                        # Gerar nome seguro
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename

                        # Salvar arquivo
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)

                        # Salvar no banco
                        anexo = Anexo(
                            dossie_id=dossie.id_dossie,
                            nome=file.filename,
                            nome_personalizado=nome_personalizado if nome_personalizado else None,
                            caminho=filepath,
                            tamanho=os.path.getsize(filepath),
                            tipo_arquivo=filename.rsplit('.', 1)[1].lower() if '.' in filename else None,
                            usuario_upload_id=usuario.id
                        )
                        db.session.add(anexo)
                        anexos_enviados += 1

                db.session.commit()

            if anexos_enviados > 0:
                flash(f'Dossiê cadastrado com sucesso! {anexos_enviados} anexo(s) enviado(s).', 'success')
            else:
                flash('Dossiê cadastrado com sucesso!', 'success')

            return redirect(url_for('dossie.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar dossiê: {str(e)}', 'error')

    escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]
    return render_template('dossies/novo.html', escolas=escolas)

@dossie_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    """Visualiza detalhes do dossiê"""
    usuario = Usuario.query.get(session['user_id'])
    dossie = Dossie.query.get_or_404(id)
    
    # Verificar se usuário pode acessar este dossiê
    if not usuario.can_access_escola(dossie.escola_id):
        flash('Acesso negado a este dossiê.', 'error')
        return redirect(url_for('dossie.listar'))

    # Registrar log de visualização
    log_acao(AcoesAuditoria.DOSSIE_VISUALIZADO, 'Dossie', f'Dossiê visualizado: {dossie.numero_dossie} - {dossie.nome_aluno}')

    return render_template('dossies/ver.html', dossie=dossie)

@dossie_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita dossiê"""
    usuario = Usuario.query.get(session['user_id'])
    dossie = Dossie.query.get_or_404(id)
    
    # Verificar se usuário pode editar este dossiê
    if not usuario.can_access_escola(dossie.escola_id):
        flash('Acesso negado a este dossiê.', 'error')
        return redirect(url_for('dossie.listar'))

    if request.method == 'POST':
        dossie.n_dossie = request.form.get('n_dossie', '').strip()
        dossie.nome = request.form.get('nome', '').strip()
        dossie.cpf = request.form.get('cpf', '').strip()
        dossie.n_mae = request.form.get('n_mae', '').strip()
        dossie.n_pai = request.form.get('n_pai', '').strip()
        dossie.ano = int(request.form.get('ano')) if request.form.get('ano') else None
        dossie.status = request.form.get('status', 'ativo')
        dossie.local = request.form.get('local', '').strip()
        dossie.pasta = request.form.get('pasta', '').strip()
        dossie.tipo_documento = request.form.get('tipo_documento', '').strip()
        dossie.observacao = request.form.get('observacao', '').strip()

        # Atualizar escola se usuário for admin geral
        if usuario.is_admin_geral():
            dossie.id_escola = request.form.get('id_escola', type=int)

        if not dossie.n_dossie or not dossie.nome:
            flash('Número do dossiê e nome do aluno são obrigatórios!', 'error')
            escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]
            return render_template('dossies/editar.html', dossie=dossie, escolas=escolas)

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
                        if dossie.foto:
                            old_photo_path = os.path.join('static', 'uploads', 'dossies', dossie.foto)
                            if os.path.exists(old_photo_path):
                                try:
                                    os.remove(old_photo_path)
                                except:
                                    pass

                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"dossie_{dossie.id_dossie}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join('static', 'uploads', 'dossies')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar dossiê com o nome da foto
                        dossie.set_foto(filename)

            db.session.commit()
            flash('Dossiê atualizado com sucesso!', 'success')
            return redirect(url_for('dossie.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar dossiê: {str(e)}', 'error')

    escolas = Escola.query.all() if usuario.is_admin_geral() else [usuario.escola]
    return render_template('dossies/editar.html', dossie=dossie, escolas=escolas)

@dossie_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    """Exclui dossiê"""
    usuario = Usuario.query.get(session['user_id'])
    dossie = Dossie.query.get_or_404(id)
    
    # Verificar se usuário pode excluir este dossiê
    if not usuario.can_access_escola(dossie.escola_id) or not usuario.is_admin_escola():
        flash('Acesso negado para excluir este dossiê.', 'error')
        return redirect(url_for('dossie.listar'))

    try:
        db.session.delete(dossie)
        db.session.commit()
        flash(f'Dossiê "{dossie.n_dossie}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir dossiê: {str(e)}', 'error')

    return redirect(url_for('dossie.listar'))
