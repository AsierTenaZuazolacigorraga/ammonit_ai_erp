@echo off
setlocal

rem Change the path to the current file path
set "CURRENT_PATH=%~dp0"
cd %CURRENT_PATH%

rem Load environment variables from .env
for /f "usebackq tokens=1,* delims==" %%a in ("..\..\.env") do (
    set "%%a=%%b"
)

dist\main.exe --db_path "C:\CAF\CAFRepository\my_projects\iot_bind\backend\.gitignores\db.accdb" --username %FIRST_SUPERUSER% --password %FIRST_SUPERUSER_PASSWORD%

pause