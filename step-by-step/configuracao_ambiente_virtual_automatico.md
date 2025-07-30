# Configuração de Ativação Automática do Ambiente Virtual

## Para Git Bash (MINGW64)

### Opção 1: Modificar o arquivo .bashrc

1. **Abra o arquivo .bashrc**:
```bash
nano ~/.bashrc
```

2. **Adicione a linha no final do arquivo**:
```bash
# Ativação automática do ambiente virtual
if [ -f "c:/Users/edima/biblioteca/.venv/Scripts/activate" ]; then
    source c:/Users/edima/biblioteca/.venv/Scripts/activate
fi
```

3. **Salve e recarregue**:
```bash
source ~/.bashrc
```

### Opção 2: Modificar o arquivo .bash_profile

1. **Crie ou edite o arquivo .bash_profile**:
```bash
nano ~/.bash_profile
```

2. **Adicione o conteúdo**:
```bash
# Ativação automática do ambiente virtual
if [ -f "c:/Users/edima/biblioteca/.venv/Scripts/activate" ]; then
    source c:/Users/edima/biblioteca/.venv/Scripts/activate
fi
```

### Opção 3: Para diretório específico (Recomendado)

1. **Crie um arquivo .bashrc no diretório do projeto**:
```bash
cd c:/Users/edima/biblioteca
nano .bashrc
```

2. **Adicione o conteúdo**:
```bash
# Ativação automática do ambiente virtual
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "Ambiente virtual ativado automaticamente!"
fi
```

3. **Configure o Git Bash para carregar este arquivo**:
```bash
echo 'if [ -f ".bashrc" ]; then source .bashrc; fi' >> ~/.bashrc
```

## Para PowerShell

### Opção 1: Modificar o perfil do PowerShell

1. **Abra o PowerShell como administrador**

2. **Verifique se o perfil existe**:
```powershell
Test-Path $PROFILE
```

3. **Crie o perfil se não existir**:
```powershell
if (!(Test-Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force
}
```

4. **Edite o perfil**:
```powershell
notepad $PROFILE
```

5. **Adicione o conteúdo**:
```powershell
# Ativação automática do ambiente virtual
if (Test-Path "c:\Users\edima\biblioteca\.venv\Scripts\Activate.ps1") {
    & "c:\Users\edima\biblioteca\.venv\Scripts\Activate.ps1"
    Write-Host "Ambiente virtual ativado automaticamente!" -ForegroundColor Green
}
```

## Para CMD (Prompt de Comando)

### Opção 1: Modificar o arquivo autoexec.bat

1. **Crie um arquivo autoexec.bat**:
```cmd
echo @echo off > c:\autoexec.bat
echo call c:\Users\edima\biblioteca\.venv\Scripts\activate.bat >> c:\autoexec.bat
```

### Opção 2: Criar um arquivo .bat no diretório

1. **Crie um arquivo activate_env.bat**:
```cmd
@echo off
call .venv\Scripts\activate.bat
echo Ambiente virtual ativado!
cmd /k
```

## Verificação

Após configurar, teste abrindo um novo terminal:

```bash
# Deve mostrar o ambiente virtual ativo
(.venv) edima@EdimarAquino MINGW64 ~/biblioteca (main)
$
```

## Solução Alternativa - Alias

Se preferir ter controle manual, crie um alias:

```bash
# Adicione ao .bashrc
alias activate='source c:/Users/edima/biblioteca/.venv/Scripts/activate'
```

Então use: `activate` para ativar o ambiente.

## Recomendação

**Para desenvolvimento**, recomendo a **Opção 3** (arquivo .bashrc no diretório do projeto), pois:
- Só ativa quando você entrar no diretório do projeto
- Não interfere com outros projetos
- É mais organizado e específico

## Troubleshooting

Se não funcionar:

1. **Verifique o caminho**:
```bash
ls -la c:/Users/edima/biblioteca/.venv/Scripts/
```

2. **Teste manualmente**:
```bash
source c:/Users/edima/biblioteca/.venv/Scripts/activate
```

3. **Verifique permissões**:
```bash
chmod +x c:/Users/edima/biblioteca/.venv/Scripts/activate
``` 