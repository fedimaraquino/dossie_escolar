#!/usr/bin/env python3
"""
Script para debugar a listagem de dossiês da escola Lindalva
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from models import db, Dossie, Escola, Usuario
    
    print("🔍 Debugando dossiês da escola Lindalva...")
    print("=" * 60)
    
    # Criar aplicação
    app = create_app()
    
    with app.app_context():
        # 1. Verificar escola Lindalva
        escola_lindalva = Escola.query.filter(Escola.nome.like('%LINDALVA%')).first()
        if not escola_lindalva:
            print("❌ Escola Lindalva não encontrada!")
        else:
            print(f"🏫 Escola encontrada: {escola_lindalva.nome} (ID: {escola_lindalva.id})")
            
            # 2. Verificar dossiês desta escola
            dossies_lindalva = Dossie.query.filter_by(id_escola=escola_lindalva.id).all()
            print(f"📊 Total de dossiês na escola Lindalva: {len(dossies_lindalva)}")
            
            if dossies_lindalva:
                print("\n📋 Dossiês encontrados:")
                print("-" * 80)
                print(f"{'ID':<5} {'Número':<12} {'Nome':<30} {'Status':<12} {'Data Cadastro':<15}")
                print("-" * 80)
                
                for dossie in dossies_lindalva:
                    data_cadastro = dossie.dt_cadastro.strftime('%d/%m/%Y') if dossie.dt_cadastro else "N/A"
                    print(f"{dossie.id_dossie:<5} {dossie.n_dossie:<12} {dossie.nome[:28]:<30} {dossie.status:<12} {data_cadastro:<15}")
                
                print("-" * 80)
            
            # 3. Simular consulta da listagem (como se fosse admin geral)
            print("\n🔍 Simulando consulta da listagem (Admin Geral):")
            
            # Simular filtro por escola
            query = Dossie.query
            query = query.filter(Dossie.id_escola == escola_lindalva.id)
            
            # Executar consulta
            dossies_filtrados = query.all()
            print(f"📊 Dossiês retornados pelo filtro: {len(dossies_filtrados)}")
            
            if dossies_filtrados:
                print("✅ Filtro funcionando corretamente!")
            else:
                print("❌ Filtro não retornou resultados!")
                
            # 4. Verificar se há problemas com o campo id_escola
            print("\n🔍 Verificando campo id_escola:")
            todos_dossies = Dossie.query.all()
            print(f"📊 Total de dossiês no sistema: {len(todos_dossies)}")
            
            for dossie in todos_dossies:
                print(f"  • Dossiê {dossie.n_dossie}: id_escola = {dossie.id_escola}, escola = {dossie.escola.nome if dossie.escola else 'N/A'}")
                
            # 5. Verificar se há problemas com tipos de dados
            print("\n🔍 Verificando tipos de dados:")
            if dossies_lindalva:
                print(f"  • Tipo do campo id_escola: {type(dossies_lindalva[0].id_escola)}")
                print(f"  • Tipo do ID da escola: {type(escola_lindalva.id)}")
            
            # 6. Testar consulta com conversão de tipo
            print("\n🔍 Testando com conversão de tipo:")
            try:
                escola_id_int = int(escola_lindalva.id)
                query_teste = Dossie.query.filter(Dossie.id_escola == escola_id_int)
                dossies_teste = query_teste.all()
                print(f"📊 Dossiês com conversão de tipo: {len(dossies_teste)}")
            except Exception as e:
                print(f"❌ Erro na conversão: {e}")
            
    print("\n" + "=" * 60)
    print("✅ Debug concluído!")
    
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}") 