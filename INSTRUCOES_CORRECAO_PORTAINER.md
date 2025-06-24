# 🚨 CORREÇÃO URGENTE - TIMEOUT DO PORTAINER

## 📋 RESUMO EXECUTIVO

**Problema**: Portainer com timeout de segurança no servidor remoto  
**Solução**: Reinicialização via script automatizado  
**Tempo estimado**: 5-10 minutos  
**Impacto**: Zero downtime para aplicação principal  

---

## 🔧 COMANDOS PARA EXECUTAR NO SERVIDOR REMOTO

### 1. Conectar ao Servidor
```bash
ssh root@10.0.1.185
# ou
ssh usuario@IP_DO_SERVIDOR
```

### 2. Navegar para o Projeto
```bash
cd /caminho/para/dossie_novo
ls -la docker-compose.portainer.yml
```

### 3. Executar Correção
```bash
chmod +x fix-portainer.sh
./fix-portainer.sh
```

### 4. Verificar Resultado
```bash
docker service ls | grep portainer
curl -f http://localhost:9000
```

---

## 🌐 URLs DE ACESSO

| Serviço | URL |
|---------|-----|
| **Portainer** | http://10.0.1.185:9000 |
| **Sistema** | http://10.0.1.185 |
| **Traefik** | http://10.0.1.185:8080 |

---

## ⚡ CORREÇÃO RÁPIDA (ALTERNATIVA)

Se o script não funcionar, execute manualmente:

```bash
# 1. Verificar status
docker service ls

# 2. Forçar restart
docker service update --force portainer_portainer

# 3. Se falhar, recriar
docker stack rm portainer
sleep 15
docker stack deploy -c docker-compose.portainer.yml portainer
```

---

## ✅ INDICADORES DE SUCESSO

- ✅ `docker service ls` mostra `portainer_portainer 1/1`
- ✅ Acesso web em http://10.0.1.185:9000
- ✅ Primeira tela do Portainer aparece
- ✅ Sistema principal continua funcionando

---

## 🆘 EM CASO DE PROBLEMAS

### Verificar Logs:
```bash
docker service logs portainer_portainer --tail 20
```

### Verificar Rede:
```bash
docker network ls | grep traefik-public
```

### Limpar Recursos:
```bash
docker system prune -f
```

---

## 📞 SUPORTE

**Documentação completa**: `step-by-step/guia_correcao_portainer_remoto.md`  
**Script de correção**: `fix-portainer.sh`  
**Configuração**: `docker-compose.portainer.yml`  

---

**⚠️ IMPORTANTE**: Execute no servidor remoto, não nesta máquina local!  
**🕐 Tempo**: 5-10 minutos para correção completa  
**🔄 Impacto**: Apenas Portainer afetado, sistema principal continua funcionando 