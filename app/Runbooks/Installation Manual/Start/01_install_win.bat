@echo off
SETLOCAL

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed. Please install Python and try again.
    EXIT /B 1
)

:: Run the Python script
python 01_start.py
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python script execution failed.
    EXIT /B 1
)

:: Switch to current directory
SET "CURR_DIR=%CD%"

:: Read git.ini file
SET "GIT_INI=%CURR_DIR%\git.ini"
IF NOT EXIST "%GIT_INI%" (
    echo Error: git.ini file not found.
    EXIT /B 1
)

FOR /F "tokens=1,2 delims==" %%A IN ('findstr "home_dir" "%GIT_INI%"') DO (
    IF "%%A" == "home_dir" SET "HOME_DIR=%%B"
)

:: Check if home_dir exists
IF NOT EXIST "%CURR_DIR%\%HOME_DIR%" (
    echo Error: Home directory %HOME_DIR% not found.
    EXIT /B 1
)

:: Switch to home directory and then to config directory
CD /D "%CURR_DIR%\%HOME_DIR%\config"
IF NOT EXIST "run_python.bat" (
    echo Error: run_python.bat not found.
    EXIT /B 1
)

:: Run run_python.bat
call run_python.bat
IF %ERRORLEVEL% NEQ 0 (
    echo Error: run_python.bat execution failed.
    EXIT /B 1
)

:: Switch to home directory
CD /D "%CURR_DIR%\%HOME_DIR%"

:: Check if docker-compose.yml exists
IF EXIST "docker-compose.yml" (
    IF EXIST "dockerize.bat" (
        call dockerize.bat
    ) ELSE (
        echo Warning: dockerize.bat not found.
    )
) ELSE (
    echo Warning: docker-compose.yml not found.
)

ENDLOCAL
