@echo off
setlocal enabledelayedexpansion

:: Read home_dir from git.ini
for /f "tokens=2 delims==" %%A in ('findstr "^home_dir" git.ini') do set "home_dir=%%A"

:: Trim spaces and remove quotes if any
set "home_dir=%home_dir: =%"
set "home_dir=%home_dir:"=%"

:: Define target directory
set "target_dir=%home_dir%\application\appservice\app"

:: Check if the directory exists
if not exist "%target_dir%" (
    echo Error: Target directory does not exist!
    exit /b
)

:: Navigate to the app directory
cd /d "%target_dir%"

echo Current working directory is: %cd%

echo Target directory %target_dir%

:: Check if app.py exists and rename it to appDOCKER.py
if exist "app.py" (
    echo Renaming app.py to appDOCKER.py...
    ren app.py appDOCKER.py
    echo Renamed app.py to appDOCKER.py.
) else (
    echo app.py not found in target directory.
)

:: Copy app.py from devenv directory to the target directory
set "devenv_dir=config\devenv"

echo Dev env directory %devenv_dir%

echo Current working directory is: %cd%

cd ..\..\..

echo Current working directory is: %cd%

:: Navigate to the devenv directory
cd /d "%devenv_dir%"

:: Echo the current working directory to confirm we are in the right place
echo Current working directory is: %cd%

if exist "app.py" (
    echo Copying app.py from %devenv_dir% to target directory...
    copy app.py "..\..\application\appservice\app\app.py"
    echo app.py copied successfully from %devenv_dir% to %target_dir%.
) else (
    echo Error: app.py not found in devenv directory.
    exit /b
)

cd ..\..\application\appservice\app

:: Check if the virtual environment exists
if not exist "erpenv" (
    echo Creating virtual environment...
    python -m venv erpenv
	
	:: Activate the virtual environment
	call erpenv\Scripts\activate.bat
	
	:: Check if the virtual environment is activated by checking the 'erpenv' folder
	echo Checking if the virtual environment is activated...
	if not exist "erpenv\Scripts\activate.bat" (
		echo Error: Virtual environment is not activated correctly!
		exit /b
	) else (
		echo Virtual environment activated successfully.
	)
	
	:: Install required packages from requirements.txt
	echo Installing required packages from requirements.txt...
	
	python.exe -m pip install --upgrade pip

	pip install -r requirements.txt

	if errorlevel 1 (
		echo Error installing packages. Exiting...
		exit /b
	)

	:: Wait for all installations to finish before opening VS Code
	echo All required packages installed.
	cd ..\app
)

:: Open VS Code in the same directory
echo Opening VS Code...
code .

endlocal
