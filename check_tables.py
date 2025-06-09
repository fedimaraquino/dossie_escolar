from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Verificar estrutura da tabela movimentacoes
    with db.engine.connect() as conn:
        print("Estrutura da tabela movimentacoes:")
        result = conn.execute(text(""""""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'movimentacoes'
            ORDER BY ordinal_position;
        """))
        for row in result:
            print(f"  - {row[0]} ({row[1]}) - Nullable: {row[2]}")

        # Verificar se a coluna solicitante_id existe
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = 'movimentacoes' AND column_name = 'solicitante_id';
        """))
        exists = result.fetchone()[0]
        print(f"\nColuna 'solicitante_id' existe: {'Sim' if exists > 0 else 'Não'}")

        if exists == 0:
            print("\n🔧 Adicionando coluna solicitante_id...")
            try:
                conn.execute(text("ALTER TABLE movimentacoes ADD COLUMN solicitante_id INTEGER REFERENCES solicitantes(id);"))
                conn.commit()
                print("✅ Coluna adicionada com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao adicionar coluna: {e}")
                conn.rollback()
