@echo off
echo ===================================================
echo  SIKKER INSTALLATION AF JORD TRANSPORT APPLIKATION
echo ===================================================
echo.

REM Check om Python er installeret
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEJL] Python er ikke installeret. Download fra https://python.org
    echo        Husk at tilfoeje Python til PATH under installationen
    pause
    exit /b 1
)

REM Check om Node.js er installeret
node --version >nul 2>&1
if errorlevel 1 (
    echo [FEJL] Node.js er ikke installeret. Download fra https://nodejs.org
    echo        Installer LTS versionen og genstart derefter computeren
    pause
    exit /b 1
)

echo [INFO] Python og Node.js er installeret korrekt
echo.

REM Opret backup mappe hvis den ikke eksisterer
if not exist "backup" mkdir backup

REM Backup af vigtige filer hvis de eksisterer
echo [BACKUP] Opretter sikkerhedskopi af eksisterende filer...
if exist "jord_transport\jord_transport.py" (
    copy "jord_transport\jord_transport.py" "backup\jord_transport_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.py" >nul
    echo         - jord_transport.py sikkerhedskopieret
)
if exist "jord_transport\__init__.py" (
    copy "jord_transport\__init__.py" "backup\__init___backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.py" >nul
    echo         - __init__.py sikkerhedskopieret
)
if exist "assets\styles.css" (
    copy "assets\styles.css" "backup\styles_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%.css" >nul
    echo         - styles.css sikkerhedskopieret
)
echo.

REM Opret virtual environment
echo [SETUP] Opretter virtuelt miljoe...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo [FEJL] Kunne ikke oprette virtuelt miljoe
        pause
        exit /b 1
    )
    echo        Virtuelt miljoe oprettet
) else (
    echo        Virtuelt miljoe eksisterer allerede
)
echo.

REM Aktiver virtual environment og installer dependencies
echo [INSTALL] Installerer Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if errorlevel 1 (
    echo [FEJL] Installation af Python dependencies mislykkedes
    pause
    exit /b 1
)
echo          Python dependencies installeret
echo.

REM Tjek om rxconfig.py allerede eksisterer
echo [CONFIG] Haandterer Reflex konfiguration...
if not exist "rxconfig.py" (
    echo         Opretter rxconfig.py (ingen eksisterende fil fundet)...
    reflex init --no-template >nul 2>&1
    if errorlevel 1 (
        echo [ADVARSEL] Kunne ikke oprette rxconfig.py automatisk
        echo            Du kan oprette den manuelt senere
    ) else (
        echo         rxconfig.py oprettet
    )
) else (
    echo         rxconfig.py eksisterer allerede - springer initialisering over
)
echo.

REM Installer Node.js dependencies uden at overskrive eksisterende kode
echo [FRONTEND] Installerer frontend dependencies...
reflex install >nul 2>&1

if errorlevel 1 (
    echo [ADVARSEL] Frontend dependencies installation havde problemer
    echo            Applikationen kan muligvis stadig virke
) else (
    echo           Frontend dependencies installeret
)
echo.

echo ===================================================
echo  INSTALLATION FULDFOERT!
echo ===================================================
echo.
echo Sikkerhedskopier gemt i: backup\
echo.
echo For at starte applikationen:
echo  1. Dobbeltklik paa START_APP.bat
echo  2. Eller koer: venv\Scripts\activate.bat ^&^& reflex run
echo.
echo Applikationen vil vaere tilgaengelig paa:
echo  - Frontend: http://localhost:3001/
echo  - Backend:  http://localhost:8001/
echo.
pause