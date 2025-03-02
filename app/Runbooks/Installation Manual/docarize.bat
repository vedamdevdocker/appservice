@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Check if Docker Compose is installed
docker-compose -v >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Docker Compose is not installed. Please install it and try again.
    EXIT /B 1
)

echo ✅ Docker Compose is installed.

:: Check if docker-compose.yml exists in the current directory
IF NOT EXIST "docker-compose.yml" (
    echo ❌ ERROR: docker-compose.yml not found in the current directory.
    EXIT /B 1
)

echo ✅ Found docker-compose.yml, proceeding...

:: Run docker-compose build
echo 🚀 Building Docker images...
docker-compose build
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: docker-compose build failed.
    EXIT /B 1
)
echo ✅ Build completed successfully.

:: Run docker-compose up -d
echo 🚀 Starting Docker containers...
docker-compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: docker-compose up failed.
    EXIT /B 1
)
echo ✅ Containers started successfully.

:: Run docker ps
echo 🔍 Checking running containers...
docker ps

echo ✅ Process completed successfully. Exiting...
EXIT /B 0
