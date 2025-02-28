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

ENDLOCAL
