@echo off
echo Iniciando deploy via Portainer...

REM Verificar se o Docker está instalado
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker nao esta instalado. Por favor, instale o Docker primeiro.
    exit /b 1
)

REM Verificar se o Docker Compose está instalado
where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker Compose nao esta instalado. Por favor, instale o Docker Compose primeiro.
    exit /b 1
)

REM Criar rede se não existir
echo Criando redes Docker...
docker network create traefik-public 2>nul
docker network create app-network 2>nul

REM Construir a imagem
echo Construindo imagem Docker...
docker build -t dossie-app:latest .

REM Verificar se a construção foi bem sucedida
if %ERRORLEVEL% neq 0 (
    echo Erro ao construir a imagem Docker.
    exit /b 1
)

REM Iniciar os serviços
echo Iniciando serviços...
docker-compose -f docker-compose.app.yml up -d

REM Verificar se os serviços iniciaram corretamente
if %ERRORLEVEL% neq 0 (
    echo Erro ao iniciar os serviços.
    exit /b 1
)

REM Verificar status dos containers
echo Verificando status dos containers...
docker-compose -f docker-compose.app.yml ps

echo Deploy concluido com sucesso!
echo Para verificar os logs, use: docker-compose -f docker-compose.app.yml logs -f
echo Para acessar a aplicacao, use: http://10.0.1.185:5000

pause 