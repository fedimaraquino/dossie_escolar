#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando deploy via Portainer...${NC}"

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker não está instalado. Por favor, instale o Docker primeiro.${NC}"
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.${NC}"
    exit 1
fi

# Criar rede se não existir
echo -e "${YELLOW}Criando redes Docker...${NC}"
docker network create traefik-public 2>/dev/null || true
docker network create app-network 2>/dev/null || true

# Construir a imagem
echo -e "${YELLOW}Construindo imagem Docker...${NC}"
docker build -t dossie-app:latest .

# Verificar se a construção foi bem sucedida
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao construir a imagem Docker.${NC}"
    exit 1
fi

# Iniciar os serviços
echo -e "${YELLOW}Iniciando serviços...${NC}"
docker-compose -f docker-compose.app.yml up -d

# Verificar se os serviços iniciaram corretamente
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao iniciar os serviços.${NC}"
    exit 1
fi

# Verificar status dos containers
echo -e "${YELLOW}Verificando status dos containers...${NC}"
docker-compose -f docker-compose.app.yml ps

echo -e "${GREEN}Deploy concluído com sucesso!${NC}"
echo -e "${YELLOW}Para verificar os logs, use: docker-compose -f docker-compose.app.yml logs -f${NC}"
echo -e "${YELLOW}Para acessar a aplicação, use: http://10.0.1.185:5000${NC}" 