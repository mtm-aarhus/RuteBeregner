@echo off
echo Installer Jord Transport applikation...

REM Check om Python er installeret
python --version >nul 2>&1
if errorlevel 1 (
    echo Python er ikke installeret. Download fra https://python.org
    echo Husk at tilfoeje Python til PATH under installationen
    pause
    exit /b 1
)

REM Check om Node.js er installeret
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js er ikke installeret. Download fra https://nodejs.org
    echo Installer LTS versionen og genstart derefter computeren
    pause
    exit /b 1
)

REM Opret virtual environment
echo Opretter virtuelt miljoe...
python -m venv venv
if errorlevel 1 (
    echo Kunne ikke oprette virtuelt miljoe
    pause
    exit /b 1
)

REM Aktiver virtual environment og installer dependencies
echo Installerer Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo Installation af Python dependencies mislykkedes
    pause
    exit /b 1
)

REM Tjek om rxconfig.py allerede eksisterer
if not exist "rxconfig.py" (
    echo Opretter rxconfig.py...
    reflex init --no-template
) else (
    echo rxconfig.py eksisterer allerede - springer initialisering over
)

REM Installer Node.js dependencies uden at overskrive eksisterende kode
echo Installerer frontend dependencies...
reflex install

if errorlevel 1 (
    echo Frontend dependencies installation mislykkedes
    pause
    exit /b 1
)

echo Installation fuldfoert!
echo.
echo For at starte applikationen:
echo 1. Dobbeltklik paa START_APP.bat
echo 2. Eller aabn terminal her og koer: venv\Scripts\activate.bat ^&^& reflex run
echo.
pause
