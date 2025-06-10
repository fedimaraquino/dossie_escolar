#!/usr/bin/env python3
"""
Script para criar configurações padrão do sistema
Executa na inicialização ou setup
"""

from app import create_app
from models import db
from models.configuracao_avancada import (
    ConfiguracaoSistema, ConfigScope, ConfigType, ConfigCategory
)

def criar_configuracoes_padrao():
    """Cria todas as configurações padrão do sistema"""
    
    configuracoes = [
        # SEGURANÇA
        {
            'chave': 'security.password.min_length',
            'nome_exibicao': 'Tamanho Mínimo da Senha',
            'descricao': 'Número mínimo de caracteres para senhas',
            'categoria': ConfigCategory.SECURITY,
            'tipo': ConfigType.INTEGER,
            'valor': '8',
            'valor_padrao': '8',
            'valor_minimo': 6,
            'valor_maximo': 50,
            'obrigatoria': True
        },
        {
            'chave': 'security.session.timeout_minutes',
            'nome_exibicao': 'Timeout de Sessão (minutos)',
            'descricao': 'Tempo limite para sessões inativas',
            'categoria': ConfigCategory.SECURITY,
            'tipo': ConfigType.INTEGER,
            'valor': '30',
            'valor_padrao': '30',
            'valor_minimo': 5,
            'valor_maximo': 480
        },
        {
            'chave': 'security.login.max_attempts',
            'nome_exibicao': 'Máximo de Tentativas de Login',
            'descricao': 'Número máximo de tentativas antes do bloqueio',
            'categoria': ConfigCategory.SECURITY,
            'tipo': ConfigType.INTEGER,
            'valor': '5',
            'valor_padrao': '5',
            'valor_minimo': 3,
            'valor_maximo': 10
        },
        {
            'chave': 'security.audit.log_all_actions',
            'nome_exibicao': 'Log de Todas as Ações',
            'descricao': 'Registrar todas as ações dos usuários',
            'categoria': ConfigCategory.SECURITY,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true',
            'obrigatoria': True
        },
        
        # DOSSIÊS
        {
            'chave': 'dossie.files.max_size_mb',
            'nome_exibicao': 'Tamanho Máximo de Arquivo (MB)',
            'descricao': 'Tamanho máximo permitido para arquivos anexados',
            'categoria': ConfigCategory.DOSSIE,
            'tipo': ConfigType.INTEGER,
            'valor': '10',
            'valor_padrao': '10',
            'valor_minimo': 1,
            'valor_maximo': 100
        },
        {
            'chave': 'dossie.files.allowed_types',
            'nome_exibicao': 'Tipos de Arquivo Permitidos',
            'descricao': 'Extensões de arquivo permitidas (JSON array)',
            'categoria': ConfigCategory.DOSSIE,
            'tipo': ConfigType.JSON,
            'valor': '["pdf", "doc", "docx", "jpg", "png", "jpeg"]',
            'valor_padrao': '["pdf", "doc", "docx", "jpg", "png", "jpeg"]'
        },
        {
            'chave': 'dossie.workflow.require_approval',
            'nome_exibicao': 'Requer Aprovação para Alterações',
            'descricao': 'Alterações em dossiês precisam de aprovação',
            'categoria': ConfigCategory.DOSSIE,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true'
        },
        {
            'chave': 'dossie.retention.years',
            'nome_exibicao': 'Período de Retenção (anos)',
            'descricao': 'Tempo de retenção obrigatória dos dossiês',
            'categoria': ConfigCategory.DOSSIE,
            'tipo': ConfigType.INTEGER,
            'valor': '7',
            'valor_padrao': '7',
            'valor_minimo': 1,
            'valor_maximo': 50
        },
        
        # ESCOLA
        {
            'chave': 'escola.horario_funcionamento',
            'nome_exibicao': 'Horário de Funcionamento',
            'descricao': 'Horário padrão de funcionamento da escola',
            'categoria': ConfigCategory.ESCOLA,
            'escopo': ConfigScope.ESCOLA,
            'tipo': ConfigType.STRING,
            'valor': '07:00-17:00',
            'valor_padrao': '07:00-17:00',
            'validacao_regex': r'^\d{2}:\d{2}-\d{2}:\d{2}$'
        },
        {
            'chave': 'escola.permite_emprestimo_externo',
            'nome_exibicao': 'Permite Empréstimo Externo',
            'descricao': 'Permite empréstimo de dossiês para pessoas externas',
            'categoria': ConfigCategory.ESCOLA,
            'escopo': ConfigScope.ESCOLA,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'false',
            'valor_padrao': 'false'
        },
        
        # INTERFACE
        {
            'chave': 'ui.theme',
            'nome_exibicao': 'Tema da Interface',
            'descricao': 'Tema padrão da interface do usuário',
            'categoria': ConfigCategory.USER_INTERFACE,
            'escopo': ConfigScope.USUARIO,
            'tipo': ConfigType.STRING,
            'valor': 'light',
            'valor_padrao': 'light',
            'opcoes_validas': '["light", "dark", "auto"]'
        },
        {
            'chave': 'ui.items_per_page',
            'nome_exibicao': 'Itens por Página',
            'descricao': 'Número padrão de itens exibidos por página',
            'categoria': ConfigCategory.USER_INTERFACE,
            'escopo': ConfigScope.USUARIO,
            'tipo': ConfigType.INTEGER,
            'valor': '25',
            'valor_padrao': '25',
            'opcoes_validas': '["10", "25", "50", "100"]'
        },
        
        # SISTEMA
        {
            'chave': 'system.cache.enabled',
            'nome_exibicao': 'Cache Habilitado',
            'descricao': 'Habilitar sistema de cache para melhor performance',
            'categoria': ConfigCategory.SYSTEM,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true',
            'requer_reinicializacao': True
        },
        {
            'chave': 'system.maintenance.auto_cleanup',
            'nome_exibicao': 'Limpeza Automática',
            'descricao': 'Executar limpeza automática de logs e arquivos temporários',
            'categoria': ConfigCategory.SYSTEM,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true'
        },
        
        # BACKUP
        {
            'chave': 'backup.auto_enabled',
            'nome_exibicao': 'Backup Automático',
            'descricao': 'Executar backups automáticos do sistema',
            'categoria': ConfigCategory.BACKUP,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true'
        },
        {
            'chave': 'backup.frequency',
            'nome_exibicao': 'Frequência do Backup',
            'descricao': 'Frequência de execução dos backups automáticos',
            'categoria': ConfigCategory.BACKUP,
            'tipo': ConfigType.STRING,
            'valor': 'daily',
            'valor_padrao': 'daily',
            'opcoes_validas': '["hourly", "daily", "weekly", "monthly"]'
        },
        
        # NOTIFICAÇÕES
        {
            'chave': 'notification.email.enabled',
            'nome_exibicao': 'Notificações por Email',
            'descricao': 'Habilitar envio de notificações por email',
            'categoria': ConfigCategory.NOTIFICATION,
            'tipo': ConfigType.BOOLEAN,
            'valor': 'true',
            'valor_padrao': 'true'
        },
        {
            'chave': 'notification.email.sender',
            'nome_exibicao': 'Email Remetente',
            'descricao': 'Endereço de email usado como remetente',
            'categoria': ConfigCategory.NOTIFICATION,
            'tipo': ConfigType.EMAIL,
            'valor': 'noreply@escola.edu.br',
            'valor_padrao': 'noreply@escola.edu.br',
            'validacao_regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
    ]
    
    print("🔧 Criando configurações padrão do sistema...")
    
    criadas = 0
    atualizadas = 0
    
    for config_data in configuracoes:
        # Verificar se já existe
        existing = ConfiguracaoSistema.query.filter_by(
            chave=config_data['chave'],
            escopo=config_data.get('escopo', ConfigScope.GLOBAL)
        ).first()
        
        if existing:
            print(f"   ℹ️  {config_data['chave']} já existe")
            atualizadas += 1
            continue
        
        # Criar nova configuração
        config = ConfiguracaoSistema(
            chave=config_data['chave'],
            nome_exibicao=config_data['nome_exibicao'],
            descricao=config_data['descricao'],
            categoria=config_data['categoria'],
            escopo=config_data.get('escopo', ConfigScope.GLOBAL),
            tipo=config_data['tipo'],
            valor=config_data['valor'],
            valor_padrao=config_data['valor_padrao'],
            validacao_regex=config_data.get('validacao_regex'),
            valor_minimo=config_data.get('valor_minimo'),
            valor_maximo=config_data.get('valor_maximo'),
            opcoes_validas=config_data.get('opcoes_validas'),
            obrigatoria=config_data.get('obrigatoria', False),
            requer_reinicializacao=config_data.get('requer_reinicializacao', False)
        )
        
        db.session.add(config)
        print(f"   ✅ {config_data['chave']}")
        criadas += 1
    
    db.session.commit()
    
    print(f"\n📊 Resultado:")
    print(f"   Configurações criadas: {criadas}")
    print(f"   Configurações existentes: {atualizadas}")
    print(f"   Total: {criadas + atualizadas}")
    
    return criadas, atualizadas

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("🚀 SETUP DE CONFIGURAÇÕES PADRÃO")
        print("=" * 50)
        
        try:
            # Criar tabelas se não existirem
            db.create_all()
            
            # Criar configurações
            criadas, atualizadas = criar_configuracoes_padrao()
            
            print(f"\n🎉 Setup concluído com sucesso!")
            print(f"✅ {criadas} configurações criadas")
            print(f"ℹ️  {atualizadas} configurações já existiam")
            
        except Exception as e:
            print(f"❌ Erro durante o setup: {e}")
            import traceback
            traceback.print_exc()
