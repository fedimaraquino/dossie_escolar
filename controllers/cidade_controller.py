# controllers/cidade_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Cidade
from .auth_controller import login_required, admin_required

cidade_bp = Blueprint('cidade', __name__, url_prefix='/cidades')

@cidade_bp.route('/')
@login_required
def listar():
    """Lista todas as cidades"""
    search = request.args.get('search', '')
    uf = request.args.get('uf', '')
    page = request.args.get('page', 1, type=int)

    query = Cidade.query
    
    if search:
        query = query.filter(
            db.or_(
                Cidade.nome.contains(search),
                Cidade.uf.contains(search),
                Cidade.pais.contains(search)
            )
        )
    
    if uf:
        query = query.filter(Cidade.uf == uf)

    cidades = query.order_by(Cidade.nome).paginate(
        page=page, per_page=15, error_out=False
    )

    # Lista de UFs para o filtro
    ufs = db.session.query(Cidade.uf).distinct().order_by(Cidade.uf).all()
    ufs = [uf[0] for uf in ufs]

    return render_template('cidades/listar.html', 
                         cidades=cidades, 
                         search=search, 
                         uf=uf,
                         ufs=ufs)

@cidade_bp.route('/nova', methods=['GET', 'POST'])
@admin_required
def nova():
    """Cadastra nova cidade"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip().upper()
        pais = request.form.get('pais', 'Brasil').strip()
        
        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('cidades/nova.html')

        # Verificar se já existe
        if Cidade.query.filter_by(nome=nome, uf=uf).first():
            flash('Cidade já cadastrada nesta UF!', 'error')
            return render_template('cidades/nova.html')

        cidade = Cidade(
            nome=nome,
            uf=uf,
            pais=pais
        )

        try:
            db.session.add(cidade)
            db.session.commit()
            flash('Cidade cadastrada com sucesso!', 'success')
            return redirect(url_for('cidade.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar cidade: {str(e)}', 'error')

    return render_template('cidades/nova.html')

@cidade_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    """Visualiza detalhes da cidade"""
    cidade = Cidade.query.get_or_404(id)
    return render_template('cidades/ver.html', cidade=cidade)

@cidade_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar(id):
    """Edita dados da cidade"""
    cidade = Cidade.query.get_or_404(id)

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        uf = request.form.get('uf', '').strip().upper()
        pais = request.form.get('pais', 'Brasil').strip()

        if not nome or not uf:
            flash('Nome e UF são obrigatórios!', 'error')
            return render_template('cidades/editar.html', cidade=cidade)

        # Verificar se já existe outra cidade com mesmo nome/uf
        cidade_existente = Cidade.query.filter_by(nome=nome, uf=uf).first()
        if cidade_existente and cidade_existente.id_cidade != cidade.id_cidade:
            flash('Já existe outra cidade com este nome nesta UF!', 'error')
            return render_template('cidades/editar.html', cidade=cidade)

        cidade.nome = nome
        cidade.uf = uf
        cidade.pais = pais

        try:
            db.session.commit()
            flash('Cidade atualizada com sucesso!', 'success')
            return redirect(url_for('cidade.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cidade: {str(e)}', 'error')

    return render_template('cidades/editar.html', cidade=cidade)

@cidade_bp.route('/excluir/<int:id>', methods=['POST'])
@admin_required
def excluir(id):
    """Exclui cidade"""
    cidade = Cidade.query.get_or_404(id)
    
    # Verificar se há escolas vinculadas
    from models import Escola
    escolas_vinculadas = Escola.query.filter_by(id_cidade=cidade.id_cidade).count()
    
    if escolas_vinculadas > 0:
        flash(f'Não é possível excluir a cidade "{cidade.nome}" pois há {escolas_vinculadas} escola(s) vinculada(s).', 'error')
        return redirect(url_for('cidade.listar'))

    try:
        db.session.delete(cidade)
        db.session.commit()
        flash(f'Cidade "{cidade.nome}" excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir cidade: {str(e)}', 'error')

    return redirect(url_for('cidade.listar'))

@cidade_bp.route('/api/por-uf/<uf>')
@login_required
def api_por_uf(uf):
    """API para buscar cidades por UF"""
    from flask import jsonify
    
    cidades = Cidade.query.filter_by(uf=uf.upper()).order_by(Cidade.nome).all()
    return jsonify([{
        'id': cidade.id_cidade,
        'nome': cidade.nome
    } for cidade in cidades])
