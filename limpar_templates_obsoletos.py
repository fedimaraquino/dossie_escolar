#!/usr/bin/env python3
"""
Script para limpar templates obsoletos
Remove apenas arquivos que não estão sendo usados
"""

import os
import shutil
from datetime import datetime

def limpar_templates_obsoletos():
    """Limpar templates obsoletos do sistema"""
    print("🧹 LIMPEZA DE TEMPLATES OBSOLETOS")
    print("=" * 40)
    
    # Arquivos obsoletos identificados
    arquivos_obsoletos = [
        'templates/dashboard.html',
        'templates/dashboard_completo.html', 
        'templates/index.html',
        'templates/index_completo.html',
        'templates/index_modular.html',
        'templates/login.html',
        'templates/login_completo.html',
        'templates/login_modular.html',
        'templates/escolas/listar_simples.html',
        'templates/escolas/nova_simples.html'
    ]
    
    # Criar pasta de backup
    backup_dir = f"backup_templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    removidos = 0
    nao_encontrados = 0
    
    print(f"📦 Criando backup em: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)
    
    for arquivo in arquivos_obsoletos:
        if os.path.exists(arquivo):
            try:
                # Fazer backup antes de remover
                backup_path = os.path.join(backup_dir, os.path.basename(arquivo))
                shutil.copy2(arquivo, backup_path)
                
                # Remover arquivo original
                os.remove(arquivo)
                
                print(f"   ✅ Removido: {arquivo}")
                removidos += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao remover {arquivo}: {e}")
        else:
            print(f"   ℹ️  Não encontrado: {arquivo}")
            nao_encontrados += 1
    
    print(f"\n📊 Resultado da limpeza:")
    print(f"   Arquivos removidos: {removidos}")
    print(f"   Arquivos não encontrados: {nao_encontrados}")
    print(f"   Backup criado em: {backup_dir}")
    
    # Verificar arquivos ativos
    print(f"\n✅ Arquivos principais mantidos:")
    arquivos_principais = [
        'templates/base.html',
        'templates/dashboard_novo.html',
        'templates/auth/login_novo.html'
    ]
    
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ ATENÇÃO: {arquivo} não encontrado!")
    
    print(f"\n🎯 Limpeza concluída!")
    print(f"📁 Templates organizados por pasta mantidos")
    print(f"💾 Backup disponível em: {backup_dir}")
    
    return removidos, nao_encontrados

def verificar_templates_ativos():
    """Verificar se os templates ativos estão presentes"""
    print(f"\n🔍 VERIFICAÇÃO DE TEMPLATES ATIVOS")
    print("=" * 40)
    
    templates_criticos = [
        'templates/base.html',
        'templates/dashboard_novo.html', 
        'templates/auth/login_novo.html',
        'templates/errors/404.html',
        'templates/errors/500.html',
        'templates/usuarios/perfil.html',
        'templates/admin/configuracoes/index.html'
    ]
    
    todos_ok = True
    
    for template in templates_criticos:
        if os.path.exists(template):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ FALTANDO: {template}")
            todos_ok = False
    
    if todos_ok:
        print(f"\n🎉 Todos os templates críticos estão presentes!")
    else:
        print(f"\n⚠️  ATENÇÃO: Alguns templates críticos estão faltando!")
    
    return todos_ok

if __name__ == '__main__':
    print("🚀 SCRIPT DE LIMPEZA DE TEMPLATES")
    print("=" * 50)
    
    try:
        # Verificar templates ativos primeiro
        templates_ok = verificar_templates_ativos()
        
        if templates_ok:
            # Fazer limpeza
            removidos, nao_encontrados = limpar_templates_obsoletos()
            
            print(f"\n✨ LIMPEZA CONCLUÍDA COM SUCESSO!")
            print(f"🗑️  {removidos} arquivos obsoletos removidos")
            print(f"💾 Backup criado para segurança")
            print(f"🎯 Sistema mais organizado e limpo")
            
        else:
            print(f"\n⚠️  LIMPEZA CANCELADA!")
            print(f"❌ Templates críticos estão faltando")
            print(f"🔧 Verifique a integridade do sistema primeiro")
            
    except Exception as e:
        print(f"\n❌ Erro durante a limpeza: {e}")
        import traceback
        traceback.print_exc()
