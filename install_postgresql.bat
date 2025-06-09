@echo off
echo ========================================
echo   INSTALACAO POSTGRESQL PARA DOSSIE
echo ========================================
echo.

echo 1. Instalando psycopg2 (driver PostgreSQL)...
pip install psycopg2-binary

echo.
echo 2. Instalando Flask-Migrate (migrações)...
pip install Flask-Migrate

echo.
echo 3. Atualizando requirements.txt...
pip freeze > requirements.txt

echo.
echo ========================================
echo   PROXIMOS PASSOS:
echo ========================================
echo.
echo 1. Instale o PostgreSQL:
echo    - Download: https://www.postgresql.org/download/windows/
echo    - Ou use: winget install PostgreSQL.PostgreSQL
echo.
echo 2. Crie o banco de dados:
echo    - Abra pgAdmin ou psql
echo    - CREATE DATABASE dossie_escolar;
echo    - CREATE USER dossie_user WITH PASSWORD 'sua_senha';
echo    - GRANT ALL PRIVILEGES ON DATABASE dossie_escolar TO dossie_user;
echo.
echo 3. Configure as variaveis de ambiente (opcional):
echo    - set DATABASE_URL=postgresql://dossie_user:sua_senha@localhost/dossie_escolar
echo.
echo 4. Execute: python migrate_to_postgresql.py
echo.
pause
