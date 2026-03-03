@echo off
:: ============================================
:: Backup Automático - Ótica Shirlene
:: ============================================

:: Define o diretório do banco original
set SOURCE=C:\Users\joaov\OneDrive\Desktop\ShirleneSystem\optical_store.db

:: Define o destino (pasta ShOptoSystem no Google Drive)
set BACKUP_DIR=C:\Users\joaov\Documents\Google Drive\ShOptoSystem

:: Cria a pasta de destino se não existir
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Gera o nome do arquivo com a data de hoje
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DATETIME=%%I
set DATE_STR=%DATETIME:~0,4%-%DATETIME:~4,2%-%DATETIME:~6,2%

:: Copia o banco com o nome datado
copy "%SOURCE%" "%BACKUP_DIR%\optical_store_%DATE_STR%.db"

:: Remove backups com mais de 30 dias
forfiles /p "%BACKUP_DIR%" /s /m *.db /d -30 /c "cmd /c del @path" 2>nul

echo Backup concluido: optical_store_%DATE_STR%.db
pause
