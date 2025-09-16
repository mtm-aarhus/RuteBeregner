# Jord Transport - Lokal Installation

## Forudsaetninger
- Windows 10/11
- Python 3.8+ installeret (download fra https://python.org)
- Node.js LTS installeret (download fra https://nodejs.org)
- Internetforbindelse (kun under installation)

## Installation
1. Dobbeltklik paa INSTALL.bat
2. Vent til installationen er faerdig (kan tage 5-10 minutter)
3. Dobbeltklik paa START_APP.bat

## Foerste gang brug
1. Applikationen aabner automatisk i browseren
2. Upload din Excel-fil med adresser
3. Konfigurer indstillinger efter behov

## Problemloesning

### Python ikke fundet
- Download Python fra https://python.org
- Vaelg "Add Python to PATH" under installationen

### Node.js ikke fundet
- Download Node.js LTS fra https://nodejs.org
- Genstart computeren efter installation

### Installation fejler
- Kontroller internetforbindelse
- Koer INSTALL.bat som administrator
- Slet .web mappen hvis den eksisterer og koer INSTALL.bat igen

### "Cannot find module tslib" fejl
- Koer INSTALL.bat igen (sikrer at alle dependencies installeres)
- Eller koer manuelt: reflex init

### Applikationen starter ikke
- Kontroller at INSTALL.bat er koert succesfuldt
- Proev at koere START_APP.bat som administrator

### Port allerede i brug
- Luk andre applikationer der bruger port 3002 eller 8002
- Eller rediger rxconfig.py for at aendre porte

## Support
Ved problemer, kontakt udvikleren med fejlbesked og systemoplysninger.
