#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Controle de Dossiê Escolar
"""

import os
import sys

def install_dependencies():
    """Instala as dependências do projeto"""
    print("Instalando dependências...")
    os.system("pip install -r requirements.txt")

def run_app():
    """Executa a aplicação"""
    print("Iniciando o Sistema de Controle de Dossiê Escolar...")
    print("Acesse: http://localhost:5000")
    print("Login padrão: admin@escola.com / admin123")
    print("-" * 50)
    
    # Importar e executar a aplicação
    from app import app
    app.run(debug=True, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install_dependencies()
    else:
        run_app()
