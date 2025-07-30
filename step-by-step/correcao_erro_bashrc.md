# Correção do Erro de Sintaxe no .bashrc

## Problema Identificado

O erro mostra que há caracteres especiais (espaços invisíveis) no início da linha do arquivo `.bashrc`:

```
bash: /c/Users/edima/.bashrc: line 1: syntax error near unexpected token `then'
bash: /c/Users/edima/.bashrc: line 1: `□□if [ -f ".bashrc" ]; then source .bashrc; fi'
```

## Solução

### Passo 1: Limpar o arquivo .bashrc

1. **Abra o arquivo .bashrc**:
```bash
nano ~/.bashrc
```

2. **Delete todo o conteúdo e recrie**:
```bash
# Pressione Ctrl+A para selecionar tudo
# Pressione Delete para apagar
# Digite o novo conteúdo:
```

3. **Adicione o conteúdo correto**:
```bash
# Ativação automática do ambiente virtual
if [ -f "c:/Users/edima/dossie_novo/.venv/Scripts/activate" ]; then
    source c:/Users/edima/dossie_novo/.venv/Scripts/activate
    echo "Ambiente virtual ativado automaticamente!"
fi
```

### Passo 2: Alternativa - Recriar o arquivo

Se o problema persistir, recrie o arquivo:

```bash
# Faça backup do arquivo atual
cp ~/.bashrc ~/.bashrc.backup

# Remova o arquivo atual
rm ~/.bashrc

# Crie um novo arquivo
cat > ~/.bashrc << 'EOF'
# Ativação automática do ambiente virtual
if [ -f "c:/Users/edima/dossie_novo/.venv/Scripts/activate" ]; then
    source c:/Users/edima/dossie_novo/.venv/Scripts/activate
    echo "Ambiente virtual ativado automaticamente!"
fi
EOF
```

### Passo 3: Verificar e testar

1. **Verifique o arquivo**:
```bash
cat ~/.bashrc
```

2. **Teste a sintaxe**:
```bash
bash -n ~/.bashrc
```

3. **Recarregue**:
```bash
source ~/.bashrc
```

## Solução Alternativa - Configuração por Diretório

Se preferir uma abordagem mais segura:

1. **Vá para o diretório do projeto**:
```bash
cd c:/Users/edima/dossie_novo
```

2. **Crie um arquivo .bashrc no projeto**:
```bash
cat > .bashrc << 'EOF'
# Ativação automática do ambiente virtual
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "Ambiente virtual ativado automaticamente!"
fi
EOF
```

3. **Configure o .bashrc global para carregar este arquivo**:
```bash
echo 'if [ -f ".bashrc" ]; then source .bashrc; fi' >> ~/.bashrc
```

## Verificação Final

Após corrigir, teste:

```bash
# Abra um novo terminal
# Deve mostrar:
(.venv) 
edima@EdimarAquino MINGW64 ~/dossie_novo (main)
$ 
```

## Prevenção

Para evitar problemas futuros:
- Sempre use um editor de texto adequado (nano, vim, VS Code)
- Evite copiar e colar de fontes que podem ter caracteres especiais
- Verifique a sintaxe antes de salvar: `bash -n arquivo.sh` 