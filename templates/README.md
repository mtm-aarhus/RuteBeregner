# Jord Transport Excel/CSV Skabeloner

Dette dokument beskriver de standardiserede skabeloner til Jord Transport systemet.

## Oversigt

Systemet tilbyder to skabelon formater:
- **Excel skabelon** (anbefalet): Avancerede funktioner med validering og beskyttelse
- **CSV skabelon**: Simpel tekstbaseret format til grundlæggende brug

## Skabelon Struktur

### Obligatoriske Felter (SKAL udfyldes)

| Felt | Beskrivelse | Eksempel |
|------|-------------|----------|
| `Adresse` | Startadressens gade og husnummer | "Nørregade 10" |
| `Postnummer` | Startadressens postnummer (4 cifre) | 1000 |
| `PostDistrikt` | Startadressens by/distrikt | "København" |
| `ModtageranlægID` | ID til lookup af slutadresse | 1061 |

### Valgfrie Felter

| Felt | Beskrivelse | Gyldige Værdier | Eksempel |
|------|-------------|-----------------|----------|
| `Navn` | Virksomheds- eller projektnavn | Fri tekst | "ABC Transport" |
| `Dato` | Transport dato | YYYY-MM-DD format | "2024-08-26" |
| `KøretøjsType` | Type køretøj | Personbil, Lastbil, Varebil, Trailer | "Lastbil" |
| `LastVægt` | Vægt af last i kg | Positivt tal | 2500 |
| `Brændstoftype` | Brændstoftype | diesel, benzin, el, hybrid | "diesel" |

## Gyldige ModtageranlægID Værdier

| ID | Navn | Adresse |
|----|------|---------|
| 1061 | Gert Svith, Birkesig Grusgrav | Rugvænget 18, 8444 Grenå |
| 1013 | JJ Grus A/S (Kalbygård Grusgrav) | Hovedvejen 24A, 8670 Låsby |
| 1327 | Johs. Sørensen & Sønner A/S, Ren depotjord | Holmstrupgårdvej 9, 8220 Brabrand |
| 2191 | JJ Grus A/S (Ans) | Søndermarksgade 43, 8643 Ans |
| 1901 | EHJ Energi & Miljø A/S - Let forurenet jord | Hadstenvej 16, 8940 Randers SV |

## Excel Skabelon Funktioner

### Header Beskyttelse
- Header rækken er beskyttet mod ændringer
- Password: `jordtransport2024`
- Kun data celler (række 2+) kan redigeres

### Data Validering
- **Postnummer**: Skal være mellem 1000-9999
- **Brændstoftype**: Dropdown med gyldige værdier
- **KøretøjsType**: Dropdown med gyldige værdier
- **ModtageranlægID**: Numerisk validering

### Arkstruktur
1. **Data**: Hovedark til data indtastning
2. **Instruktioner**: Detaljeret vejledning og eksempler
3. **Gyldige_IDs**: Reference tabel for ModtageranlægID

## Anvendelse

### 1. Download Skabelon
```bash
# Fra applikationen
# Klik på "Download Excel" eller "Download CSV" knappen
```

### 2. Udfyld Data
- Start med obligatoriske felter
- Tilføj valgfrie felter efter behov
- Følg dataformat reglerne

### 3. Validering
- Excel: Indbygget validering advarer om fejl
- CSV: Validering sker ved upload

### 4. Upload
- Upload til Jord Transport systemet
- Systemet validerer automatisk
- Fejl vises med instruktioner

## Eksempel Data Række

```
Adresse: "Nørregade 10"
Postnummer: 1000
PostDistrikt: "København"
ModtageranlægID: 1061
Navn: "ABC Transport"
Dato: "2024-08-26"
KøretøjsType: "Lastbil"
LastVægt: 2500
Brændstoftype: "diesel"
```

## Fejlfinding

### Almindelige Problemer

**Problem**: "Manglende obligatoriske kolonner"
**Løsning**: Sørg for alle obligatoriske kolonner eksisterer med korrekte navne

**Problem**: "Ugyldigt ModtageranlægID"
**Løsning**: Brug kun ID'er fra den gyldige liste ovenfor

**Problem**: "Postnummer skal være mellem 1000 og 9999"
**Løsning**: Kontroller postnummer format og værdi

**Problem**: "Ugyldig brændstoftype"
**Løsning**: Brug kun: diesel, benzin, el, eller hybrid

### Validering Fejlede
1. Download ny skabelon
2. Kopier data til skabelonen
3. Kontroller obligatoriske felter
4. Ret fejl og upload igen

## Teknisk Information

### Fil Formater
- **Excel**: .xlsx format (anbefalet)
- **CSV**: UTF-8 kodning, komma-separeret

### Filstørrelse Grænser
- Maksimum: 10MB
- Anbefalet: Under 5MB for hurtig behandling

### Validering Regler
Se `utils/template_utils.py` for detaljerede validering regler.

### Skabelon Generering
Kør `python templates/create_excel_template.py` for at genskabe skabeloner.

## Support

Ved problemer med skabeloner:
1. Kontroller denne dokumentation
2. Download ny skabelon
3. Følg eksempel data format
4. Kontakt systemadministrator hvis problemet fortsætter

---
*Sidst opdateret: 2024-08-26*