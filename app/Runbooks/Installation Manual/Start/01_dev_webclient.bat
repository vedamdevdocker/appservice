@echo off
setlocal enabledelayedexpansion

:: Read home_dir from git.ini
for /f "tokens=2 delims==" %%A in ('findstr "^home_dir" git.ini') do set "home_dir=%%A"

:: Trim spaces and remove quotes if any
set "home_dir=%home_dir: =%"
set "home_dir=%home_dir:"=%"

:: Define my-app directory
set "my_app_dir=%home_dir%\application\webclient\my-app"

:: Check if the directory exists
if not exist "%my_app_dir%" (
    echo Error: my-app directory does not exist!
    exit /b
)

:: Navigate to the my-app directory
cd /d "%my_app_dir%"

:: Check if node_modules exists
if not exist "node_modules" (
    echo node_modules not found. Running npm install...
    npm install
    if errorlevel 1 (
        echo Error installing npm packages. Exiting...
        exit /b
    )
) else (
    echo node_modules already exists. Skipping npm install.
)

:: Open VS Code in my-app directory
echo Opening VS Code...
code .

endlocal
