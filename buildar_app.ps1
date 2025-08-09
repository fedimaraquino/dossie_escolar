# Script PowerShell para build e push de imagens Docker com versionamento
# Uso: .\buildar_app.ps1 [opcional: -Version "1.2.0"] [opcional: -DockerUsername "usuario"]

param(
    [string]$Version,
    [string]$DockerUsername = "fedimaraquino"
)

# Versão automática quando não informada: vYYYYMMDD-HHmmss[-g<sha>]
if ([string]::IsNullOrWhiteSpace($Version)) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Version = "v$timestamp"
    try {
        $gitSha = (git rev-parse --short HEAD) 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitSha)) {
            $Version = "$Version-g$gitSha"
        }
    } catch {
        # Ignorar caso git não esteja disponível
    }
}

# Configurações
$ImageName = "dossie-novo"
$FullImageName = "${DockerUsername}/${ImageName}"

Write-Host "Docker Build and Push Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Versao: $Version" -ForegroundColor Yellow
Write-Host "Usuario Docker: $DockerUsername" -ForegroundColor Yellow
Write-Host "Nome da imagem: $FullImageName" -ForegroundColor Yellow
Write-Host ""

# Verificar se o Docker está rodando
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERRO: Docker nao esta rodando!" -ForegroundColor Red
    exit 1
}

# Verificar se está logado no Docker Hub
$dockerInfo = docker info 2>&1
if ($dockerInfo -notmatch "Username") {
    Write-Host "AVISO: Voce nao esta logado no Docker Hub" -ForegroundColor Yellow
    Write-Host "Executando login automatico..." -ForegroundColor Green
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha no login do Docker Hub!" -ForegroundColor Red
        Write-Host "Execute manualmente: docker login" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "SUCESSO: Login realizado com sucesso!" -ForegroundColor Green
}

Write-Host "Iniciando build da imagem..." -ForegroundColor Green

# Build da imagem com tag de versão
Write-Host "Build da versao $Version..." -ForegroundColor Green
docker build -t "${FullImageName}:${Version}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCESSO: Build da versao $Version concluido!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no build da imagem!" -ForegroundColor Red
    exit 1
}

# Push das imagens
Write-Host "Fazendo push das imagens para o Docker Hub..." -ForegroundColor Cyan

# Push da versão específica
Write-Host "Push da versao $Version..." -ForegroundColor Green
docker push "${FullImageName}:${Version}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCESSO: Push da versao $Version concluido!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha no push da versao $Version!" -ForegroundColor Red
    exit 1
}

Write-Host "" 
Write-Host "SUCESSO! Imagem enviada para o Docker Hub:" -ForegroundColor Green
Write-Host "   - ${FullImageName}:${Version}" -ForegroundColor White
Write-Host "" 
Write-Host "Comandos para usar a imagem:" -ForegroundColor Cyan
Write-Host "   docker pull ${FullImageName}:${Version}" -ForegroundColor White
Write-Host "" 
Write-Host "URL da imagem no Docker Hub:" -ForegroundColor Cyan
Write-Host "   https://hub.docker.com/r/${DockerUsername}/${ImageName}" -ForegroundColor White