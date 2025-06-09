"""
Configurações do Sistema de Controle de Dossiê Escolar
"""

import os
import secrets

class Config:
    """Configurações base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configurações de paginação
    POSTS_PER_PAGE = 10
    
    # Configurações de upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    # PostgreSQL para desenvolvimento
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        os.environ.get('DATABASE_URL') or \
        'postgresql://dossie:fep09151@localhost/dossie_escola'

    # Fallback para SQLite se PostgreSQL não estiver disponível
    SQLALCHEMY_FALLBACK_URI = 'sqlite:///dossie_escolar.db'

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    # PostgreSQL para produção
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://dossie:fep09151@localhost/dossie_escola'

class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
