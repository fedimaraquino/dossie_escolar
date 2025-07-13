FROM python:3.11-slim

# Variável para forçar o rebuild completo
ENV CACHE_BUSTER=202501270000

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Criar diretórios necessários com permissões corretas
RUN mkdir -p /app/static/uploads/fotos \
    /app/static/uploads/dossies \
    /app/static/uploads/diretores \
    /app/static/uploads/anexos \
    /app/logs \
    && chmod -R 755 /app/static/uploads \
    && chmod -R 755 /app/logs \
    && chown -R www-data:www-data /app/static/uploads \
    && chown -R www-data:www-data /app/logs

# Definir variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV UPLOAD_FOLDER=/app/static/uploads

# Expor a porta
EXPOSE 5000

# Script de inicialização
COPY docker-entrypoint.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]

# Cache buster: 2025-01-27 00:00
