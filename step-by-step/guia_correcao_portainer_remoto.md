# Guia de Correção do Timeout do Portainer - Servidor Remoto

## Data da Implementação
**27/01/2025**

## Problema Identificado
O Portainer apresentou timeout por motivos de segurança no servidor remoto, necessitando reinicialização para reativar o acesso.

## Arquivos Envolvidos
- `docker-compose.portainer.yml` - Configuração do Portainer
- `fix-portainer.sh` - Script de correção automatizada
- `step-by-step/guia_correcao_portainer_remoto.md` - Este guia

## Visão Geral da Solução
Processo passo-a-passo para conectar ao servidor remoto e executar a correção do timeout do Portainer.

## Instruções para Correção Remota

### Passo 1: Conectar ao Servidor Remoto

#### Via SSH:
```bash
# Conectar via SSH ao servidor
ssh usuario@IP_DO_SERVIDOR

# Exemplo:
ssh root@10.0.1.185
```

#### Via Terminal Web (se disponível):
- Acesse o terminal web do servidor
- Navegue até o diretório do projeto

### Passo 2: Navegar para o Diretório do Projeto

```bash
# Navegar para o diretório do projeto
cd /caminho/para/dossie_novo

# Verificar se está no diretório correto
ls -la docker-compose.portainer.yml
```

### Passo 3: Verificar Status Atual

```bash
# Verificar se o Docker Swarm está ativo
docker info | grep Swarm

# Verificar serviços rodando
docker service ls

# Verificar se o Portainer está rodando
docker service ls | grep portainer
```

### Passo 4: Executar o Script de Correção

```bash
# Dar permissão de execução ao script
chmod +x fix-portainer.sh

# Executar o script de correção
./fix-portainer.sh
```

### Passo 5: Monitorar a Execução

O script irá:
1. ✅ Verificar arquivos necessários
2. ✅ Criar diretórios Traefik
3. ✅ Verificar/criar rede traefik-public
4. ✅ Tentar restart simples do Portainer
5. ✅ Se falhar, remover e recriar completamente
6. ✅ Validar funcionamento
7. ✅ Exibir status final

### Passo 6: Verificar Resultado

```bash
# Verificar se o Portainer está rodando
docker service ls | grep portainer

# Verificar logs do Portainer
docker service logs portainer_portainer --tail 10

# Testar acesso web
curl -f http://localhost:9000
```

## URLs de Acesso Após Correção

### Portainer:
- **URL Direta**: http://IP_DO_SERVIDOR:9000
- **Via Traefik**: http://IP_DO_SERVIDOR/portainer

### Sistema Principal:
- **URL**: http://IP_DO_SERVIDOR

### Traefik Dashboard:
- **URL**: http://IP_DO_SERVIDOR:8080

## Configuração Inicial do Portainer

Após a correção, na primeira tela do Portainer:

1. **Criar usuário admin**:
   - Username: `admin` (ou seu preferido)
   - Password: `senha_segura_123` (ou sua preferida)

2. **Selecionar ambiente**:
   - Escolher: **"Docker Swarm"**

3. **Configurar endpoint**:
   - Selecionar: **"Local Docker Environment"**

## Comandos de Troubleshooting

### Se o Script Falhar:

```bash
# Verificar logs detalhados
docker service logs portainer_portainer --tail 50

# Verificar rede
docker network ls | grep traefik-public

# Verificar volumes
docker volume ls | grep portainer

# Limpar recursos órfãos
docker system prune -f
```

### Correção Manual (se necessário):

```bash
# Remover stack do Portainer
docker stack rm portainer

# Aguardar remoção
sleep 15

# Recriar stack
docker stack deploy -c docker-compose.portainer.yml portainer

# Verificar status
docker service ls
```

### Verificar Configuração:

```bash
# Verificar configuração do serviço
docker service inspect portainer_portainer

# Verificar rede overlay
docker network inspect traefik-public

# Verificar volumes
docker volume inspect portainer_data
```

## Indicadores de Sucesso

### ✅ Portainer Funcionando:
- Serviço com status "1/1"
- Acesso web em http://IP:9000
- Logs sem erros de timeout
- Integração com Traefik ativa

### ✅ Sistema Completo:
- Portainer acessível
- Traefik funcionando
- Aplicação principal rodando
- SSL funcionando (se configurado)

## Problemas Comuns e Soluções

### 1. Timeout Persistente:
```bash
# Forçar restart completo
docker service update --force portainer_portainer
```

### 2. Rede Não Encontrada:
```bash
# Criar rede manualmente
docker network create --driver overlay traefik-public
```

### 3. Volume Corrompido:
```bash
# Remover volume e recriar
docker volume rm portainer_data
docker stack deploy -c docker-compose.portainer.yml portainer
```

### 4. Porta Ocupada:
```bash
# Verificar o que está usando a porta 9000
netstat -tulpn | grep :9000
```

## Monitoramento Contínuo

### Comandos de Monitoramento:
```bash
# Status dos serviços
watch -n 5 'docker service ls'

# Logs em tempo real
docker service logs -f portainer_portainer

# Uso de recursos
docker stats
```

### Configuração de Alerta:
- Monitorar logs de timeout
- Configurar notificações de status
- Implementar health checks

## Próximos Passos

### Imediatos:
1. ✅ Executar correção no servidor remoto
2. ✅ Verificar acesso ao Portainer
3. ✅ Validar funcionamento do sistema

### Preventivos:
1. **Configurar backup automático** dos dados do Portainer
2. **Implementar monitoramento** de timeout
3. **Documentar procedimento** de recuperação

### Melhorias:
1. **Automatizar detecção** de problemas
2. **Implementar notificações** de status
3. **Criar dashboard** de monitoramento

## Contatos e Suporte

### Em caso de problemas:
1. **Verificar logs**: `docker service logs portainer_portainer`
2. **Consultar documentação**: Esta pasta step-by-step
3. **Executar troubleshooting**: Comandos listados acima

### Backup de Configuração:
- Arquivo: `docker-compose.portainer.yml`
- Script: `fix-portainer.sh`
- Documentação: Esta pasta step-by-step

---

**Status**: ✅ Guia Criado  
**Última atualização**: 27/01/2025  
**Próxima revisão**: Após execução da correção no servidor remoto 