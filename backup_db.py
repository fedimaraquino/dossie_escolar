#!/usr/bin/env python3
# backup_db.py - Script para backup e restore do banco de dados

import os
import shutil
from datetime import datetime

DB_FILE = 'dossie_system.db'
BACKUP_DIR = 'backups'

def criar_backup():
    """Cria backup do banco de dados"""
    if not os.path.exists(DB_FILE):
        print("❌ Banco de dados não encontrado!")
        return False
    
    # Criar pasta de backup se não existir
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Nome do backup com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.db'
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    # Copiar arquivo
    shutil.copy2(DB_FILE, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    
    # Manter apenas os 10 backups mais recentes
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_')])
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
            print(f"🗑️  Backup antigo removido: {old_backup}")
    
    return True

def listar_backups():
    """Lista todos os backups disponíveis"""
    if not os.path.exists(BACKUP_DIR):
        print("❌ Pasta de backups não encontrada!")
        return []
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_')])
    
    if not backups:
        print("❌ Nenhum backup encontrado!")
        return []
    
    print("📋 Backups disponíveis:")
    for i, backup in enumerate(backups, 1):
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
        print(f"  {i}. {backup} ({size} bytes) - {mtime.strftime('%d/%m/%Y %H:%M:%S')}")
    
    return backups

def restaurar_backup(backup_name):
    """Restaura um backup específico"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup não encontrado: {backup_name}")
        return False
    
    # Fazer backup do banco atual antes de restaurar
    if os.path.exists(DB_FILE):
        current_backup = f'backup_before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(DB_FILE, os.path.join(BACKUP_DIR, current_backup))
        print(f"💾 Backup do banco atual criado: {current_backup}")
    
    # Restaurar backup
    shutil.copy2(backup_path, DB_FILE)
    print(f"✅ Banco restaurado de: {backup_name}")
    return True

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("📖 Uso:")
        print("  python backup_db.py criar     - Criar backup")
        print("  python backup_db.py listar    - Listar backups")
        print("  python backup_db.py restaurar <nome_backup> - Restaurar backup")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == 'criar':
        criar_backup()
    elif comando == 'listar':
        listar_backups()
    elif comando == 'restaurar':
        if len(sys.argv) < 3:
            backups = listar_backups()
            if backups:
                print("\n💡 Use: python backup_db.py restaurar <nome_backup>")
        else:
            backup_name = sys.argv[2]
            restaurar_backup(backup_name)
    else:
        print("❌ Comando inválido!")

if __name__ == '__main__':
    main()
