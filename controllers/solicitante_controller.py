"""
Controller para Solicitantes - Integração com app.py
"""

from flask import Blueprint

# Importar o blueprint do módulo solicitantes
from apps.solicitantes.routes import solicitantes_bp

# Exportar o blueprint para ser usado no app.py
solicitante_bp = solicitantes_bp
