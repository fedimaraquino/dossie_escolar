#!/usr/bin/env python3
# test_anexo.py - Teste para anexos

from models import *
from app import create_app
import os

app = create_app()

with app.app_context():
    # Buscar dossiê existente
    dossie = Dossie.query.first()
    if not dossie:
        print("Nenhum dossiê encontrado")
        exit()
    
    print(f"Dossiê encontrado: {dossie.n_dossie} - {dossie.nome}")
    
    # Criar pasta de anexos se não existir
    upload_folder = 'uploads/anexos'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Pasta criada: {upload_folder}")
    
    # Criar arquivo de teste
    test_file = os.path.join(upload_folder, 'teste_historico.txt')
    with open(test_file, 'w') as f:
        f.write('Este é um arquivo de teste para o histórico escolar')
    
    # Criar anexo no banco
    anexo = Anexo(
        dossie_id=dossie.id_dossie,
        nome='teste_historico.txt',
        nome_personalizado='Histórico Escolar',
        caminho=test_file,
        tamanho=os.path.getsize(test_file),
        tipo_arquivo='txt',
        usuario_upload_id=1  # Admin
    )
    
    db.session.add(anexo)
    db.session.commit()
    
    print(f"Anexo criado: {anexo.nome_personalizado} ({anexo.nome})")
    print(f"Dossiê {dossie.n_dossie} agora tem {len(dossie.anexos)} anexo(s)")
