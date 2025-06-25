# Correção de conflito: múltiplas definições da função `log_acao`

## Problema

Ocorreu o erro:
```
log_acao() got multiple values for argument 'detalhes'
```

Esse erro foi causado porque existiam múltiplas funções chamadas `log_acao` no projeto, com assinaturas diferentes:
- `utils/logs.py`: função principal, aceita `acao, item_alterado=None, detalhes=None, usuario_id=None`.
- `app_completo.py`: função local, aceita apenas `acao, item_alterado=None, detalhes=None`.
- `apps/core/utils.py`: função utilitária, espera `usuario_id` como primeiro argumento.

Quando o Flask carrega o projeto, dependendo do entrypoint, a função de `app_completo.py` pode sobrescrever a principal, causando conflito de parâmetros.

## Solução aplicada

- Renomeamos a função `log_acao` de `app_completo.py` para `log_acao_simples`.
- Todas as chamadas internas em `app_completo.py` foram atualizadas para usar `log_acao_simples`.
- Os controllers e demais módulos continuam importando a função correta de `utils/logs.py`.

Assim, eliminamos o conflito global de nomes e garantimos que cada parte do sistema utilize a função correta.

## Orientações para o futuro

- Sempre que criar funções utilitárias globais, evite nomes genéricos já usados em outros módulos.
- Prefira importar explicitamente do módulo correto (`from utils.logs import log_acao`).
- Se precisar de funções de log diferentes, use nomes distintos (ex: `log_acao_simples`, `log_acao_avancado`).
- Mantenha a assinatura das funções consistente em todo o projeto.

---

**Arquivo alterado:**
- `app_completo.py` (função e chamadas internas)

**Função principal de log:**
- `utils/logs.py::log_acao`

**Função local (apenas para app_completo.py):**
- `log_acao_simples`

---

Se o erro persistir em outros módulos, repita o processo de renomeação e ajuste de importações. 