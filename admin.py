#!/usr/bin/env python3
# admin.py - Área de administração Flask (similar ao Django Admin)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Usuario, Escola, Dossie, Anexo, Perfil, Cidade, Movimentacao, Diretor, Permissao, PerfilPermissao
from controllers.auth_controller import login_required
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso negado. Faça login.', 'error')
            return redirect(url_for('auth.login'))
        
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or not usuario.is_admin_geral():
            flash('Acesso negado. Apenas administradores.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Dashboard administrativo"""
    # Estatísticas gerais
    stats = {
        'usuarios': Usuario.query.count(),
        'escolas': Escola.query.count(),
        'dossies': Dossie.query.count(),
        'anexos': Anexo.query.count(),
        'perfis': Perfil.query.count(),
        'cidades': Cidade.query.count(),
        'movimentacoes': Movimentacao.query.count()
    }
    
    # Atividades recentes
    usuarios_recentes = Usuario.query.order_by(Usuario.data_cadastro.desc()).limit(5).all()
    dossies_recentes = Dossie.query.order_by(Dossie.dt_cadastro.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                         stats=stats, 
                         usuarios_recentes=usuarios_recentes,
                         dossies_recentes=dossies_recentes)

@admin_bp.route('/models')
@login_required
@admin_required
def models():
    """Lista todos os modelos disponíveis"""
    models_info = [
        {
            'name': 'Usuario',
            'verbose_name': 'Usuários',
            'count': Usuario.query.count(),
            'url': url_for('admin.model_list', model='usuario'),
            'icon': 'fas fa-users'
        },
        {
            'name': 'Escola',
            'verbose_name': 'Escolas',
            'count': Escola.query.count(),
            'url': url_for('admin.model_list', model='escola'),
            'icon': 'fas fa-school'
        },
        {
            'name': 'Diretor',
            'verbose_name': 'Diretores',
            'count': Diretor.query.count(),
            'url': url_for('admin.model_list', model='diretor'),
            'icon': 'fas fa-user-tie'
        },
        {
            'name': 'Dossie',
            'verbose_name': 'Dossiês',
            'count': Dossie.query.count(),
            'url': url_for('admin.model_list', model='dossie'),
            'icon': 'fas fa-folder'
        },
        {
            'name': 'Anexo',
            'verbose_name': 'Anexos',
            'count': Anexo.query.count(),
            'url': url_for('admin.model_list', model='anexo'),
            'icon': 'fas fa-paperclip'
        },
        {
            'name': 'Perfil',
            'verbose_name': 'Perfis',
            'count': Perfil.query.count(),
            'url': url_for('admin.model_list', model='perfil'),
            'icon': 'fas fa-user-tag'
        },
        {
            'name': 'Cidade',
            'verbose_name': 'Cidades',
            'count': Cidade.query.count(),
            'url': url_for('admin.model_list', model='cidade'),
            'icon': 'fas fa-map-marker-alt'
        },
        {
            'name': 'Movimentacao',
            'verbose_name': 'Movimentações',
            'count': Movimentacao.query.count(),
            'url': url_for('admin.model_list', model='movimentacao'),
            'icon': 'fas fa-exchange-alt'
        },
        {
            'name': 'Permissao',
            'verbose_name': 'Permissões',
            'count': Permissao.query.count(),
            'url': url_for('admin.model_list', model='permissao'),
            'icon': 'fas fa-shield-alt'
        },
        {
            'name': 'PerfilPermissao',
            'verbose_name': 'Perfil-Permissão',
            'count': PerfilPermissao.query.count(),
            'url': url_for('admin.model_list', model='perfil_permissao'),
            'icon': 'fas fa-link'
        }
    ]
    
    return render_template('admin/models.html', models=models_info)

@admin_bp.route('/model/<model>')
@login_required
@admin_required
def model_list(model):
    """Lista registros de um modelo"""
    model_map = {
        'usuario': Usuario,
        'escola': Escola,
        'diretor': Diretor,
        'dossie': Dossie,
        'anexo': Anexo,
        'perfil': Perfil,
        'cidade': Cidade,
        'movimentacao': Movimentacao,
        'permissao': Permissao,
        'perfil_permissao': PerfilPermissao
    }
    
    if model not in model_map:
        flash('Modelo não encontrado', 'error')
        return redirect(url_for('admin.models'))
    
    Model = model_map[model]
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Busca
    search = request.args.get('search', '')
    if search:
        # Busca simples por nome (adaptar conforme modelo)
        if hasattr(Model, 'nome'):
            objects = Model.query.filter(Model.nome.contains(search))
        elif hasattr(Model, 'email'):
            objects = Model.query.filter(Model.email.contains(search))
        else:
            objects = Model.query
    else:
        objects = Model.query
    
    # Ordenação
    try:
        if hasattr(Model, 'data_cadastro') and hasattr(Model.data_cadastro, 'desc'):
            objects = objects.order_by(Model.data_cadastro.desc())
        elif hasattr(Model, 'dt_cadastro') and hasattr(Model.dt_cadastro, 'desc'):
            objects = objects.order_by(Model.dt_cadastro.desc())
        elif hasattr(Model, 'id') and hasattr(Model.id, 'desc'):
            objects = objects.order_by(Model.id.desc())
        elif hasattr(Model, 'id_perfil') and hasattr(Model.id_perfil, 'desc'):
            objects = objects.order_by(Model.id_perfil.desc())
        elif hasattr(Model, 'id_cidade') and hasattr(Model.id_cidade, 'desc'):
            objects = objects.order_by(Model.id_cidade.desc())
        else:
            # Ordenação padrão sem desc() para evitar erros
            pass
    except AttributeError:
        # Se der erro, não ordena
        pass
    
    pagination = objects.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/model_list.html', 
                         model=model,
                         Model=Model,
                         objects=pagination.items,
                         pagination=pagination,
                         search=search)

@admin_bp.route('/model/<model>/<int:object_id>')
@login_required
@admin_required
def model_detail(model, object_id):
    """Detalhes de um registro"""
    model_map = {
        'usuario': Usuario,
        'escola': Escola,
        'diretor': Diretor,
        'dossie': Dossie,
        'anexo': Anexo,
        'perfil': Perfil,
        'cidade': Cidade,
        'movimentacao': Movimentacao,
        'permissao': Permissao,
        'perfil_permissao': PerfilPermissao
    }
    
    if model not in model_map:
        flash('Modelo não encontrado', 'error')
        return redirect(url_for('admin.models'))
    
    Model = model_map[model]

    # Buscar objeto com tratamento de diferentes tipos de ID
    try:
        if model == 'perfil':
            obj = Model.query.filter_by(id_perfil=object_id).first_or_404()
        elif model == 'cidade':
            obj = Model.query.filter_by(id_cidade=object_id).first_or_404()
        else:
            obj = Model.query.get_or_404(object_id)
    except Exception:
        # Fallback para busca genérica
        obj = Model.query.filter_by(id=object_id).first_or_404()
    
    return render_template('admin/model_detail.html', 
                         model=model,
                         Model=Model,
                         object=obj)

@admin_bp.route('/system-info')
@login_required
@admin_required
def system_info():
    """Informações do sistema"""
    import platform

    # Informações do sistema
    system_info = {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'processor': platform.processor() or 'N/A',
    }

    # Tentar usar psutil se disponível
    try:
        import psutil
        system_info.update({
            'memory_total': f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            'memory_available': f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
            'disk_usage': f"{psutil.disk_usage('/').percent:.1f}%"
        })
    except ImportError:
        system_info.update({
            'memory_total': 'N/A',
            'memory_available': 'N/A',
            'disk_usage': 'N/A'
        })
    
    # Informações do banco
    from flask import current_app
    db_info = {
        'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else current_app.config.get('SQLALCHEMY_DATABASE_URI', ''),
        'total_tables': len(db.metadata.tables),
        'migrations_folder': 'migrations' if os.path.exists('migrations') else 'Não configurado'
    }
    
    return render_template('admin/system_info.html', 
                         system_info=system_info,
                         db_info=db_info)

@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """Visualizar logs do sistema"""
    log_files = []
    
    # Procurar arquivos de log
    for file in os.listdir('.'):
        if file.endswith('.log'):
            log_files.append({
                'name': file,
                'size': os.path.getsize(file),
                'modified': datetime.fromtimestamp(os.path.getmtime(file))
            })
    
    return render_template('admin/logs.html', log_files=log_files)

@admin_bp.route('/backup')
@login_required
@admin_required
def backup():
    """Página de backup"""
    backup_files = []
    
    # Listar backups existentes
    for file in os.listdir('.'):
        if file.startswith('backup_'):
            backup_files.append({
                'name': file,
                'size': os.path.getsize(file),
                'created': datetime.fromtimestamp(os.path.getctime(file))
            })
    
    return render_template('admin/backup.html', backup_files=backup_files)

@admin_bp.route('/create-backup', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Criar backup do banco"""
    try:
        import subprocess
        import os

        # Usar o script de backup funcional
        result = subprocess.run(['python', 'simple_backup.py'],
                              capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            # Extrair nome do arquivo do output
            output_lines = result.stdout.split('\n')
            backup_file = None
            for line in output_lines:
                if 'Arquivo salvo:' in line:
                    backup_file = line.split(':')[-1].strip()
                    break

            if backup_file:
                flash(f'Backup criado com sucesso: {backup_file}', 'success')
            else:
                flash('Backup criado com sucesso!', 'success')
        else:
            flash(f'Erro ao criar backup: {result.stderr}', 'error')

    except Exception as e:
        flash(f'Erro ao executar backup: {str(e)}', 'error')

    return redirect(url_for('admin.backup'))

# Função removida - usando simple_backup.py

# Registrar blueprint no app principal
def init_admin(app):
    """Inicializar área de admin"""
    app.register_blueprint(admin_bp)
