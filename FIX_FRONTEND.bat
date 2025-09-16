@echo off
echo Fixer frontend dependencies...

if not exist venv\Scripts\activate.bat (
    echo Virtual environment ikke fundet!
    echo Koer foerst INSTALL.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Slet eksisterende .web mappe for at tvinge geninstallation
if exist .web (
    echo Sletter eksisterende frontend...
    rmdir /s /q .web
)

echo Reinstallerer frontend dependencies...
reflex init

if errorlevel 1 (
    echo Frontend installation mislykkedes
    echo Kontroller at Node.js er installeret fra https://nodejs.org
    pause
    exit /b 1
)

echo Frontend dependencies fixet!
echo Applikationen kan nu startes med START_APP.bat
pause
