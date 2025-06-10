# controllers/diretor_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Diretor
from controllers.auth_controller import login_required
from utils.permissions import require_permission, Modulos, Acoes
from datetime import datetime
import re

diretor_bp = Blueprint('diretor', __name__, url_prefix='/diretores')

@diretor_bp.route('/')
@login_required
@require_permission(Modulos.DIRETOR, Acoes.VISUALIZAR)
def index():
    """Lista todos os diretores"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    # Query base
    query = Diretor.query
    
    # Aplicar filtros
    if search:
        query = query.filter(
            db.or_(
                Diretor.nome.contains(search),
                Diretor.cpf.contains(search),
                Diretor.cidade.contains(search),
                Diretor.tipo_mandato.contains(search)
            )
        )
    
    if status_filter:
        query = query.filter(Diretor.status == status_filter)
    
    # Ordenação e paginação
    diretores = query.order_by(Diretor.nome).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Estatísticas
    stats = {
        'total': Diretor.query.count(),
        'ativos': Diretor.query.filter_by(status='ativo').count(),
        'inativos': Diretor.query.filter(Diretor.status != 'ativo').count()
    }
    
    return render_template('diretores/index.html', 
                         diretores=diretores, 
                         search=search,
                         status_filter=status_filter,
                         stats=stats)

@diretor_bp.route('/criar', methods=['GET', 'POST'])
@login_required
@require_permission(Modulos.DIRETOR, Acoes.CRIAR)
def criar():
    """Criar novo diretor"""
    if request.method == 'POST':
        try:
            # Validar dados
            nome = request.form.get('nome', '').strip()
            cpf = request.form.get('cpf', '').strip()
            
            if not nome:
                flash('Nome é obrigatório', 'error')
                return render_template('diretores/form.html', 
                                     diretor=None, 
                                     tipos_mandato=Diretor.get_tipos_mandato(),
                                     status_options=Diretor.get_status_options())
            
            # Verificar CPF único
            if cpf:
                cpf_limpo = re.sub(r'[^\d]', '', cpf)
                if Diretor.query.filter_by(cpf=cpf_limpo).first():
                    flash('CPF já cadastrado', 'error')
                    return render_template('diretores/form.html', 
                                         diretor=None,
                                         tipos_mandato=Diretor.get_tipos_mandato(),
                                         status_options=Diretor.get_status_options())
            
            # Criar diretor
            diretor = Diretor(
                nome=nome,
                endereco=request.form.get('endereco', '').strip(),
                celular=request.form.get('celular', '').strip(),
                cidade=request.form.get('cidade', '').strip(),
                cpf=re.sub(r'[^\d]', '', cpf) if cpf else None,
                status=request.form.get('status', 'ativo'),
                tipo_mandato=request.form.get('tipo_mandato', '').strip()
            )
            
            # Data de admissão
            admissao_str = request.form.get('admissao')
            if admissao_str:
                try:
                    diretor.admissao = datetime.strptime(admissao_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de admissão inválida', 'error')
                    return render_template('diretores/form.html', 
                                         diretor=None,
                                         tipos_mandato=Diretor.get_tipos_mandato(),
                                         status_options=Diretor.get_status_options())
            
            # Validar CPF
            if not diretor.validate_cpf():
                flash('CPF inválido', 'error')
                return render_template('diretores/form.html', 
                                     diretor=None,
                                     tipos_mandato=Diretor.get_tipos_mandato(),
                                     status_options=Diretor.get_status_options())
            
            db.session.add(diretor)
            db.session.flush()  # Para obter o ID do diretor

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
                        filename = f"diretor_{diretor.id_diretor}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join('static', 'uploads', 'diretores')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar diretor com o nome da foto
                        diretor.set_foto(filename)

            db.session.commit()

            flash(f'Diretor "{diretor.nome}" criado com sucesso!', 'success')
            return redirect(url_for('diretor.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar diretor: {e}', 'error')
    
    return render_template('diretores/form.html', 
                         diretor=None,
                         tipos_mandato=Diretor.get_tipos_mandato(),
                         status_options=Diretor.get_status_options())

@diretor_bp.route('/<int:id_diretor>')
@login_required
@require_permission(Modulos.DIRETOR, Acoes.VISUALIZAR)
def detalhes(id_diretor):
    """Visualizar detalhes do diretor"""
    diretor = Diretor.query.get_or_404(id_diretor)
    return render_template('diretores/detalhes.html', diretor=diretor)

@diretor_bp.route('/<int:id_diretor>/editar', methods=['GET', 'POST'])
@login_required
@require_permission(Modulos.DIRETOR, Acoes.EDITAR)
def editar(id_diretor):
    """Editar diretor"""
    diretor = Diretor.query.get_or_404(id_diretor)
    
    if request.method == 'POST':
        try:
            # Validar dados
            nome = request.form.get('nome', '').strip()
            cpf = request.form.get('cpf', '').strip()
            
            if not nome:
                flash('Nome é obrigatório', 'error')
                return render_template('diretores/form.html', 
                                     diretor=diretor,
                                     tipos_mandato=Diretor.get_tipos_mandato(),
                                     status_options=Diretor.get_status_options())
            
            # Verificar CPF único (exceto o próprio)
            if cpf:
                cpf_limpo = re.sub(r'[^\d]', '', cpf)
                existing = Diretor.query.filter(
                    Diretor.cpf == cpf_limpo,
                    Diretor.id_diretor != id_diretor
                ).first()
                if existing:
                    flash('CPF já cadastrado por outro diretor', 'error')
                    return render_template('diretores/form.html', 
                                         diretor=diretor,
                                         tipos_mandato=Diretor.get_tipos_mandato(),
                                         status_options=Diretor.get_status_options())
            
            # Atualizar dados
            diretor.nome = nome
            diretor.endereco = request.form.get('endereco', '').strip()
            diretor.celular = request.form.get('celular', '').strip()
            diretor.cidade = request.form.get('cidade', '').strip()
            diretor.cpf = re.sub(r'[^\d]', '', cpf) if cpf else None
            diretor.status = request.form.get('status', 'ativo')
            diretor.tipo_mandato = request.form.get('tipo_mandato', '').strip()
            
            # Data de admissão
            admissao_str = request.form.get('admissao')
            if admissao_str:
                try:
                    diretor.admissao = datetime.strptime(admissao_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de admissão inválida', 'error')
                    return render_template('diretores/form.html', 
                                         diretor=diretor,
                                         tipos_mandato=Diretor.get_tipos_mandato(),
                                         status_options=Diretor.get_status_options())
            else:
                diretor.admissao = None
            
            # Validar CPF
            if not diretor.validate_cpf():
                flash('CPF inválido', 'error')
                return render_template('diretores/form.html',
                                     diretor=diretor,
                                     tipos_mandato=Diretor.get_tipos_mandato(),
                                     status_options=Diretor.get_status_options())

            # Processar upload da foto
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto and foto.filename:
                    from controllers.foto_controller import allowed_file, resize_image
                    import os
                    import uuid

                    if allowed_file(foto.filename):
                        # Remover foto anterior se existir
                        if diretor.foto:
                            old_photo_path = os.path.join('static', 'uploads', 'diretores', diretor.foto)
                            if os.path.exists(old_photo_path):
                                try:
                                    os.remove(old_photo_path)
                                except:
                                    pass

                        # Gerar nome único para o arquivo
                        file_extension = foto.filename.rsplit('.', 1)[1].lower()
                        filename = f"diretor_{diretor.id_diretor}_{uuid.uuid4().hex[:8]}.{file_extension}"

                        # Definir caminho para salvar
                        upload_folder = os.path.join('static', 'uploads', 'diretores')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, filename)

                        # Salvar arquivo
                        foto.save(file_path)

                        # Redimensionar imagem
                        resize_image(file_path)

                        # Atualizar diretor com o nome da foto
                        diretor.set_foto(filename)

            db.session.commit()

            flash(f'Diretor "{diretor.nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('diretor.detalhes', id_diretor=diretor.id_diretor))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar diretor: {e}', 'error')
    
    return render_template('diretores/form.html', 
                         diretor=diretor,
                         tipos_mandato=Diretor.get_tipos_mandato(),
                         status_options=Diretor.get_status_options())

@diretor_bp.route('/<int:id_diretor>/excluir', methods=['POST'])
@login_required
@require_permission(Modulos.DIRETOR, Acoes.EXCLUIR)
def excluir(id_diretor):
    """Excluir diretor"""
    try:
        diretor = Diretor.query.get_or_404(id_diretor)
        nome = diretor.nome
        
        db.session.delete(diretor)
        db.session.commit()
        
        flash(f'Diretor "{nome}" excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir diretor: {e}', 'error')
    
    return redirect(url_for('diretor.index'))

@diretor_bp.route('/api/buscar')
@login_required
@require_permission(Modulos.DIRETOR, Acoes.VISUALIZAR)
def api_buscar():
    """API para buscar diretores"""
    search = request.args.get('q', '')
    
    if len(search) < 2:
        return jsonify([])
    
    diretores = Diretor.query.filter(
        db.or_(
            Diretor.nome.contains(search),
            Diretor.cpf.contains(search)
        )
    ).filter_by(status='ativo').limit(10).all()
    
    return jsonify([{
        'id': d.id_diretor,
        'nome': d.nome,
        'cpf': d.format_cpf(),
        'tipo_mandato': d.tipo_mandato,
        'cidade': d.cidade
    } for d in diretores])

@diretor_bp.route('/relatorio')
@login_required
@require_permission(Modulos.DIRETOR, Acoes.VISUALIZAR)
def relatorio():
    """Relatório de diretores"""
    # Estatísticas gerais
    stats = {
        'total': Diretor.query.count(),
        'ativos': Diretor.query.filter_by(status='ativo').count(),
        'inativos': Diretor.query.filter(Diretor.status != 'ativo').count(),
        'por_tipo': {}
    }
    
    # Diretores por tipo de mandato
    from sqlalchemy import func
    tipos = db.session.query(
        Diretor.tipo_mandato,
        func.count(Diretor.id_diretor)
    ).group_by(Diretor.tipo_mandato).all()
    
    for tipo, count in tipos:
        if tipo:
            stats['por_tipo'][tipo] = count
    
    # Diretores recentes
    recentes = Diretor.query.order_by(Diretor.data_cadastro.desc()).limit(10).all()
    
    return render_template('diretores/relatorio.html', 
                         stats=stats, 
                         recentes=recentes)
