# controllers/escola_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, Escola, Cidade, Usuario, Movimentacao, Dossie
from utils.logs import log_acao, AcoesAuditoria
from .auth_controller import login_required, admin_required

escola_bp = Blueprint('escola', __name__, url_prefix='/escolas')

@escola_bp.route('/')
@login_required
def listar():
    """Lista todas as escolas"""
    search = request.args.get('search', '')
    situacao = request.args.get('situacao', '')
    uf = request.args.get('uf', '')
    page = request.args.get('page', 1, type=int)

    query = Escola.query
    
    if search:
        query = query.filter(
            db.or_(
                Escola.nome.contains(search),
                Escola.cnpj.contains(search),
                Escola.inep.contains(search)
            )
        )
    
    if situacao:
        query = query.filter(Escola.situacao == situacao)
    
    if uf:
        query = query.filter(Escola.uf == uf)

    escolas = query.paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('escolas/listar.html', 
                         escolas=escolas, 
                         search=search, 
                         situacao=situacao, 
                         uf=uf)

@escola_bp.route('/nova', methods=['GET', 'POST'])
@admin_required
def nova():
    """Cadastra nova escola"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip()
        
        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/nova.html', 
                                 cidades=Cidade.query.all(),
                                 usuarios=Usuario.query.filter_by(situacao='ativo').all())

        escola = Escola(
            nome=nome,
            endereco=request.form.get('endereco', '').strip(),
            uf=uf,
            cnpj=request.form.get('cnpj', '').strip(),
            inep=request.form.get('inep', '').strip(),
            email=request.form.get('email', '').strip(),
            telefone=request.form.get('telefone', '').strip(),
            diretor=request.form.get('diretor', '').strip(),
            vice_diretor=request.form.get('vice_diretor', '').strip(),
            observacoes=request.form.get('observacoes', '').strip(),
            id_cidade=request.form.get('id_cidade') if request.form.get('id_cidade') else None,
            diretor_id=request.form.get('diretor_id') if request.form.get('diretor_id') else None,
            situacao=request.form.get('situacao', 'ativa')
        )

        try:
            db.session.add(escola)
            db.session.commit()
            flash('Escola cadastrada com sucesso!', 'success')
            return redirect(url_for('escola.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar escola: {str(e)}', 'error')

    cidades = Cidade.query.all()
    usuarios = Usuario.query.filter_by(situacao='ativo').all()
    return render_template('escolas/nova.html', cidades=cidades, usuarios=usuarios)

@escola_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    """Visualiza detalhes da escola"""
    escola = Escola.query.get_or_404(id)

    # Estatísticas
    total_usuarios = len(escola.usuarios)
    total_dossies = len(escola.dossies)
    total_movimentacoes = Movimentacao.query.join(Dossie).filter(Dossie.id_escola == escola.id).count()
    movimentacoes_pendentes = Movimentacao.query.join(Dossie).filter(Dossie.id_escola == escola.id, Movimentacao.status == 'pendente').count()

    # Adiciona dinamicamente os atributos ao objeto escola
    escola.total_usuarios = total_usuarios
    escola.total_dossies = total_dossies
    escola.total_movimentacoes = total_movimentacoes
    escola.movimentacoes_pendentes = movimentacoes_pendentes

    return render_template('escolas/ver.html', escola=escola)

@escola_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    """Edita dados da escola"""
    escola = Escola.query.get_or_404(id)

    if request.method == 'POST':
        escola.nome = request.form.get('nome', '').strip()
        escola.endereco = request.form.get('endereco', '').strip()
        escola.uf = request.form.get('uf', '').strip()
        escola.cnpj = request.form.get('cnpj', '').strip()
        escola.inep = request.form.get('inep', '').strip()
        escola.email = request.form.get('email', '').strip()
        escola.telefone = request.form.get('telefone', '').strip()
        escola.diretor = request.form.get('diretor', '').strip()
        escola.vice_diretor = request.form.get('vice_diretor', '').strip()
        escola.observacoes = request.form.get('observacoes', '').strip()
        escola.id_cidade = request.form.get('id_cidade') if request.form.get('id_cidade') else None
        escola.diretor_id = request.form.get('diretor_id') if request.form.get('diretor_id') else None
        escola.situacao = request.form.get('situacao', 'ativa')

        if not escola.nome or not escola.uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('escolas/editar.html', 
                                 escola=escola,
                                 cidades=Cidade.query.all(),
                                 usuarios=Usuario.query.filter_by(situacao='ativo').all())

        try:
            # Log detalhado da edição
            import json
            usuario_logado = Usuario.query.get(session['user_id'])
            detalhes_log = {
                'escola_editada': {
                    'id': escola.id,
                    'nome': escola.nome,
                    'cnpj': escola.cnpj,
                    'situacao': escola.situacao
                },
                'editado_por': usuario_logado.nome if usuario_logado else 'Sistema',
                'ip_origem': request.remote_addr,
                'user_agent': request.headers.get('User-Agent')
            }

            log_acao(AcoesAuditoria.ESCOLA_EDITADA, 'Escola', json.dumps(detalhes_log))

            db.session.commit()
            flash('Escola atualizada com sucesso!', 'success')
            return redirect(url_for('escola.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar escola: {str(e)}', 'error')

    cidades = Cidade.query.all()
    usuarios = Usuario.query.filter_by(situacao='ativo').all()
    return render_template('escolas/editar.html', 
                         escola=escola, 
                         cidades=cidades, 
                         usuarios=usuarios)

@escola_bp.route('/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir(id):
    """Exclui escola"""
    escola = Escola.query.get_or_404(id)
    
    try:
        # Log detalhado da exclusão
        import json
        usuario_logado = Usuario.query.get(session['user_id'])
        detalhes_log = {
            'escola_excluida': {
                'id': escola.id,
                'nome': escola.nome,
                'cnpj': escola.cnpj,
                'situacao': escola.situacao
            },
            'excluido_por': usuario_logado.nome if usuario_logado else 'Sistema',
            'ip_origem': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }

        log_acao(AcoesAuditoria.ESCOLA_EXCLUIDA, 'Escola', json.dumps(detalhes_log))

        db.session.delete(escola)
        db.session.commit()
        flash(f'Escola "{escola.nome}" excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir escola: {str(e)}', 'error')

    return redirect(url_for('escola.listar'))

@escola_bp.route('/configuracoes/<int:id>')
@admin_required
def configuracoes(id):
    """Configurações da escola"""
    escola = Escola.query.get_or_404(id)
    return render_template('escolas/configuracoes.html', escola=escola)
