# controllers/configuracao_controller.py
"""
Controller para gerenciamento de configurações
Interface web para administração
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from controllers.auth_controller import login_required, admin_required
from services.configuracao_service import config_service
from models.configuracao_avancada import ConfigCategory, ConfigScope, ConfigType
from models import db
from utils.logs import log_acao, AcoesAuditoria
import json

config_bp = Blueprint('configuracao', __name__, url_prefix='/admin/configuracoes')

@config_bp.route('/')
@login_required
@admin_required
def index():
    """Página principal de configurações - otimizada"""
    try:
        categorias = {}

        # Carregar apenas categorias principais para melhor performance
        categorias_principais = [ConfigCategory.SECURITY, ConfigCategory.SYSTEM, ConfigCategory.USER_INTERFACE]

        for categoria in categorias_principais:
            try:
                configs = config_service.obter_configuracoes_categoria(
                    categoria,
                    escola_id=session.get('escola_id'),
                    usuario_id=session.get('user_id')
                )
                if configs:
                    categorias[categoria.value] = {
                        'nome': categoria.value.replace('_', ' ').title(),
                        'configuracoes': configs[:10]  # Limitar a 10 por categoria
                    }
            except Exception as e:
                print(f"Erro ao carregar categoria {categoria}: {e}")
                continue

        return render_template('admin/configuracoes/index_otimizado.html', categorias=categorias)

    except Exception as e:
        flash(f'Erro ao carregar configurações: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@config_bp.route('/categoria/<categoria>')
@login_required
@admin_required
def categoria(categoria):
    """Configurações de uma categoria específica"""
    try:
        cat_enum = ConfigCategory(categoria)
    except ValueError:
        flash('Categoria não encontrada', 'error')
        return redirect(url_for('configuracao.index'))
    
    configs = config_service.obter_configuracoes_categoria(
        cat_enum,
        escola_id=session.get('escola_id'),
        usuario_id=session.get('user_id')
    )
    
    return render_template('admin/configuracoes/categoria.html', 
                         categoria=cat_enum, 
                         configuracoes=configs)

@config_bp.route('/editar/<int:config_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(config_id):
    """Editar uma configuração específica"""
    from models.configuracao_avancada import ConfiguracaoSistema
    
    config = ConfiguracaoSistema.query.get_or_404(config_id)
    
    if request.method == 'POST':
        try:
            novo_valor = request.form.get('valor')
            motivo = request.form.get('motivo', 'Alteração via interface web')
            
            # Converter valor conforme o tipo
            if config.tipo == ConfigType.BOOLEAN:
                novo_valor = request.form.get('valor') == 'true'
            elif config.tipo == ConfigType.INTEGER:
                novo_valor = int(novo_valor)
            elif config.tipo == ConfigType.FLOAT:
                novo_valor = float(novo_valor)
            elif config.tipo == ConfigType.JSON:
                novo_valor = json.loads(novo_valor)
            
            # Atualizar configuração
            config_service.definir_configuracao(
                chave=config.chave,
                valor=novo_valor,
                escopo=config.escopo,
                escola_id=config.escola_id,
                usuario_id=config.usuario_id,
                modulo=config.modulo,
                motivo=motivo
            )
            
            flash('Configuração atualizada com sucesso!', 'success')
            
            if config.requer_reinicializacao:
                flash('Esta configuração requer reinicialização do sistema para ter efeito.', 'warning')
            
            return redirect(url_for('configuracao.categoria', categoria=config.categoria.value))
            
        except ValueError as e:
            flash(f'Erro de validação: {str(e)}', 'error')
        except Exception as e:
            flash(f'Erro ao atualizar configuração: {str(e)}', 'error')
    
    return render_template('admin/configuracoes/editar.html', config=config)

@config_bp.route('/api/configuracao/<chave>')
@login_required
def api_obter_configuracao(chave):
    """API para obter valor de configuração"""
    try:
        valor = config_service.obter_configuracao(
            chave,
            escola_id=session.get('escola_id'),
            usuario_id=session.get('user_id')
        )
        
        return jsonify({
            'success': True,
            'chave': chave,
            'valor': valor
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@config_bp.route('/api/configuracao/<chave>', methods=['POST'])
@login_required
@admin_required
def api_definir_configuracao(chave):
    """API para definir valor de configuração"""
    try:
        data = request.get_json()
        valor = data.get('valor')
        motivo = data.get('motivo', 'Alteração via API')
        escopo = ConfigScope(data.get('escopo', 'global'))
        
        config_service.definir_configuracao(
            chave=chave,
            valor=valor,
            escopo=escopo,
            escola_id=data.get('escola_id'),
            usuario_id=data.get('usuario_id'),
            modulo=data.get('modulo'),
            motivo=motivo
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@config_bp.route('/exportar')
@login_required
@admin_required
def exportar():
    """Exportar configurações"""
    try:
        escola_id = request.args.get('escola_id', type=int)
        dados = config_service.exportar_configuracoes(escola_id)
        
        return jsonify(dados)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@config_bp.route('/importar', methods=['POST'])
@login_required
@admin_required
def importar():
    """Importar configurações"""
    try:
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('configuracao.index'))
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(url_for('configuracao.index'))
        
        sobrescrever = request.form.get('sobrescrever') == 'true'
        
        # Ler e processar arquivo JSON
        dados = json.load(arquivo)
        resultado = config_service.importar_configuracoes(dados, sobrescrever)
        
        flash(f'Importação concluída: {resultado["importadas"]} configurações importadas', 'success')
        
        if resultado['erros']:
            for erro in resultado['erros']:
                flash(erro, 'warning')
        
        # Log da ação
        log_acao(
            AcoesAuditoria.CONFIGURACAO_ALTERADA,
            'ConfiguracaoSistema',
            f'Importação de configurações: {resultado["importadas"]} importadas'
        )
        
        return redirect(url_for('configuracao.index'))
        
    except Exception as e:
        flash(f'Erro na importação: {str(e)}', 'error')
        return redirect(url_for('configuracao.index'))

@config_bp.route('/resetar/<int:config_id>', methods=['POST'])
@login_required
@admin_required
def resetar(config_id):
    """Resetar configuração para valor padrão"""
    from models.configuracao_avancada import ConfiguracaoSistema
    
    try:
        config = ConfiguracaoSistema.query.get_or_404(config_id)
        
        if not config.valor_padrao:
            flash('Esta configuração não possui valor padrão definido', 'error')
            return redirect(url_for('configuracao.categoria', categoria=config.categoria.value))
        
        config_service.definir_configuracao(
            chave=config.chave,
            valor=config.valor_padrao,
            escopo=config.escopo,
            escola_id=config.escola_id,
            usuario_id=config.usuario_id,
            modulo=config.modulo,
            motivo='Reset para valor padrão'
        )
        
        flash('Configuração resetada para valor padrão', 'success')
        
    except Exception as e:
        flash(f'Erro ao resetar configuração: {str(e)}', 'error')
    
    return redirect(url_for('configuracao.categoria', categoria=config.categoria.value))

@config_bp.route('/historico/<int:config_id>')
@login_required
@admin_required
def historico(config_id):
    """Visualizar histórico de uma configuração"""
    from models.configuracao_avancada import ConfiguracaoSistema, HistoricoConfiguracao
    
    config = ConfiguracaoSistema.query.get_or_404(config_id)
    historico = HistoricoConfiguracao.query.filter_by(
        configuracao_id=config_id
    ).order_by(HistoricoConfiguracao.data_mudanca.desc()).limit(50).all()
    
    return render_template('admin/configuracoes/historico.html', 
                         config=config, 
                         historico=historico)

# Função helper para templates
@config_bp.app_template_global()
def get_config(chave, default=None):
    """Função global para templates acessarem configurações"""
    return config_service.obter_configuracao(
        chave,
        escola_id=session.get('escola_id'),
        usuario_id=session.get('user_id'),
        default=default
    )
