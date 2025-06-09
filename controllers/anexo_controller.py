# controllers/anexo_controller.py
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, redirect, url_for, flash, session, jsonify, send_file
from models import db, Anexo, Dossie
from .auth_controller import login_required

anexo_bp = Blueprint('anexo', __name__, url_prefix='/anexos')

# Configurações de upload
UPLOAD_FOLDER = 'uploads/anexos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_upload_folder():
    """Cria a pasta de upload se não existir"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@anexo_bp.route('/upload/<int:dossie_id>', methods=['POST'])
@login_required
def upload(dossie_id):
    """Upload de anexos para um dossiê"""
    dossie = Dossie.query.get_or_404(dossie_id)
    
    if 'arquivos' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
    
    files = request.files.getlist('arquivos')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
    
    create_upload_folder()
    uploaded_files = []
    errors = []
    
    for file in files:
        if file and file.filename != '':
            if not allowed_file(file.filename):
                errors.append(f'Tipo de arquivo não permitido: {file.filename}')
                continue
            
            # Verificar tamanho do arquivo
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f'Arquivo muito grande: {file.filename} ({file_size / (1024*1024):.1f}MB)')
                continue
            
            # Gerar nome seguro
            filename = secure_filename(file.filename)
            
            # Adicionar timestamp para evitar conflitos
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Caminho completo
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                # Salvar arquivo
                file.save(filepath)
                
                # Obter nome personalizado se fornecido
                nome_personalizado = request.form.get(f'nome_personalizado_{file.filename}', '').strip()

                # Salvar no banco
                anexo = Anexo(
                    dossie_id=dossie_id,
                    nome=file.filename,  # Nome original
                    nome_personalizado=nome_personalizado if nome_personalizado else None,
                    caminho=filepath,
                    tamanho=file_size,
                    tipo_arquivo=filename.rsplit('.', 1)[1].lower() if '.' in filename else None,
                    usuario_upload_id=session['user_id']
                )
                
                db.session.add(anexo)
                uploaded_files.append(file.filename)
                
            except Exception as e:
                errors.append(f'Erro ao salvar {file.filename}: {str(e)}')
    
    try:
        db.session.commit()
        
        if uploaded_files:
            message = f'{len(uploaded_files)} arquivo(s) enviado(s) com sucesso'
            if errors:
                message += f'. {len(errors)} erro(s) encontrado(s)'
            
            return jsonify({
                'success': True, 
                'message': message,
                'uploaded': uploaded_files,
                'errors': errors
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Nenhum arquivo foi enviado',
                'errors': errors
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao salvar no banco: {str(e)}'})

@anexo_bp.route('/download/<int:anexo_id>')
@login_required
def download(anexo_id):
    """Download de um anexo"""
    anexo = Anexo.query.get_or_404(anexo_id)
    
    try:
        return send_file(anexo.caminho, as_attachment=True, download_name=anexo.nome)
    except FileNotFoundError:
        flash('Arquivo não encontrado no servidor', 'error')
        return redirect(url_for('dossie.ver', id=anexo.dossie_id))

@anexo_bp.route('/excluir/<int:anexo_id>', methods=['POST'])
@login_required
def excluir(anexo_id):
    """Excluir um anexo"""
    anexo = Anexo.query.get_or_404(anexo_id)
    dossie_id = anexo.dossie_id
    
    try:
        # Remover arquivo físico
        if os.path.exists(anexo.caminho):
            os.remove(anexo.caminho)
        
        # Remover do banco
        db.session.delete(anexo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Anexo excluído com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao excluir anexo: {str(e)}'})

@anexo_bp.route('/listar/<int:dossie_id>')
@login_required
def listar_json(dossie_id):
    """Retorna lista de anexos em JSON para atualização dinâmica"""
    anexos = Anexo.query.filter_by(dossie_id=dossie_id).order_by(Anexo.data_upload.desc()).all()
    
    return jsonify({
        'anexos': [{
            'id': anexo.id,
            'nome': anexo.nome,
            'nome_personalizado': anexo.nome_personalizado,
            'nome_exibicao': anexo.nome_personalizado if anexo.nome_personalizado else anexo.nome,
            'tamanho_formatado': anexo.tamanho_formatado,
            'tipo_arquivo': anexo.tipo_arquivo,
            'icone': anexo.icone_arquivo,
            'data_upload': anexo.data_upload.strftime('%d/%m/%Y %H:%M') if anexo.data_upload else '',
            'usuario': anexo.usuario_upload.nome if anexo.usuario_upload else 'Desconhecido'
        } for anexo in anexos]
    })
