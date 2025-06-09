#!/usr/bin/env python3
"""
Script para criar configurações de exemplo
"""

from app import create_app

def criar_configuracoes_exemplo():
    """Criar configurações de exemplo"""
    print("⚙️ CRIANDO CONFIGURAÇÕES DE EXEMPLO")
    print("=" * 40)
    
    try:
        app = create_app()
        
        with app.app_context():
            from models import db, ConfiguracaoEscola, Escola
            
            # Verificar se já existem configurações
            configs_existentes = ConfiguracaoEscola.query.count()
            print(f"📊 Configurações existentes: {configs_existentes}")
            
            if configs_existentes > 0:
                print("ℹ️  Já existem configurações no sistema")
                
                # Mostrar configurações existentes
                configs = ConfiguracaoEscola.query.all()
                for config in configs:
                    escola_nome = config.escola.nome if config.escola else "Global"
                    print(f"   - {escola_nome}: {config.chave} = {config.valor}")
                
                return True
            
            # Buscar escolas
            escolas = Escola.query.all()
            print(f"🏫 Escolas encontradas: {len(escolas)}")
            
            # Configurações globais
            configuracoes_globais = [
                {
                    'chave': 'sistema_manutencao',
                    'valor': 'false',
                    'tipo': 'boolean',
                    'descricao': 'Sistema em modo de manutenção'
                },
                {
                    'chave': 'backup_automatico',
                    'valor': 'true',
                    'tipo': 'boolean',
                    'descricao': 'Backup automático habilitado'
                },
                {
                    'chave': 'logs_retencao_dias',
                    'valor': '90',
                    'tipo': 'integer',
                    'descricao': 'Dias para retenção de logs'
                },
                {
                    'chave': 'max_anexos_por_dossie',
                    'valor': '10',
                    'tipo': 'integer',
                    'descricao': 'Máximo de anexos por dossiê'
                },
                {
                    'chave': 'email_notificacoes',
                    'valor': 'admin@sistema.com',
                    'tipo': 'string',
                    'descricao': 'Email para notificações do sistema'
                }
            ]
            
            print("\n📝 Criando configurações globais...")
            for config_data in configuracoes_globais:
                config = ConfiguracaoEscola(
                    escola_id=None,  # Global
                    chave=config_data['chave'],
                    valor=config_data['valor'],
                    tipo=config_data['tipo'],
                    descricao=config_data['descricao']
                )
                db.session.add(config)
                print(f"   ✅ {config_data['chave']}")
            
            # Configurações específicas por escola
            configuracoes_escola = [
                {
                    'chave': 'horario_funcionamento',
                    'valor': '07:00-17:00',
                    'tipo': 'string',
                    'descricao': 'Horário de funcionamento da escola'
                },
                {
                    'chave': 'permite_emprestimo_externo',
                    'valor': 'true',
                    'tipo': 'boolean',
                    'descricao': 'Permite empréstimo de dossiês para externos'
                },
                {
                    'chave': 'dias_limite_emprestimo',
                    'valor': '15',
                    'tipo': 'integer',
                    'descricao': 'Dias limite para empréstimo de dossiês'
                },
                {
                    'chave': 'responsavel_dossies',
                    'valor': 'Secretaria',
                    'tipo': 'string',
                    'descricao': 'Setor responsável pelos dossiês'
                }
            ]
            
            print(f"\n🏫 Criando configurações para {len(escolas)} escola(s)...")
            for escola in escolas:
                print(f"\n   📍 {escola.nome}:")
                for config_data in configuracoes_escola:
                    config = ConfiguracaoEscola(
                        escola_id=escola.id,
                        chave=config_data['chave'],
                        valor=config_data['valor'],
                        tipo=config_data['tipo'],
                        descricao=config_data['descricao']
                    )
                    db.session.add(config)
                    print(f"      ✅ {config_data['chave']}")
            
            # Salvar todas as configurações
            db.session.commit()
            
            # Verificar resultado
            total_configs = ConfiguracaoEscola.query.count()
            configs_globais = ConfiguracaoEscola.query.filter_by(escola_id=None).count()
            configs_escolas = ConfiguracaoEscola.query.filter(ConfiguracaoEscola.escola_id.isnot(None)).count()
            
            print(f"\n📊 Resultado:")
            print(f"   Total de configurações: {total_configs}")
            print(f"   Configurações globais: {configs_globais}")
            print(f"   Configurações por escola: {configs_escolas}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_pagina_configuracoes():
    """Testar página de configurações"""
    print("\n🧪 TESTANDO PÁGINA DE CONFIGURAÇÕES")
    print("=" * 40)
    
    try:
        app = create_app()
        
        with app.app_context():
            with app.test_client() as client:
                # Simular login de admin
                with client.session_transaction() as sess:
                    sess['user_id'] = 1
                    sess['user_name'] = 'Admin Sistema'
                    sess['user_email'] = 'admin@sistema.com'
                    sess['user_perfil'] = 'Administrador Geral'
                
                # Testar rota de configurações
                response = client.get('/admin/configuracoes')
                
                print(f"📊 Status da resposta: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Página carregada com sucesso")
                    
                    data = response.get_data(as_text=True)
                    
                    if 'Configurações do Sistema' in data:
                        print("✅ Título presente")
                    
                    if 'Configurações Globais' in data:
                        print("✅ Seção de configurações globais presente")
                    
                    if 'Configurações por Escola' in data:
                        print("✅ Seção de configurações por escola presente")
                    
                    return True
                else:
                    print(f"❌ Erro na página: {response.status_code}")
                    return False
                    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("⚙️ CONFIGURAÇÃO DO SISTEMA")
    print("=" * 50)
    
    # 1. Criar configurações de exemplo
    success1 = criar_configuracoes_exemplo()
    
    # 2. Testar página
    success2 = testar_pagina_configuracoes()
    
    if success1 and success2:
        print("\n🎉 CONFIGURAÇÕES CRIADAS E TESTADAS!")
        print("\n🌐 Acesse:")
        print("   http://localhost:5000/admin/configuracoes")
        print("\n📋 Menu Administração agora funciona:")
        print("   ✅ Logs de Auditoria")
        print("   ✅ Configurações")
    else:
        print("\n⚠️  Alguns problemas encontrados")
        print(f"   Criação: {'✅' if success1 else '❌'}")
        print(f"   Teste: {'✅' if success2 else '❌'}")
