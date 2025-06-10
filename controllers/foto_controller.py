# controllers/foto_controller.py
"""
Controller para gerenciamento de fotos de usuários
"""

from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from controllers.auth_controller import login_required
from models import db, Usuario
from utils.logs import log_acao, AcoesAuditoria
import os
import uuid
from PIL import Image

foto_bp = Blueprint('foto', __name__, url_prefix='/api/foto')

# Extensões permitidas para fotos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(300, 300)):
    """Redimensiona a imagem para um tamanho máximo"""
    try:
        with Image.open(image_path) as img:
            # Converter para RGB se necessário
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar mantendo proporção
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Salvar com qualidade otimizada
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            
        return True
    except Exception as e:
        print(f"Erro ao redimensionar imagem: {e}")
        return False

@foto_bp.route('/upload', methods=['POST'])
@login_required
def upload_foto():
    """Upload de foto do usuário"""
    try:
        # Verificar se foi enviado um arquivo
        if 'foto' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['foto']
        
        # Verificar se um arquivo foi selecionado
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': 'Tipo de arquivo não permitido. Use: PNG, JPG, JPEG, GIF ou WEBP'
            }), 400
        
        # Obter usuário atual
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404
        
        # Gerar nome único para o arquivo
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{usuario.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Definir caminho para salvar
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'fotos')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        # Remover foto anterior se existir
        if usuario.foto:
            old_photo_path = os.path.join(upload_folder, usuario.foto)
            if os.path.exists(old_photo_path):
                try:
                    os.remove(old_photo_path)
                except:
                    pass  # Não falhar se não conseguir remover
        
        # Salvar arquivo
        file.save(file_path)
        
        # Redimensionar imagem
        if not resize_image(file_path):
            # Se falhar ao redimensionar, continuar com a imagem original
            pass
        
        # Atualizar banco de dados
        usuario.set_foto(filename)
        db.session.commit()
        
        # Atualizar sessão
        session['user_foto_url'] = usuario.get_foto_url()
        
        # Registrar log
        log_acao(AcoesAuditoria.ALTERACAO, 'Usuario', f'Foto atualizada: {usuario.nome}', usuario.id)
        
        return jsonify({
            'success': True,
            'message': 'Foto atualizada com sucesso!',
            'foto_url': usuario.get_foto_url()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@foto_bp.route('/remove', methods=['POST'])
@login_required
def remove_foto():
    """Remove a foto do usuário"""
    try:
        # Obter usuário atual
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404
        
        # Remover foto
        usuario.remove_foto()
        db.session.commit()
        
        # Atualizar sessão
        session['user_foto_url'] = usuario.get_foto_url()
        
        # Registrar log
        log_acao(AcoesAuditoria.ALTERACAO, 'Usuario', f'Foto removida: {usuario.nome}', usuario.id)
        
        return jsonify({
            'success': True,
            'message': 'Foto removida com sucesso!',
            'foto_url': usuario.get_foto_url()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@foto_bp.route('/info')
@login_required
def foto_info():
    """Retorna informações sobre a foto do usuário"""
    try:
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'has_foto': usuario.has_foto(),
            'foto_url': usuario.get_foto_url(),
            'foto_filename': usuario.foto
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
