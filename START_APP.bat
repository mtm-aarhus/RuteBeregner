@echo off
echo Starter Jord Transport...

if not exist venv\Scripts\activate.bat (
    echo Virtual environment ikke fundet!
    echo Koer foerst INSTALL.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo Starter webserver...
echo Applikationen vil aabne i browseren paa http://localhost:3002
echo.
echo Luk IKKE dette vindue mens applikationen koerer
echo Tryk Ctrl+C for at stoppe applikationen
echo.

reflex run
pause
