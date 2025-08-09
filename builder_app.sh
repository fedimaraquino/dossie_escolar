#!/bin/bash

# Script para build e push de imagens Docker com versionamento
# Uso: ./build_and_push.sh [VERSION] [DOCKER_USERNAME]

set -e  # Para o script se houver erro

# Configurações
DEFAULT_VERSION="1.0.0"
DEFAULT_DOCKER_USERNAME="fedimaraquino"

# Parâmetros
VERSION=${1:-$DEFAULT_VERSION}
DOCKER_USERNAME=${2:-$DEFAULT_DOCKER_USERNAME}
IMAGE_NAME="dossie-novo"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}"

echo "🐳 Docker Build and Push Script"
echo "================================"
echo "Versão: $VERSION"
echo "Usuário Docker: $DOCKER_USERNAME"
echo "Nome da imagem: $FULL_IMAGE_NAME"
echo ""

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Erro: Docker não está rodando!"
    exit 1
fi

# Verificar se está logado no Docker Hub
if ! docker info | grep -q "Username"; then
    echo "⚠️  Aviso: Você não está logado no Docker Hub"
    echo "Execute: docker login"
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔨 Iniciando build da imagem..."

# Build da imagem com tag de versão
docker build -t "${FULL_IMAGE_NAME}:${VERSION}" .

if [ $? -eq 0 ]; then
    echo "✅ Build da versão ${VERSION} concluído com sucesso!"
else
    echo "❌ Erro no build da imagem!"
    exit 1
fi

# Build da imagem com tag latest (comentado para não substituir)
# echo "🔨 Criando tag latest..."
# docker build -t "${FULL_IMAGE_NAME}:latest" .

# if [ $? -eq 0 ]; then
#     echo "✅ Build da versão latest concluído com sucesso!"
# else
#     echo "❌ Erro no build da imagem latest!"
#     exit 1
# fi

# Push das imagens
echo "📤 Fazendo push das imagens para o Docker Hub..."

# Push da versão específica
echo "📤 Push da versão ${VERSION}..."
docker push "${FULL_IMAGE_NAME}:${VERSION}"

if [ $? -eq 0 ]; then
    echo "✅ Push da versão ${VERSION} concluído!"
else
    echo "❌ Erro no push da versão ${VERSION}!"
    exit 1
fi

# Push da versão latest (comentado para não substituir)
# echo "📤 Push da versão latest..."
# docker push "${FULL_IMAGE_NAME}:latest"

# if [ $? -eq 0 ]; then
#     echo "✅ Push da versão latest concluído!"
# else
#     echo "❌ Erro no push da versão latest!"
#     exit 1
# fi

echo ""
echo "🎉 Sucesso! Imagem enviada para o Docker Hub:"
echo "   - ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
echo "📋 Comandos para usar a imagem:"
echo "   docker pull ${FULL_IMAGE_NAME}:${VERSION}"
echo ""
echo "🔗 URL da imagem no Docker Hub:"
echo "   https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}" 