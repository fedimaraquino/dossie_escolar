# controllers/movimentacao_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from models import db, Movimentacao, Dossie, Escola, Usuario
from utils.logs import log_acao, AcoesAuditoria
from .auth_controller import login_required


movimentacao_bp = Blueprint('movimentacao', __name__, url_prefix='/movimentacoes')

@movimentacao_bp.route('/')
@login_required
def listar():
    """Lista movimentações"""
    search = request.args.get('search', '')
    escola_id = request.args.get('escola', '')
    tipo = request.args.get('tipo', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    # Verificar permissões
    usuario = Usuario.query.get(session['user_id'])
    query = Movimentacao.query.join(Dossie)

    # Aplicar filtro de escola baseado no usuário atual
    escola_atual_id = usuario.get_escola_atual_id()
    if escola_atual_id:
        query = query.filter(Dossie.escola_id == escola_atual_id)
    
    if search:
        query = query.filter(
            db.or_(
                Dossie.numero_dossie.contains(search),
                Dossie.nome_aluno.contains(search),
                Movimentacao.solicitante_nome.contains(search),
                Movimentacao.solicitante_documento.contains(search)
            )
        )
    
    if escola_id and usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        query = query.filter(Dossie.escola_id == escola_id)
    
    if tipo:
        query = query.filter(Movimentacao.tipo_movimentacao == tipo)
    
    if status:
        query = query.filter(Movimentacao.status == status)

    movimentacoes = query.order_by(Movimentacao.data_movimentacao.desc()).paginate(
        page=page, per_page=15, error_out=False
    )

    escola_filtro = None
    if escola_id:
        escola_filtro = Escola.query.get(escola_id)

    escolas = Escola.query.all() if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral' else [usuario.escola]

    return render_template('movimentacoes/listar.html', 
                         movimentacoes=movimentacoes, 
                         search=search, 
                         escola_filtro=escola_filtro,
                         escolas=escolas,
                         tipo=tipo,
                         status=status)

@movimentacao_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cadastra nova movimentação"""
    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        dossie_id = request.form.get('dossie_id')
        tipo_movimentacao = request.form.get('tipo_movimentacao')
        
        if not dossie_id or not tipo_movimentacao:
            flash('Dossiê e tipo de movimentação são obrigatórios!', 'error')
            dossies = Dossie.query.filter_by(escola_id=usuario.escola_id).all() if usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral' else Dossie.query.all()
            return render_template('movimentacoes/nova.html', dossies=dossies)

        dossie = Dossie.query.get(dossie_id)
        if not dossie or (usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral' and dossie.escola_id != usuario.escola_id):
            flash('Dossiê não encontrado ou acesso negado.', 'error')
            return redirect(url_for('movimentacao.listar'))

        # Processar dados do solicitante
        solicitante_id = request.form.get('solicitante_id')
        solicitante_nome = request.form.get('solicitante_nome', '').strip()
        solicitante_documento = request.form.get('solicitante_documento', '').strip()
        solicitante_telefone = request.form.get('solicitante_telefone', '').strip()

        movimentacao = Movimentacao(
            dossie_id=dossie_id,
            tipo_movimentacao=tipo_movimentacao,
            usuario_id=usuario.id,
            escola_origem_id=dossie.escola_id,
            escola_destino_id=request.form.get('escola_destino_id') if request.form.get('escola_destino_id') else None,
            solicitante_id=int(solicitante_id) if solicitante_id else None,
            solicitante_nome=solicitante_nome,
            solicitante_documento=solicitante_documento,
            solicitante_telefone=solicitante_telefone,
            motivo=request.form.get('motivo', '').strip(),
            observacoes=request.form.get('observacoes', '').strip(),
            data_prevista_devolucao=datetime.strptime(request.form.get('data_prevista_devolucao'), '%Y-%m-%d') if request.form.get('data_prevista_devolucao') else None,
            status='pendente'
        )

        try:
            db.session.add(movimentacao)
            
            # Atualizar data da última movimentação no dossiê
            dossie.data_ultima_movimentacao = datetime.now()
            
            db.session.commit()

            # Registrar log
            log_acao(AcoesAuditoria.MOVIMENTACAO_CRIADA, 'Movimentacao', f'Movimentação criada: {movimentacao.tipo_movimentacao} - Dossiê {movimentacao.dossie.numero_dossie if movimentacao.dossie else "N/A"}')

            flash('Movimentação registrada com sucesso!', 'success')
            return redirect(url_for('movimentacao.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar movimentação: {str(e)}', 'error')

    # Buscar dossiês disponíveis
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        dossies = Dossie.query.filter_by(status='ativo').all()
        escolas = Escola.query.all()
    else:
        dossies = Dossie.query.filter_by(escola_id=usuario.escola_id, status='ativo').all()
        escolas = [usuario.escola]

    # Buscar solicitantes ativos
    from models import Solicitante
    solicitantes = Solicitante.query.filter_by(status='ativo').order_by(Solicitante.nome).all()

    # Verificar se há solicitante pré-selecionado na URL
    solicitante_preselected = request.args.get('solicitante')

    return render_template('movimentacoes/nova.html',
                         dossies=dossies,
                         escolas=escolas,
                         solicitantes=solicitantes,
                         solicitante_preselected=solicitante_preselected)

@movimentacao_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    """Visualiza detalhes da movimentação"""
    usuario = Usuario.query.get(session['user_id'])
    movimentacao = Movimentacao.query.get_or_404(id)
    
    # Verificar se usuário pode acessar esta movimentação
    if usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral' and movimentacao.dossie.escola_id != usuario.escola_id:
        flash('Acesso negado a esta movimentação.', 'error')
        return redirect(url_for('movimentacao.listar'))
    
    return render_template('movimentacoes/ver.html', movimentacao=movimentacao)

@movimentacao_bp.route('/concluir/<int:id>', methods=['POST'])
@login_required
def concluir(id):
    """Marca movimentação como concluída"""
    usuario = Usuario.query.get(session['user_id'])
    movimentacao = Movimentacao.query.get_or_404(id)
    
    # Verificar se usuário pode concluir esta movimentação
    if usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral' and movimentacao.dossie.escola_id != usuario.escola_id:
        flash('Acesso negado a esta movimentação.', 'error')
        return redirect(url_for('movimentacao.listar'))

    try:
        movimentacao.marcar_como_concluida()
        db.session.commit()
        flash('Movimentação marcada como concluída!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao concluir movimentação: {str(e)}', 'error')

    return redirect(url_for('movimentacao.ver', id=id))

@movimentacao_bp.route('/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar(id):
    """Cancela movimentação"""
    usuario = Usuario.query.get(session['user_id'])
    movimentacao = Movimentacao.query.get_or_404(id)
    
    # Verificar se usuário pode cancelar esta movimentação
    pode_cancelar = (usuario.perfil_obj and
                    (usuario.perfil_obj.perfil == 'Administrador Geral' or
                     (usuario.perfil_obj.perfil == 'Administrador da Escola' and movimentacao.dossie.escola_id == usuario.escola_id)))

    if not pode_cancelar:
        flash('Acesso negado para cancelar esta movimentação.', 'error')
        return redirect(url_for('movimentacao.listar'))

    try:
        movimentacao.status = 'cancelado'
        db.session.commit()
        flash('Movimentação cancelada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cancelar movimentação: {str(e)}', 'error')

    return redirect(url_for('movimentacao.ver', id=id))

@movimentacao_bp.route('/relatorio')
@login_required
def relatorio():
    """Relatório de movimentações"""
    usuario = Usuario.query.get(session['user_id'])
    
    # Estatísticas básicas
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        total_movimentacoes = Movimentacao.query.count()
        pendentes = Movimentacao.query.filter_by(status='pendente').count()
        em_atraso = Movimentacao.query.filter(
            Movimentacao.data_prevista_devolucao < datetime.now(),
            Movimentacao.status == 'pendente'
        ).count()
    else:
        total_movimentacoes = Movimentacao.query.join(Dossie).filter(
            Dossie.escola_id == usuario.escola_id
        ).count()
        pendentes = Movimentacao.query.join(Dossie).filter(
            Dossie.escola_id == usuario.escola_id,
            Movimentacao.status == 'pendente'
        ).count()
        em_atraso = Movimentacao.query.join(Dossie).filter(
            Dossie.escola_id == usuario.escola_id,
            Movimentacao.data_prevista_devolucao < datetime.now(),
            Movimentacao.status == 'pendente'
        ).count()
    
    stats = {
        'total_movimentacoes': total_movimentacoes,
        'pendentes': pendentes,
        'em_atraso': em_atraso,
        'concluidas': total_movimentacoes - pendentes
    }
    
    return render_template('movimentacoes/relatorio.html', stats=stats)

@movimentacao_bp.route('/pendentes')
@login_required
def pendentes():
    """Lista movimentações pendentes"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    usuario = Usuario.query.get(session['user_id'])

    # Query base para movimentações pendentes
    query = Movimentacao.query.join(Dossie).filter(Movimentacao.status == 'pendente')

    # Se não for admin geral, filtrar apenas movimentações da escola do usuário
    if usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral':
        query = query.filter(Dossie.escola_id == usuario.escola_id)

    # Aplicar filtro de busca
    if search:
        query = query.filter(
            db.or_(
                Dossie.numero_dossie.contains(search),
                Dossie.nome_aluno.contains(search),
                Movimentacao.solicitante_nome.contains(search)
            )
        )

    # Ordenação por data de movimentação (mais recentes primeiro)
    query = query.order_by(Movimentacao.data_movimentacao.desc())

    # Paginação
    movimentacoes = query.paginate(
        page=page, per_page=10, error_out=False
    )

    # Buscar escolas para filtro (apenas admin geral)
    escolas = []
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        escolas = Escola.query.all()

    return render_template('movimentacoes/listar.html',
                         movimentacoes=movimentacoes,
                         search=search,
                         tipo='',
                         status='pendente',
                         escolas=escolas,
                         escola_filtro=None,
                         titulo="Movimentações Pendentes")

@movimentacao_bp.route('/emprestados')
@login_required
def emprestados():
    """Lista dossiês emprestados (movimentações de empréstimo pendentes)"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    usuario = Usuario.query.get(session['user_id'])

    # Query base para empréstimos pendentes
    query = Movimentacao.query.join(Dossie).filter(
        Movimentacao.tipo_movimentacao == 'emprestimo',
        Movimentacao.status == 'pendente'
    )

    # Se não for admin geral, filtrar apenas movimentações da escola do usuário
    if usuario.perfil_obj and usuario.perfil_obj.perfil != 'Administrador Geral':
        query = query.filter(Dossie.escola_id == usuario.escola_id)

    # Aplicar filtro de busca
    if search:
        query = query.filter(
            db.or_(
                Dossie.numero_dossie.contains(search),
                Dossie.nome_aluno.contains(search),
                Movimentacao.solicitante_nome.contains(search)
            )
        )

    # Ordenação por data prevista de devolução (mais urgentes primeiro)
    query = query.order_by(
        Movimentacao.data_prevista_devolucao.asc().nullslast(),
        Movimentacao.data_movimentacao.desc()
    )

    # Paginação
    movimentacoes = query.paginate(
        page=page, per_page=10, error_out=False
    )

    # Buscar escolas para filtro (apenas admin geral)
    escolas = []
    if usuario.perfil_obj and usuario.perfil_obj.perfil == 'Administrador Geral':
        escolas = Escola.query.all()

    return render_template('movimentacoes/listar.html',
                         movimentacoes=movimentacoes,
                         search=search,
                         tipo='emprestimo',
                         status='pendente',
                         escolas=escolas,
                         escola_filtro=None,
                         titulo="Dossiês Emprestados")
