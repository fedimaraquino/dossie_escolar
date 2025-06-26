from app import app
from models import Escola

with app.app_context():
    escolas = Escola.query.all()
    with open('relatorio_escolas_dossies.txt', 'w', encoding='utf-8') as f:
        f.write('Escola | ID | Qtd Dossiês\n' + '-'*40 + '\n')
        for e in escolas:
            f.write(f'{e.nome} | {e.id} | {len(e.dossies)}\n')
print('Arquivo relatorio_escolas_dossies.txt gerado com sucesso!') 