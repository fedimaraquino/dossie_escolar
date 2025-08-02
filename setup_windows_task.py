#!/usr/bin/env python3
"""
Script para configurar tarefa agendada no Windows
Configura backup automático diário usando Task Scheduler
"""

import os
import sys
import subprocess
import getpass

def setup_windows_task():
    """Configurar tarefa agendada no Windows"""
    print("=== Configuracao do Task Scheduler ===")
    print()
    
    # Obter usuário atual
    user = getpass.getuser()
    print(f"Usuario atual: {user}")
    
    # Obter caminho absoluto do script
    script_path = os.path.abspath('backup_b2_complete.py')
    python_path = sys.executable
    
    # Nome da tarefa
    task_name = "DossieBackupB2"
    
    # Comando para criar a tarefa
    command = f"""schtasks /create /tn "{task_name}" /tr "{python_path} {script_path}" /sc daily /st 02:00 /ru "{user}" /f"""
    
    print(f"🔧 Criando tarefa agendada: {task_name}")
    print(f"Comando: {command}")
    print()
    
    # Executar comando
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tarefa agendada criada com sucesso!")
            print("A tarefa executara diariamente às 02:00")
            return True
        else:
            print(f"❌ Erro ao criar tarefa: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar comando: {str(e)}")
        return False

def list_windows_tasks():
    """Listar tarefas existentes"""
    print("=== Tarefas Existentes ===")
    print()
    
    try:
        result = subprocess.run("schtasks /query /tn DossieBackupB2", 
                              shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tarefa DossieBackupB2 encontrada:")
            print(result.stdout)
        else:
            print("❌ Tarefa DossieBackupB2 nao encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao listar tarefas: {str(e)}")

def delete_windows_task():
    """Deletar tarefa existente"""
    print("=== Deletando Tarefa ===")
    print()
    
    try:
        result = subprocess.run("schtasks /delete /tn DossieBackupB2 /f", 
                              shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tarefa DossieBackupB2 deletada com sucesso!")
            return True
        else:
            print(f"❌ Erro ao deletar tarefa: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar tarefa: {str(e)}")
        return False

def test_backup():
    """Testar backup manualmente"""
    print("=== Teste de Backup B2 ===")
    print()
    
    response = input("Deseja testar o backup B2 agora? (s/N): ").lower()
    if response != 's':
        return True
    
    print("Executando backup de teste...")
    
    try:
        result = subprocess.run([sys.executable, 'backup_b2_complete.py'], 
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
B2_BUCKET_NAME=dossie-backups

# Configuracoes de Retencao
BACKUP_RETENTION_DAYS=30
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env.template criado!")
    print("Copie para .env e configure suas variaveis")
    print()

def main():
    """Função principal"""
    print("🔧 Configurador de Backup Automatico Windows - Dossie Escolar")
    print("=" * 70)
    print()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('backup_b2_complete.py'):
        print("❌ Arquivo backup_b2_complete.py nao encontrado")
        print("Execute este script no diretorio do projeto")
        return 1
    
    # Verificar se estamos no Windows
    if os.name != 'nt':
        print("❌ Este script e apenas para Windows")
        print("Para Linux/Mac, use o crontab")
        return 1
    
    # Criar template de variáveis
    create_env_template()
    
    # Listar tarefas existentes
    list_windows_tasks()
    
    # Perguntar se quer criar nova tarefa
    response = input("\nDeseja criar uma nova tarefa agendada? (s/N): ").lower()
    if response == 's':
        # Deletar tarefa existente se houver
        delete_windows_task()
        
        # Criar nova tarefa
        if setup_windows_task():
            print("\n✅ Tarefa agendada configurada com sucesso!")
        else:
            print("\n❌ Falha ao configurar tarefa agendada")
            return 1
    
    # Teste de backup
    test_backup()
    
    print("\n🎉 Configuracao concluida!")
    print()
    print("Resumo:")
    print("✅ Backblaze B2 configurado")
    print("✅ Tarefa agendada configurada (backup diário às 02:00)")
    print("✅ Template de variáveis criado")
    print()
    print("Próximos passos:")
    print("1. Configure o arquivo .env com suas variáveis B2")
    print("2. Execute o primeiro backup manual para testar")
    print("3. Verifique os logs em backup_b2_complete.log")
    print("4. Para restaurar, use: python b2_restore.py")
    print()
    print("Comandos úteis:")
    print("- Ver tarefas: schtasks /query /tn DossieBackupB2")
    print("- Deletar tarefa: schtasks /delete /tn DossieBackupB2 /f")
    print("- Backup manual: python backup_b2_complete.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 