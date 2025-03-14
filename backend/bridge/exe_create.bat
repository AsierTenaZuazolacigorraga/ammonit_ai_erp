@echo off
setlocal

rem Change the path to the current file path
set "CURRENT_PATH=%~dp0"
cd %CURRENT_PATH%

call .venv\Scripts\activate

rem Add the project root to PYTHONPATH so imports work correctly
cd ..\..\
set PYTHONPATH=%CD%

rem Go back to the bridge directory
cd backend\bridge

rem Run PyInstaller with additional options to include the backend module
pyinstaller --onefile --additional-hooks-dir=. --paths=..\.. main.py

pause
