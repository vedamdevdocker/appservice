@echo off
setlocal

:: Get the directory of the current script
set SCRIPT_DIR=%~dp0

:: Move one level up to get the parent directory
cd ..

:: Run the Python script
python "%SCRIPT_DIR%\05_update_nginx_conf_file.py"

:: Check if the script executed successfully
if %errorlevel% neq 0 (
    echo Error: The Python script encountered an issue.
    exit /b %errorlevel%
)

echo The nginx configuration file is updated successfully!
exit /b 0
