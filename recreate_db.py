#!/usr/bin/env python3
"""
Script para recriar o banco de dados com a estrutura correta
"""
import os
from app import create_app
from models import db, Perfil, Escola, Usuario, Cidade

def recreate_database():
    """Recria o banco de dados do zero"""
    
    # Remover banco existente se houver
    db_file = 'dossie_escolar.db'
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️ Banco de dados {db_file} removido")
    
    # Criar aplicação
    app = create_app()
    
    with app.app_context():
        # Dropar e recriar todas as tabelas
        db.drop_all()
        db.create_all()
        print("📊 Tabelas recriadas com sucesso")
        
        # Criar perfis padrão se não existirem
        if not Perfil.query.first():
            perfis = [
                Perfil(perfil='Administrador Geral'),
                Perfil(perfil='Administrador da Escola'),
                Perfil(perfil='Operador'),
                Perfil(perfil='Consulta')
            ]

            for perfil in perfis:
                db.session.add(perfil)

            db.session.commit()
            print("✅ Perfis criados")
        else:
            print("ℹ️ Perfis já existem")
        
        # Criar cidades de exemplo se não existirem
        if not Cidade.query.first():
            cidades = [
                Cidade(nome='São Paulo', uf='SP', pais='Brasil'),
                Cidade(nome='Rio de Janeiro', uf='RJ', pais='Brasil'),
                Cidade(nome='Belo Horizonte', uf='MG', pais='Brasil'),
                Cidade(nome='Salvador', uf='BA', pais='Brasil'),
                Cidade(nome='Brasília', uf='DF', pais='Brasil')
            ]

            for cidade in cidades:
                db.session.add(cidade)

            db.session.commit()
            print("✅ Cidades criadas")
        else:
            print("ℹ️ Cidades já existem")
        
        # Criar escola de exemplo se não existir
        if not Escola.query.first():
            escola = Escola(
                nome='Escola Municipal Exemplo',
                endereco='Rua das Flores, 123',
                id_cidade=1,  # São Paulo
                situacao='ativa',
                inep='12345678',
                email='escola@exemplo.com',
                uf='SP',
                cnpj='12345678000199'
            )

            db.session.add(escola)
            db.session.commit()
            print("✅ Escola criada")
        else:
            print("ℹ️ Escola já existe")
        
        # Criar usuário administrador se não existir
        if not Usuario.query.filter_by(email='admin@sistema.com').first():
            admin = Usuario(
                nome='Administrador do Sistema',
                email='admin@sistema.com',
                cpf='12345678901',
                perfil_id=1,  # Administrador Geral
                escola_id=1,
                situacao='ativo'
            )
            admin.set_password('admin123')

            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário administrador criado")
        else:
            print("ℹ️ Usuário administrador já existe")
        
        print("\n🎉 Banco de dados recriado com sucesso!")
        print("📋 Dados de acesso:")
        print("   Email: admin@sistema.com")
        print("   Senha: admin123")

if __name__ == '__main__':
    recreate_database()
