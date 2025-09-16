"""
Utility functions for Excel/CSV template management and validation.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

# Template configuration
MANDATORY_FIELDS = [
    "Adresse",           # Start address street/road
    "Postnummer",        # Start address postal code  
    "PostDistrikt",      # Start address city
    "SlutAdresse"        # Flexible end address (address, coordinates, or facility ID)
]

OPTIONAL_FIELDS = [
    "Navn",              # Company/project name
    "Dato",              # Transport date
    "KøretøjsType",      # Vehicle type
    "LastVægt",          # Load weight in kg
    "Brændstoftype"      # Fuel type
]

ALL_FIELDS = MANDATORY_FIELDS + OPTIONAL_FIELDS

# Valid values for dropdown fields
VALID_FUEL_TYPES = ["diesel", "benzin", "el", "hybrid"]
VALID_VEHICLE_TYPES = ["Personbil", "Lastbil", "Varebil", "Trailer"]

# Valid ModtageranlægID values (imported from address_mapping)
try:
    from components.address_mapping import get_all_receiver_ids
    VALID_RECEIVER_IDS = get_all_receiver_ids()
except ImportError:
    # Fallback hardcoded values
    VALID_RECEIVER_IDS = [1061, 1013, 1327, 2191, 1901]


def validate_template_data(data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validates uploaded data against template requirements.
    
    Args:
        data: List of dictionaries from parsed file
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not data:
        errors.append("Ingen data fundet i filen")
        return False, errors
    
    # Check if mandatory columns exist in first row
    first_row = data[0]
    missing_mandatory = []
    for field in MANDATORY_FIELDS:
        if field not in first_row:
            missing_mandatory.append(field)
    
    if missing_mandatory:
        errors.append(f"Manglende obligatoriske kolonner: {', '.join(missing_mandatory)}")
    
    # Validate data content
    for row_idx, row in enumerate(data, 1):
        row_errors = []
        
        # Check mandatory fields are not empty
        for field in MANDATORY_FIELDS:
            value = row.get(field)
            if not value or str(value).strip() == "":
                row_errors.append(f"Obligatorisk felt '{field}' er tomt")
        
        # Validate postal code
        postal_code = row.get("Postnummer")
        if postal_code:
            try:
                postal_int = int(float(postal_code))
                if postal_int < 1000 or postal_int > 9999:
                    row_errors.append("Postnummer skal være mellem 1000 og 9999")
            except (ValueError, TypeError):
                row_errors.append("Postnummer skal være et gyldigt tal")
        
        # Validate SlutAdresse (can be address, coordinates, or facility ID)
        slut_adresse = row.get("SlutAdresse")
        if slut_adresse:
            slut_adresse_str = str(slut_adresse).strip()
            
            # Check if it's a facility ID (pure number)
            try:
                facility_id = int(float(slut_adresse_str))
                if facility_id not in VALID_RECEIVER_IDS:
                    row_errors.append(f"Ugyldigt anlæg ID: {facility_id}. Gyldige værdier: {VALID_RECEIVER_IDS}")
            except (ValueError, TypeError):
                # Not a number, check if it's coordinates (two numbers separated by comma, no spaces except around comma)
                if ',' in slut_adresse_str and len(slut_adresse_str.split(',')) == 2:
                    coord_parts = slut_adresse_str.split(',')
                    # Only treat as coordinates if both parts are valid numbers and no spaces/letters (except around comma)
                    try:
                        lat_str = coord_parts[0].strip()
                        lon_str = coord_parts[1].strip()
                        
                        # Check if both parts are purely numeric (with decimal point allowed)
                        if lat_str.replace('.', '').replace('-', '').isdigit() and lon_str.replace('.', '').replace('-', '').isdigit():
                            lat = float(lat_str)
                            lon = float(lon_str)
                            # Basic coordinate range validation for Denmark
                            if not (54.0 <= lat <= 58.0 and 8.0 <= lon <= 16.0):
                                row_errors.append(f"Koordinater ligger uden for Danmarks område: {slut_adresse_str}")
                        # If parts contain letters or spaces, it's likely an address, not coordinates
                    except (ValueError, TypeError):
                        # If conversion fails, it's likely an address, not coordinates
                        pass
                elif len(slut_adresse_str) < 5:
                    row_errors.append(f"SlutAdresse for kort: '{slut_adresse_str}'. Skal være adresse, koordinater eller anlæg ID")
                # If it's not coordinates or facility ID, assume it's an address (no further validation needed)
        
        # Validate fuel type if provided
        fuel_type = row.get("Brændstoftype")
        if fuel_type and str(fuel_type).strip():
            fuel_normalized = str(fuel_type).strip().lower()
            if fuel_normalized not in VALID_FUEL_TYPES:
                row_errors.append(f"Ugyldig brændstoftype: {fuel_type}. Gyldige værdier: {VALID_FUEL_TYPES}")
        
        # Validate vehicle type if provided  
        vehicle_type = row.get("KøretøjsType")
        if vehicle_type and str(vehicle_type).strip():
            if str(vehicle_type).strip() not in VALID_VEHICLE_TYPES:
                row_errors.append(f"Ugyldig køretøjstype: {vehicle_type}. Gyldige værdier: {VALID_VEHICLE_TYPES}")
        
        # Validate load weight if provided
        load_weight = row.get("LastVægt")
        if load_weight and str(load_weight).strip():
            try:
                weight_float = float(load_weight)
                if weight_float < 0:
                    row_errors.append("LastVægt skal være et positivt tal")
            except (ValueError, TypeError):
                row_errors.append("LastVægt skal være et gyldigt tal")
        
        # Add row-specific errors
        if row_errors:
            errors.append(f"Række {row_idx}: {'; '.join(row_errors)}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_template_info() -> Dict[str, Any]:
    """
    Returns information about the template structure.
    
    Returns:
        Dictionary with template configuration
    """
    return {
        "mandatory_fields": MANDATORY_FIELDS,
        "optional_fields": OPTIONAL_FIELDS,
        "all_fields": ALL_FIELDS,
        "valid_fuel_types": VALID_FUEL_TYPES,
        "valid_vehicle_types": VALID_VEHICLE_TYPES,
        "valid_receiver_ids": VALID_RECEIVER_IDS,
        "template_files": {
            "excel": "templates/jord_transport_template.xlsx",
            "csv": "templates/jord_transport_template.csv"
        }
    }


def check_template_compatibility(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Checks how well uploaded data matches template structure.
    
    Args:
        data: Parsed file data
        
    Returns:
        Compatibility report dictionary
    """
    if not data:
        return {
            "compatible": False,
            "score": 0.0,
            "issues": ["Ingen data fundet"],
            "suggestions": ["Upload en fil med data"]
        }
    
    first_row = data[0]
    found_fields = list(first_row.keys())
    
    # Calculate compatibility score
    mandatory_found = sum(1 for field in MANDATORY_FIELDS if field in found_fields)
    optional_found = sum(1 for field in OPTIONAL_FIELDS if field in found_fields)
    
    mandatory_score = mandatory_found / len(MANDATORY_FIELDS)
    optional_score = optional_found / len(OPTIONAL_FIELDS) if OPTIONAL_FIELDS else 1.0
    
    # Weight mandatory fields more heavily
    overall_score = (mandatory_score * 0.8) + (optional_score * 0.2)
    
    issues = []
    suggestions = []
    
    # Check for missing mandatory fields
    missing_mandatory = [field for field in MANDATORY_FIELDS if field not in found_fields]
    if missing_mandatory:
        issues.append(f"Mangler obligatoriske kolonner: {', '.join(missing_mandatory)}")
        suggestions.append("Tilføj de manglende obligatoriske kolonner til din fil")
    
    # Check for unexpected fields
    unexpected_fields = [field for field in found_fields if field not in ALL_FIELDS]
    if unexpected_fields:
        issues.append(f"Uventede kolonner fundet: {', '.join(unexpected_fields)}")
        suggestions.append("Fjern eller omdøb uventede kolonner for bedre kompatibilitet")
    
    # Check for missing useful optional fields
    useful_optional = ["Navn", "Brændstoftype", "LastVægt"]
    missing_useful = [field for field in useful_optional if field not in found_fields]
    if missing_useful:
        suggestions.append(f"Overvej at tilføje nyttige kolonner: {', '.join(missing_useful)}")
    
    compatible = mandatory_score == 1.0 and len(issues) <= 1  # Allow unexpected fields
    
    return {
        "compatible": compatible,
        "score": overall_score,
        "mandatory_coverage": mandatory_score,
        "optional_coverage": optional_score,
        "found_fields": found_fields,
        "missing_mandatory": missing_mandatory,
        "unexpected_fields": unexpected_fields,
        "issues": issues,
        "suggestions": suggestions
    }


def get_template_download_paths() -> Dict[str, Optional[str]]:
    """
    Returns paths to template files if they exist.
    
    Returns:
        Dictionary with paths to Excel and CSV templates
    """
    base_path = Path(__file__).parent.parent  # Go up from utils/ to project root
    
    excel_path = base_path / "templates" / "jord_transport_template.xlsx"
    csv_path = base_path / "templates" / "jord_transport_template.csv"
    
    return {
        "excel": str(excel_path) if excel_path.exists() else None,
        "csv": str(csv_path) if csv_path.exists() else None
    }


def regenerate_templates() -> Dict[str, str]:
    """
    Regenerates the template files.
    
    Returns:
        Dictionary with paths to generated templates
    """
    try:
        # Import and run the template creation
        from templates.create_excel_template import create_excel_template, create_csv_template
        
        excel_path = create_excel_template()
        csv_path = create_csv_template()
        
        return {
            "excel": excel_path,
            "csv": csv_path,
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def format_validation_report(is_valid: bool, errors: List[str]) -> str:
    """
    Formats validation results for display.
    
    Args:
        is_valid: Whether validation passed
        errors: List of validation errors
        
    Returns:
        Formatted report string
    """
    if is_valid:
        return "[SUCCESS] Fil valideret succesfuldt! Data er klar til behandling."
    
    report_lines = ["[ERROR] Validering fejlede. Følgende problemer skal rettes:"]
    report_lines.extend(f"- {error}" for error in errors)
    
    report_lines.append("")
    report_lines.append("[TIP] Download den korrekte skabelon og prøv igen.")
    
    return "\n".join(report_lines)