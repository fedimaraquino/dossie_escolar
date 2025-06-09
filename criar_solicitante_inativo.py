from app import create_app
from models import db, Solicitante
from datetime import datetime

app = create_app()
with app.app_context():
    # Criar um solicitante inativo para teste
    solicitante_inativo = Solicitante(
        nome="Pedro Santos Inativo",
        endereco="Rua Inativa, 456",
        celular="(11) 97777-7777",
        cidade_id=1,
        cpf="555.666.777-88",
        email="pedro.inativo@email.com",
        parentesco="pai",
        data_nascimento=datetime(1975, 8, 20).date(),
        tipo_solicitacao="certificado",
        status="inativo",  # Status inativo
        data_cadastro=datetime.now(),
        observacoes="Solicitante inativo para teste de ativação"
    )
    
    try:
        db.session.add(solicitante_inativo)
        db.session.commit()
        print(f"✅ Solicitante inativo criado com sucesso!")
        print(f"   ID: {solicitante_inativo.id}")
        print(f"   Nome: {solicitante_inativo.nome}")
        print(f"   Status: {solicitante_inativo.status}")
        print(f"   Movimentações: {len(solicitante_inativo.movimentacoes)}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar solicitante: {e}")
    
    # Listar todos os solicitantes
    print(f"\nTodos os solicitantes:")
    solicitantes = Solicitante.query.all()
    for sol in solicitantes:
        print(f"  - ID: {sol.id} - {sol.nome} - Status: {sol.status} - Movimentações: {len(sol.movimentacoes)}")
