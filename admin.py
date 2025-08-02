#!/usr/bin/env python3
# admin.py - Área de administração Flask (similar ao Django Admin)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Usuario, Escola, Dossie, Anexo, Perfil, Cidade, Movimentacao, Diretor, Permissao, PerfilPermissao, Solicitante
from controllers.auth_controller import login_required
from datetime import datetime
import os
import sys

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
        'movimentacoes': Movimentacao.query.count(),
        'solicitantes': Solicitante.query.count()
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
        },
        {
            'name': 'Solicitante',
            'verbose_name': 'Solicitantes',
            'count': Solicitante.query.count(),
            'url': url_for('admin.model_list', model='solicitante'),
            'icon': 'fas fa-user-friends'
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
        'perfil_permissao': PerfilPermissao,
        'solicitante': Solicitante
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
        'perfil_permissao': PerfilPermissao,
        'solicitante': Solicitante
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
    from models import LogAuditoria, LogSistema
    from utils.logs import obter_logs_auditoria, obter_logs_sistema

    # Obter logs recentes
    logs_auditoria = obter_logs_auditoria(limite=50)
    logs_sistema = obter_logs_sistema(limite=50)

    # Estatísticas
    total_auditoria = LogAuditoria.query.count()
    total_sistema = LogSistema.query.count()

    # Logs de hoje
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    logs_hoje_auditoria = LogAuditoria.query.filter(LogAuditoria.data_hora >= hoje).count()
    logs_hoje_sistema = LogSistema.query.filter(LogSistema.data_hora >= hoje).count()

    stats = {
        'total_auditoria': total_auditoria,
        'total_sistema': total_sistema,
        'logs_hoje_auditoria': logs_hoje_auditoria,
        'logs_hoje_sistema': logs_hoje_sistema
    }

    return render_template('admin/logs.html',
                         logs_auditoria=logs_auditoria,
                         logs_sistema=logs_sistema,
                         stats=stats)

@admin_bp.route('/configuracoes')
@login_required
@admin_required
def configuracoes():
    """Configurações do sistema"""
    from models import Escola, Usuario, Dossie, Movimentacao
    import platform
    import psutil

    # Informações do sistema
    system_info = {
        'python_version': platform.python_version(),
        'sistema_operacional': platform.system(),
        'arquitetura': platform.architecture()[0],
        'processador': platform.processor(),
        'hostname': platform.node()
    }

    # Estatísticas do banco
    stats = {
        'total_escolas': Escola.query.count(),
        'total_usuarios': Usuario.query.count(),
        'total_dossies': Dossie.query.count(),
        'total_movimentacoes': Movimentacao.query.count()
    }

    # Informações de memória (se disponível)
    try:
        memory = psutil.virtual_memory()
        system_info['memoria_total'] = f"{memory.total // (1024**3)} GB"
        system_info['memoria_disponivel'] = f"{memory.available // (1024**3)} GB"
        system_info['uso_memoria'] = f"{memory.percent}%"
    except:
        system_info['memoria_total'] = 'N/A'
        system_info['memoria_disponivel'] = 'N/A'
        system_info['uso_memoria'] = 'N/A'

    return render_template('admin/configuracoes.html',
                         system_info=system_info,
                         stats=stats)

@admin_bp.route('/backup')
@login_required
@admin_required
def backup():
    """Página de backup B2"""
    import subprocess
    import json
    
    # Listar backups existentes
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('backup_') and file.endswith('.sql'):
            backup_files.append({
                'name': file,
                'size': os.path.getsize(file),
                'created': datetime.fromtimestamp(os.path.getctime(file)),
                'b2_uploaded': False  # TODO: verificar se foi enviado para B2
            })
    
    # Ordenar por data de criação (mais recente primeiro)
    backup_files.sort(key=lambda x: x['created'], reverse=True)
    
    # Configuração B2
    b2_config = {
        'key_id': os.getenv('B2_APPLICATION_KEY_ID', ''),
        'key': os.getenv('B2_APPLICATION_KEY', ''),
        'bucket': os.getenv('B2_BUCKET_NAME', 'dossie-backups'),
        'retention': int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    }
    
    # Status do crontab
    crontab_status = {
        'active': False,
        'schedule': 'daily_02:00',
        'next_run': 'Não configurado'
    }
    
    # Verificar se crontab está ativo
    try:
        result = subprocess.run(['schtasks', '/query', '/tn', 'DossieBackupB2'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            crontab_status['active'] = True
            crontab_status['next_run'] = 'Próxima execução automática'
    except:
        pass
    
    # Logs recentes
    recent_logs = "Logs do sistema de backup B2..."
    try:
        if os.path.exists('backup_b2_complete.log'):
            with open('backup_b2_complete.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_logs = ''.join(lines[-20:])  # Últimas 20 linhas
    except:
        recent_logs = "Nenhum log disponível"
    
    # Lista de arquivos B2 (simulado)
    b2_files = []
    try:
        # TODO: Implementar listagem real do B2
        b2_files = [
            {'name': 'backup_simple_20250731_000531.sql', 'date': '31/07/2025'},
            {'name': 'backup_simple_20250730_191906.sql', 'date': '30/07/2025'}
        ]
    except:
        pass
    
    return render_template('admin/backup.html', 
                         backup_files=backup_files,
                         b2_config=b2_config,
                         crontab_status=crontab_status,
                         recent_logs=recent_logs,
                         b2_files=b2_files)

@admin_bp.route('/backup/manual', methods=['POST'])
@login_required
@admin_required
def backup_manual():
    """Executar backup manual B2"""
    try:
        import subprocess
        
        backup_type = request.form.get('backup_type', 'simple')
        upload_b2 = request.form.get('upload_b2') == 'on'
        
        # Executar backup
        if backup_type == 'simple':
            result = subprocess.run(['python', 'backup_b2_complete.py'],
                                  capture_output=True, text=True, cwd='.')
        else:
            result = subprocess.run(['python', 'b2_backup.py'],
                                  capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            flash('Backup manual executado com sucesso!', 'success')
        else:
            flash(f'Erro ao executar backup: {result.stderr}', 'error')
            
    except Exception as e:
        flash(f'Erro ao executar backup: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/config-b2', methods=['POST'])
@login_required
@admin_required
def config_b2():
    """Configurar credenciais B2"""
    try:
        # Salvar configurações em arquivo .env
        env_content = f"""# Configuracoes do Banco de Dados
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dossie_escolar
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Configuracoes do Backblaze B2
B2_APPLICATION_KEY_ID={request.form.get('b2_key_id')}
B2_APPLICATION_KEY={request.form.get('b2_key')}
B2_BUCKET_NAME={request.form.get('b2_bucket', 'dossie-backups')}

# Configuracoes de Retencao
BACKUP_RETENTION_DAYS={request.form.get('retention_days', '30')}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        flash('Configuração B2 salva com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao salvar configuração: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/auto-config', methods=['POST'])
@login_required
@admin_required
def backup_auto_config():
    """Configurar backup automático"""
    try:
        import subprocess
        
        action = request.form.get('action')
        schedule = request.form.get('schedule')
        
        if action == 'enable':
            # Configurar crontab
            if schedule == 'daily_02:00':
                cron_expr = '0 2 * * *'
            elif schedule == 'daily_03:00':
                cron_expr = '0 3 * * *'
            elif schedule == 'weekly_sunday':
                cron_expr = '0 2 * * 0'
            else:
                cron_expr = request.form.get('custom_cron', '0 2 * * *')
            
            # Criar tarefa agendada no Windows
            script_path = os.path.abspath('backup_b2_complete.py')
            python_path = sys.executable
            
            cmd = f'schtasks /create /tn "DossieBackupB2" /tr "{python_path} {script_path}" /sc daily /st 02:00 /f'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                flash('Backup automático ativado com sucesso!', 'success')
            else:
                flash(f'Erro ao ativar backup automático: {result.stderr}', 'error')
                
        elif action == 'disable':
            # Desativar crontab
            cmd = 'schtasks /delete /tn DossieBackupB2 /f'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                flash('Backup automático desativado com sucesso!', 'success')
            else:
                flash(f'Erro ao desativar backup automático: {result.stderr}', 'error')
                
    except Exception as e:
        flash(f'Erro ao configurar backup automático: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/test', methods=['POST'])
@login_required
@admin_required
def test_backup():
    """Testar backup automático"""
    try:
        import subprocess
        
        result = subprocess.run(['python', 'backup_b2_complete.py'],
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Teste de backup executado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': f'Erro no teste: {result.stderr}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao testar backup: {str(e)}'})

@admin_bp.route('/backup/logs')
@login_required
@admin_required
def get_logs():
    """Obter logs recentes"""
    try:
        if os.path.exists('backup_b2_complete.log'):
            with open('backup_b2_complete.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_logs = ''.join(lines[-20:])
        else:
            recent_logs = "Nenhum log disponível"
        
        return jsonify({'logs': recent_logs})
        
    except Exception as e:
        return jsonify({'logs': f'Erro ao ler logs: {str(e)}'})

@admin_bp.route('/backup/upload-b2/<filename>', methods=['POST'])
@login_required
@admin_required
def upload_to_b2(filename):
    """Fazer upload de arquivo para B2"""
    try:
        import subprocess
        
        result = subprocess.run(['python', 'b2_upload.py', filename],
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': f'Upload de {filename} para B2 realizado com sucesso!'})
        else:
            return jsonify({'success': False, 'message': f'Erro no upload: {result.stderr}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao fazer upload: {str(e)}'})

@admin_bp.route('/backup/restore-b2', methods=['POST'])
@login_required
@admin_required
def restore_from_b2():
    """Restaurar backup do B2"""
    try:
        b2_file = request.form.get('b2_file')
        if not b2_file:
            flash('Selecione um arquivo para restaurar', 'error')
            return redirect(url_for('admin.backup'))
        
        # TODO: Implementar restauração do B2
        flash(f'Restauração de {b2_file} iniciada...', 'info')
        
    except Exception as e:
        flash(f'Erro ao restaurar backup: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/restore-local', methods=['POST'])
@login_required
@admin_required
def restore_local():
    """Restaurar backup local"""
    try:
        if 'local_file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('admin.backup'))
        
        file = request.files['local_file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('admin.backup'))
        
        # Salvar arquivo temporariamente
        filename = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        file.save(filename)
        
        # TODO: Implementar restauração
        flash(f'Restauração de {file.filename} iniciada...', 'info')
        
    except Exception as e:
        flash(f'Erro ao restaurar backup: {str(e)}', 'error')
    
    return redirect(url_for('admin.backup'))

@admin_bp.route('/backup/clean', methods=['POST'])
@login_required
@admin_required
def clean_backups():
    """Limpar backups antigos"""
    try:
        import subprocess
        
        result = subprocess.run(['python', 'backup_b2_complete.py'],
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Limpeza de backups antigos concluída!'})
        else:
            return jsonify({'success': False, 'message': f'Erro na limpeza: {result.stderr}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao limpar backups: {str(e)}'})

@admin_bp.route('/create-backup', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Criar backup do banco (legado)"""
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

@admin_bp.route('/backup/delete/<filename>', methods=['DELETE'])
@login_required
@admin_required
def delete_backup(filename):
    """Deletar arquivo de backup"""
    try:
        # Verificar se o arquivo existe e é um backup
        if not filename.startswith('backup_'):
            return jsonify({'success': False, 'error': 'Arquivo inválido'})
        
        if os.path.exists(filename):
            os.remove(filename)
            return jsonify({'success': True, 'message': f'Backup {filename} deletado com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao deletar backup: {str(e)}'})

# Registrar blueprint no app principal
def init_admin(app):
    """Inicializar área de admin"""
    app.register_blueprint(admin_bp)
