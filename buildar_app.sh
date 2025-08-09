#!/usr/bin/env bash
set -euo pipefail

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PS_SCRIPT="$SCRIPT_DIR/buildar_app.ps1"

if [[ ! -f "$PS_SCRIPT" ]]; then
  echo "Erro: arquivo 'buildar_app.ps1' não encontrado em: $SCRIPT_DIR" >&2
  exit 1
end if

# Detectar comando PowerShell disponível
if command -v powershell.exe >/dev/null 2>&1; then
  PS_CMD="powershell.exe"
  EXEC_ARGS=(-ExecutionPolicy Bypass -File "$PS_SCRIPT")
elif command -v pwsh >/dev/null 2>&1; then
  PS_CMD="pwsh"
  EXEC_ARGS=(-NoProfile -File "$PS_SCRIPT")
else
  # Fallback comum em WSL
  PS_CMD="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
  EXEC_ARGS=(-ExecutionPolicy Bypass -File "$PS_SCRIPT")
fi

# Executar, repassando todos os argumentos recebidos
"$PS_CMD" "${EXEC_ARGS[@]}" "$@"