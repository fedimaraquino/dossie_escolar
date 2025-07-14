# Correção de Persistência de Fotos - Sistema de Controle de Dossiê Escolar

## Data da Implementação
**27/01/2025**

## Problema Identificado
As fotos dos usuários estavam sendo apagadas quando o container da aplicação era reiniciado, indicando problema de persistência de dados.

## Solução Aplicada
- Volumes Docker persistentes configurados para `/app/static/uploads`, `/app/static` e `/app/logs`.
- Dockerfile e entrypoint garantem criação e permissões corretas dos diretórios de upload.
- Variáveis de ambiente garantem que o caminho de upload é sempre `/app/static/uploads`.

## Checklist de Validação
1. Faça upload de uma foto de usuário, diretor, escola ou dossiê.
2. Confirme que a imagem aparece normalmente na interface.
3. Reinicie o container com `docker-compose restart dossie-app`.
4. Verifique se a imagem continua aparecendo normalmente.
5. (Opcional) Verifique o conteúdo do volume com:
   ```bash
   docker run --rm -v app_uploads:/data alpine ls -la /data/fotos
   ```
6. (Opcional) Verifique permissões dentro do container:
   ```bash
   docker exec -it CONTAINER_ID ls -la /app/static/uploads
   ```

## Configuração docker-compose.yml (exemplo)
```yaml
services:
  dossie-app:
    build: .
    image: dossie-app:local
    environment:
      - DATABASE_URL=postgresql://dossie_user:***@dossie_db:5432/dossie_escola
      - SECRET_KEY=***
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - UPLOAD_FOLDER=/app/static/uploads
      - MAX_CONTENT_LENGTH=16777216
    ports:
      - "5000:5000"
    volumes:
      - app_uploads:/app/static/uploads:rw
      - app_logs:/app/instance/logs:rw
      - app_static:/app/static:rw
    depends_on:
      - dossie_db
    restart: unless-stopped

volumes:
  app_uploads:
    driver: local
  app_logs:
    driver: local
  app_static:
    driver: local
  postgres_data:
    driver: local
```

## Observações
- Se as imagens continuarem sumindo, verifique se o volume está realmente sendo usado e se não há conflitos de permissões.
- Para produção (EasyPanel/Hostinger), siga o mesmo padrão de volumes.
- Sempre faça backup das fotos antes de qualquer alteração estrutural nos volumes. 