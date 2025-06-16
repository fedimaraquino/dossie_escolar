@echo off
echo Configurando Docker Swarm e redes...

REM Inicializar o Swarm se ainda não estiver inicializado
docker info | findstr "Swarm: active" >nul
if %ERRORLEVEL% neq 0 (
    echo Inicializando Docker Swarm...
    docker swarm init
    if %ERRORLEVEL% neq 0 (
        echo Erro ao inicializar Docker Swarm.
        exit /b 1
    )
)

REM Criar redes no modo swarm
echo Criando redes Docker no modo swarm...
docker network create --driver overlay --attachable traefik-public
docker network create --driver overlay --attachable app-network

echo Configuracao concluida!
echo Agora voce pode fazer o deploy da stack no Portainer.

pause 