# Otimização da Imagem Docker - Sistema de Controle de Dossiê Escolar

Data: 2025-01-31
Responsável: Automação

## Objetivo
Reduzir significativamente o tamanho da imagem Docker sem alterar o comportamento da aplicação em produção.

## Alterações Realizadas

1. Dockerfile
   - Removido `build-essential` e `libpq-dev` (não necessários em runtime)
   - Instalado pacotes via APT com `--no-install-recommends`
   - Mantidos apenas `postgresql-client` e `netcat-traditional`

2. .dockerignore (novo)
   - Exclusão de arquivos e pastas não necessários no build: `.venv/`, `docs/`, `step-by-step/`, `uploads/`, `instance/`, `*.md`, scripts locais e compose alternativos

## Resultado
- Antes: `fedimaraquino/dossie-novo:1.0.0` ≈ 2.53GB
- Depois: `fedimaraquino/dossie-novo:1.0.0-lean` ≈ 1.28GB
- Redução aproximada: ~49%

Comando para verificar:
```
docker images | findstr dossie-novo
```

## Observações de Compatibilidade
- A aplicação continua usando `gunicorn` + `docker-entrypoint.sh`
- Cliente `psql` mantido para scripts de inicialização
- Dependências Python mantidas (nenhuma remoção de requirements na etapa atual)

## Comandos Utilizados
- Build:
```
docker build --progress=plain -t fedimaraquino/dossie-novo:1.0.0-lean .
```
- (Opcional) Push:
```
docker push fedimaraquino/dossie-novo:1.0.0-lean
```

## Próximas Otimizações (Seguras e Recomendadas)
- Avaliar remoção de pacotes pesados não utilizados no `requirements.txt` (ex.: Django/DRF, langchain/openai, faiss, scikit-learn, scipy, matplotlib, uvicorn/starlette). A análise inicial não encontrou uso no código, mas requer validação com a equipe antes de remoção.
- Habilitar multi-stage para build de extensões nativas, se necessário (não requerido no momento pois utilizamos wheels binárias `*-manylinux`).
- Fixar versões base e revisar periodicamente o `.dockerignore`.

## Validação
- Build OK
- Tamanho reduzido confirmado
- Sem mudanças funcionais na aplicação