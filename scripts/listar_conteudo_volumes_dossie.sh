#!/bin/bash
# Script: listar_conteudo_volumes_dossie.sh
# Descrição: Lista o conteúdo dos volumes Docker do projeto dossie (uploads e logs)
# Uso: bash scripts/listar_conteudo_volumes_dossie.sh

set -e

VOLUMES=(
  "dossie-app_dossie_app_uploads"
  "dossie-app_dossie_app_logs"
)

for VOLUME in "${VOLUMES[@]}"; do
  echo "\n==============================="
  echo "Conteúdo do volume: $VOLUME"
  echo "==============================="
  docker run --rm -v ${VOLUME}:/data alpine sh -c 'ls -lR /data || echo "(diretório vazio)"'
  echo "-------------------------------\n"
done

# Dica: Para ver arquivos específicos, edite o script e altere o caminho após /data
# Exemplo: /data/fotos, /data/dossies, etc. 