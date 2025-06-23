from app import create_app, db

print("Iniciando a criação das tabelas no banco de dados...")

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}") 