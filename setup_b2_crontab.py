#!/usr/bin/env python3
"""
Script para configurar backup automático B2
Configura crontab para executar backup diariamente
"""

import os
import sys
import subprocess
from crontab import CronTab
import getpass

def setup_b2_config():
    """Configurar Backblaze B2"""
    print("=== Configuracao do Backblaze B2 ===")
    print()
    print("Para usar o Backblaze B2, voce precisa:")
    print("1. Criar uma conta no Backblaze B2")
    print("2. Criar um bucket para backups")
    print("3. Obter Application Key ID e Application Key")
    print("4. Configurar as variaveis de ambiente")
    print()
    
    # Verificar se as variáveis estão configuradas
    b2_key_id = os.getenv('B2_APPLICATION_KEY_ID')
    b2_key = os.getenv('B2_APPLICATION_KEY')
    b2_bucket = os.getenv('B2_BUCKET_NAME')
    
    if b2_key_id and b2_key and b2_bucket:
        print("✅ Variaveis B2 configuradas!")
        print(f"   Key ID: {b2_key_id}")
        print(f"   Bucket: {b2_bucket}")
    else:
        print("❌ Variaveis B2 nao configuradas")
        print("Configure as seguintes variaveis de ambiente:")
        print("   B2_APPLICATION_KEY_ID")
        print("   B2_APPLICATION_KEY")
        print("   B2_BUCKET_NAME")
        return False
    
    return True

def setup_crontab():
    """Configurar crontab para backup automático"""
    print("=== Configuracao do Crontab ===")
    print()
    
    # Obter usuário atual
    user = getpass.getuser()
    print(f"Usuario atual: {user}")
    
    # Criar instância do crontab
    cron = CronTab(user=user)
    
    # Verificar se já existe o job
    existing_jobs = cron.find_comment('dossie-b2-backup')
    
    if existing_jobs:
        print("⚠️  Job de backup B2 ja existe no crontab")
        for job in existing_jobs:
            print(f"   {job}")
        
        response = input("Deseja substituir? (s/N): ").lower()
        if response != 's':
            print("Configuracao mantida")
            return True
        
        # Remover jobs existentes
        for job in existing_jobs:
            cron.remove(job)
    
    # Obter caminho absoluto do script
    script_path = os.path.abspath('b2_backup.py')
    python_path = sys.executable
    
    # Criar comando
    command = f"{python_path} {script_path}"
    
    # Criar job (diariamente às 02:00)
    job = cron.new(command=command, comment='dossie-b2-backup')
    job.hour.on(2)
    job.minute.on(0)
    
    # Salvar crontab
    cron.write()
    
    print("✅ Job de backup B2 configurado!")
    print(f"Comando: {command}")
    print("Horario: Diariamente às 02:00")
    print()
    
    return True

def test_backup():
    """Testar backup manualmente"""
    print("=== Teste de Backup B2 ===")
    print()
    
    response = input("Deseja testar o backup B2 agora? (s/N): ").lower()
    if response != 's':
        return True
    
    print("Executando backup de teste...")
    
    try:
        result = subprocess.run([sys.executable, 'b2_backup.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backup de teste executado com sucesso!")
            print("Logs:")
            print(result.stdout)
        else:
            print("❌ Erro no backup de teste:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Erro ao executar backup: {str(e)}")
    
    return True

def create_env_template():
    """Criar template de variáveis de ambiente"""
    print("=== Template de Variaveis de Ambiente ===")
    print()
    
    env_content = """# Configuracoes do Banco de Dados
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dossie_escolar
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Configuracoes do Backblaze B2
B2_APPLICATION_KEY_ID=005be81810e36920000000005
B2_APPLICATION_KEY=K005XwOmArA3gy7RYaaokuIGPK45Uk0
B2_BUCKET_NAME=biblioescolar

# Configuracoes de Retencao
BACKUP_RETENTION_DAYS=30
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env.template criado!")
    print("Copie para .env e configure suas variaveis")
    print()

def create_backup_dir():
    """Criar diretório de backups"""
    backup_dir = './backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Diretorio de backups criado: {backup_dir}")
    else:
        print(f"✅ Diretorio de backups ja existe: {backup_dir}")

def main():
    """Função principal"""
    print("🔧 Configurador de Backup Automatico B2 - Dossie Escolar")
    print("=" * 60)
    print()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('b2_backup.py'):
        print("❌ Arquivo b2_backup.py nao encontrado")
        print("Execute este script no diretorio do projeto")
        return 1
    
    # Setup do B2
    if not setup_b2_config():
        return 1
    
    # Criar diretório de backups
    create_backup_dir()
    
    # Criar template de variáveis
    create_env_template()
    
    # Setup do crontab
    if not setup_crontab():
        return 1
    
    # Teste de backup
    test_backup()
    
    print("🎉 Configuracao concluida!")
    print()
    print("Resumo:")
    print("✅ Backblaze B2 configurado")
    print("✅ Crontab configurado (backup diário às 02:00)")
    print("✅ Template de variáveis criado")
    print("✅ Diretório de backups criado")
    print()
    print("Próximos passos:")
    print("1. Configure o arquivo .env com suas variáveis B2")
    print("2. Execute o primeiro backup manual para testar")
    print("3. Verifique os logs em b2_backup.log")
    print("4. Para restaurar, use: python b2_restore.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 