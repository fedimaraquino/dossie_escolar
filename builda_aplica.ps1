# Script para Buildar e Enviar Aplicação para Docker Hub
# Usuário: fedimaraquino
# Data: 2025-01-27

param(
    [string]$Tag = "latest",
    [string]$DockerHubUser = "fedimaraquino",
    [string]$ImageName = "dossie-escolar",
    [switch]$SkipBuild = $false,
    [switch]$SkipPush = $false,
    [switch]$Force = $false
)

# Configurações
$FullImageName = "$DockerHubUser/$ImageName"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$VersionTag = "v$Timestamp"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SISTEMA DE CONTROLE DE DOSSIE ESCOLAR" -ForegroundColor Cyan
Write-Host "  Build e Deploy para Docker Hub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o Docker está rodando
Write-Host "Verificando se o Docker está disponível..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Erro: Docker não está disponível ou não está rodando" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop e tente novamente" -ForegroundColor Red
    exit 1
}

# Verificar se está logado no Docker Hub
Write-Host "Verificando login no Docker Hub..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($dockerInfo -match "Username:") {
        Write-Host "✓ Logado no Docker Hub" -ForegroundColor Green
    } else {
        Write-Host "⚠ Não logado no Docker Hub. Execute: docker login" -ForegroundColor Yellow
        $login = Read-Host "Deseja fazer login agora? (s/n)"
        if ($login -eq "s" -or $login -eq "S") {
            docker login
        } else {
            Write-Host "✗ Login necessário para continuar" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "✗ Erro ao verificar login no Docker Hub" -ForegroundColor Red
    exit 1
}

# Verificar se os arquivos necessários existem
Write-Host "Verificando arquivos necessários..." -ForegroundColor Yellow
$requiredFiles = @("Dockerfile", "requirements.txt", "app.py")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "✗ Arquivo $file não encontrado" -ForegroundColor Red
        exit 1
    }
}

# Parar containers existentes se necessário
if ($Force) {
    Write-Host "Parando containers existentes..." -ForegroundColor Yellow
    try {
        docker-compose down 2>$null
        Write-Host "✓ Containers parados" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Nenhum container para parar" -ForegroundColor Yellow
    }
}

# Limpar imagens antigas se necessário
if ($Force) {
    Write-Host "Limpando imagens antigas..." -ForegroundColor Yellow
    try {
        docker rmi "$FullImageName`:$VersionTag" 2>$null
        Write-Host "✓ Imagens antigas removidas" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Nenhuma imagem antiga para remover" -ForegroundColor Yellow
    }
}

# Build da imagem
if (-not $SkipBuild) {
    Write-Host "Iniciando build da imagem Docker..." -ForegroundColor Yellow
    Write-Host "Imagem: $FullImageName`:$VersionTag" -ForegroundColor Cyan
    Write-Host "Versão: $VersionTag" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # Build apenas com tag de versão, preservando latest
        docker build --progress=plain --tag "$FullImageName`:$VersionTag" .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Build concluído com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "✗ Erro durante o build" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "✗ Erro durante o build: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ Build pulado conforme solicitado" -ForegroundColor Yellow
}

# Verificar se a imagem foi criada
Write-Host "Verificando imagem criada..." -ForegroundColor Yellow
try {
    $imageInfo = docker images "$FullImageName" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    Write-Host "✓ Imagem criada:" -ForegroundColor Green
    Write-Host $imageInfo -ForegroundColor White
} catch {
    Write-Host "✗ Erro ao verificar imagem" -ForegroundColor Red
    exit 1
}

# Testar a imagem localmente (opcional)
$testImage = Read-Host "Deseja testar a imagem localmente? (s/n)"
if ($testImage -eq "s" -or $testImage -eq "S") {
    Write-Host "Testando imagem localmente..." -ForegroundColor Yellow
    try {
        # Parar container de teste se existir
        docker stop dossie-test 2>$null
        docker rm dossie-test 2>$null
        
        # Executar container de teste
        docker run -d --name dossie-test -p 5001:5000 "$FullImageName`:$VersionTag"
        
        Start-Sleep -Seconds 5
        
        # Verificar se o container está rodando
        $containerStatus = docker ps --filter "name=dossie-test" --format "{{.Status}}"
        if ($containerStatus) {
            Write-Host "✓ Container de teste rodando: $containerStatus" -ForegroundColor Green
            Write-Host "Acesse: http://localhost:5001" -ForegroundColor Cyan
        } else {
            Write-Host "✗ Container de teste não está rodando" -ForegroundColor Red
        }
        
        # Parar container de teste
        docker stop dossie-test
        docker rm dossie-test
        Write-Host "✓ Container de teste removido" -ForegroundColor Green
    } catch {
        Write-Host "✗ Erro ao testar imagem: $_" -ForegroundColor Red
    }
}

# Push para Docker Hub
if (-not $SkipPush) {
    Write-Host "Enviando imagem para Docker Hub..." -ForegroundColor Yellow
    Write-Host "Usuário: $DockerHubUser" -ForegroundColor Cyan
    Write-Host "Repositório: $ImageName" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # Push apenas da tag de versão
        Write-Host "Enviando tag: $VersionTag" -ForegroundColor Yellow
        docker push "$FullImageName`:$VersionTag"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Tag $VersionTag enviada com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "✗ Erro ao enviar tag $VersionTag" -ForegroundColor Red
            exit 1
        }
        
    } catch {
        Write-Host "✗ Erro durante o push: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ Push pulado conforme solicitado" -ForegroundColor Yellow
}

# Resumo final
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA OPERAÇÃO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ Imagem: $FullImageName" -ForegroundColor Green
Write-Host "✓ Tag versão: $VersionTag" -ForegroundColor Green
Write-Host "✓ Timestamp: $Timestamp" -ForegroundColor Green

if (-not $SkipPush) {
    Write-Host ""
    Write-Host "Para usar a imagem:" -ForegroundColor Yellow
    Write-Host "docker pull `"$FullImageName`:$VersionTag`"" -ForegroundColor White
    Write-Host "docker run -p 5000:5000 `"$FullImageName`:$VersionTag`"" -ForegroundColor White
    Write-Host ""
    Write-Host "URL no Docker Hub:" -ForegroundColor Yellow
    Write-Host "https://hub.docker.com/r/$DockerHubUser/$ImageName" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✓ Processo concluído com sucesso!" -ForegroundColor Green 