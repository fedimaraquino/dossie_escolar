from app import create_app
from models import db, Dossie

app = create_app()
with app.app_context():
    # Verificar dossiê em detalhes
    dossie = Dossie.query.first()
    if dossie:
        print(f"Dossiê encontrado:")
        print(f"  ID: {dossie.id}")
        print(f"  Situação: '{dossie.situacao}'")
        print(f"  Situação repr: {repr(dossie.situacao)}")
        print(f"  Situação len: {len(dossie.situacao)}")
        print(f"  Situação bytes: {dossie.situacao.encode('utf-8')}")
        
        # Testar diferentes consultas
        print("\nTestando consultas:")
        
        # Consulta 1: filter_by
        result1 = Dossie.query.filter_by(situacao='ativo').all()
        print(f"filter_by(situacao='ativo'): {len(result1)} resultados")
        
        # Consulta 2: filter com ==
        result2 = Dossie.query.filter(Dossie.situacao == 'ativo').all()
        print(f"filter(situacao == 'ativo'): {len(result2)} resultados")
        
        # Consulta 3: filter com strip
        result3 = Dossie.query.filter(Dossie.situacao.like('%ativo%')).all()
        print(f"filter(situacao.like('%ativo%')): {len(result3)} resultados")
        
        # Consulta 4: todos os dossiês
        result4 = Dossie.query.all()
        print(f"query.all(): {len(result4)} resultados")
        
        # Limpar situação e definir novamente
        print("\n🔧 Limpando e redefinindo situação...")
        dossie.situacao = 'ativo'
        db.session.commit()
        
        # Testar novamente
        result5 = Dossie.query.filter_by(situacao='ativo').all()
        print(f"Após redefinir - filter_by(situacao='ativo'): {len(result5)} resultados")
        
        if result5:
            print("✅ Dossiê encontrado após correção!")
        else:
            print("❌ Ainda não encontrado. Verificando estrutura da tabela...")
            
            # Verificar estrutura da tabela
            from sqlalchemy import text
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dossies' AND column_name = 'situacao';"))
                for row in result:
                    print(f"Coluna situacao: {row[0]} - Tipo: {row[1]}")
                
                # Verificar dados diretamente no banco
                result = conn.execute(text("SELECT id, situacao, length(situacao) FROM dossies;"))
                for row in result:
                    print(f"ID: {row[0]}, Situacao: '{row[1]}', Length: {row[2]}")
    else:
        print("Nenhum dossiê encontrado!")
