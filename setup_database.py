from app import create_app, init_database

print("Iniciando a configuração completa do banco de dados (tabelas e dados iniciais)...")

app = create_app()

# A função init_database já cria as tabelas e os dados iniciais (usuário admin, perfis, etc.)
init_database(app)

print("Configuração do banco de dados concluída com sucesso.") 