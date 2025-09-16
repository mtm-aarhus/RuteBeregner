"""
Enhanced parser for handling standardized Excel/CSV templates.
Integrates with the new validation system for comprehensive error checking.

Modul til parsing og ruteudtræk.
- Startadresse bygges fra K,L,M (Adresse, Postnummer, PostDistrikt)
- Slutadresse findes via hardkodet ModtageranlægID mapping
"""
import os
import io
from typing import List, Dict, Any, Union, Optional, Tuple

# Import RouteRow model
from models.route import RouteRow

try:
    # Hvis dit projekt bruger en pakke (fx components.address_mapping)
    from components.address_mapping import (
        get_receiver_address_by_id,
        get_receiver_name_by_id,
    )
except Exception:
    # Fallback til lokal sti
    from address_mapping import (
        get_receiver_address_by_id,
        get_receiver_name_by_id,
    )

import pandas as pd
from dataclasses import asdict

# Import validation system
from utils.validators import validate_uploaded_data, ValidationResult, ValidationError
from utils.template_utils import (
    validate_template_data, check_template_compatibility,
    MANDATORY_FIELDS, VALID_FUEL_TYPES, VALID_VEHICLE_TYPES
)

def parse_file_to_routes_with_validation(file: Any) -> Tuple[List[RouteRow], ValidationResult]:
    """
    Parser en uploadet CSV eller Excel fil til RouteRow objekter med fuld validering.
    
    Args:
        file: Kan være et file-objekt, bytes, eller et objekt med .read() metode
        
    Returns:
        Tuple med (liste af RouteRow objekter, ValidationResult)
    """
    # Parse file to raw data with enhanced error handling
    try:
        raw_data, parsing_errors = parse_file_enhanced(file)
    except Exception as e:
        # Create failed validation result
        validation_result = ValidationResult(is_valid=False)
        validation_result.errors.append(ValidationError(
            field="parsing",
            message=f"Fejl ved fil-parsing: {str(e)}"
        ))
        return [], validation_result
    
    # Validate data using comprehensive validation system
    validation_result = validate_uploaded_data(raw_data)
    
    # If validation failed, return empty routes with errors
    if not validation_result.is_valid:
        return [], validation_result
    
    # Convert to RouteRow objects using new template structure
    route_rows = []
    for i, row in enumerate(raw_data):
        try:
            route_row = create_route_row_from_template_data(row)
            route_rows.append(route_row)
        except Exception as e:
            # Add specific row processing error
            validation_result.errors.append(ValidationError(
                field="route_processing",
                message=f"Fejl ved behandling af række {i+1}: {str(e)}",
                row_number=i+1
            ))
    
    # Update validation status if route creation failed
    if validation_result.errors:
        validation_result.is_valid = False
    
    return route_rows, validation_result


def parse_file_to_routes(file: Any) -> List[RouteRow]:
    """
    Backwards compatibility wrapper. Parses file without comprehensive validation.
    For new implementations, use parse_file_to_routes_with_validation() instead.
    
    Args:
        file: Kan være et file-objekt, bytes, eller et objekt med .read() metode
        
    Returns:
        Liste af RouteRow objekter
    """
    route_rows, _ = parse_file_to_routes_with_validation(file)
    return route_rows

def parse_file_enhanced(file: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Enhanced parser with better error handling and format detection.
    
    Args:
        file: Kan være et file-objekt, bytes, eller et objekt med .read() metode
        
    Returns:
        Tuple med (parsed data, list of parsing warnings)
    """
    warnings = []
    
    # Get filename and content with improved error handling
    filename, content = _extract_file_content(file)
    
    # Detect file format with enhanced logic
    file_format, format_confidence = _detect_file_format(filename, content)
    
    if format_confidence < 0.8:
        warnings.append(f"Usikker filformat detektering (confidence: {format_confidence:.1%})")
    
    # Parse based on detected format with robust error handling
    try:
        if file_format == "excel":
            data = _parse_excel_robust(content, warnings)
        elif file_format == "csv":
            data = _parse_csv_robust(content, warnings)
        else:
            raise ValueError(f"Ikke-understøttet filformat: {file_format}")
            
        # Clean and normalize column names
        data = _normalize_column_names(data, warnings)
        
        return data, warnings
        
    except Exception as e:
        raise ValueError(f"Fejl ved parsing af {file_format} fil: {str(e)}")


def parse_file(file: Any) -> List[Dict[str, Any]]:
    """
    Backwards compatibility wrapper. For new implementations, use parse_file_enhanced().
    
    Args:
        file: Kan være et file-objekt, bytes, eller et objekt med .read() metode
        
    Returns:
        Liste af dictionaries med data fra filen
    """
    data, _ = parse_file_enhanced(file)
    return data


def _extract_file_content(file: Any) -> Tuple[str, bytes]:
    """
    Extracts filename and content from various file input types.
    
    Args:
        file: File input of various types
        
    Returns:
        Tuple of (filename, content_bytes)
    """
    filename = "uploaded_file"
    content = None
    
    # Extract filename
    if hasattr(file, "name") and file.name:
        filename = file.name
    elif hasattr(file, "filename") and file.filename:
        filename = file.filename
        
    # Extract content with improved error handling
    try:
        if isinstance(file, (bytes, bytearray)):
            content = bytes(file)
        elif hasattr(file, "read"):
            content = file.read()
            # Reset position if possible
            if hasattr(file, "seek"):
                try:
                    file.seek(0)
                except (AttributeError, OSError):
                    pass  # Some file-like objects don't support seek
        else:
            # Try to convert to bytes if it's a string
            try:
                content = str(file).encode('utf-8')
            except Exception:
                pass
    except Exception as e:
        raise ValueError(f"Fejl ved læsning af filindhold: {str(e)}")
    
    if content is None:
        raise ValueError("Kunne ikke læse filindhold")
        
    return filename, content


def _detect_file_format(filename: str, content: bytes) -> Tuple[str, float]:
    """
    Detects file format with confidence score.
    
    Args:
        filename: Name of the file
        content: File content bytes
        
    Returns:
        Tuple of (format_name, confidence_score)
    """
    confidence = 0.0
    file_format = "unknown"
    
    # Check filename extension first (high confidence)
    filename_lower = filename.lower()
    if filename_lower.endswith((".xlsx", ".xlsm")):
        file_format = "excel"
        confidence = 0.95
    elif filename_lower.endswith(".xls"):
        file_format = "excel"
        confidence = 0.90  # Slightly lower due to older format
    elif filename_lower.endswith(".csv"):
        file_format = "csv"
        confidence = 0.95
    else:
        # Analyze content for format detection
        if len(content) >= 2:
            # Excel files often start with "PK" (ZIP signature)
            if content[:2] == b"PK":
                file_format = "excel"
                confidence = 0.85
            # Check for common CSV patterns
            elif b"," in content[:1000] and b"\n" in content[:1000]:
                file_format = "csv"
                confidence = 0.75
            # Try to decode as text for CSV detection
            else:
                try:
                    text_content = content.decode('utf-8')[:1000]
                    if ',' in text_content and ('\n' in text_content or '\r' in text_content):
                        file_format = "csv"
                        confidence = 0.70
                except UnicodeDecodeError:
                    # Likely binary format (Excel)
                    file_format = "excel"
                    confidence = 0.60
    
    # Default fallback
    if file_format == "unknown":
        file_format = "csv"  # Safer default
        confidence = 0.40
    
    return file_format, confidence


def _parse_excel_robust(content: bytes, warnings: List[str]) -> List[Dict[str, Any]]:
    """
    Robust Excel parsing with multiple engine fallbacks.
    
    Args:
        content: Excel file content
        warnings: List to append warnings to
        
    Returns:
        List of dictionaries with parsed data
    """
    engines = ['openpyxl', 'xlrd', None]  # Try different engines
    
    for engine in engines:
        try:
            # Try reading with specific engine
            if engine:
                df = pd.read_excel(io.BytesIO(content), engine=engine)
            else:
                df = pd.read_excel(io.BytesIO(content))
                
            # Successfully parsed
            if engine and engine != 'openpyxl':
                warnings.append(f"Brugte {engine} engine til Excel parsing")
                
            return df.fillna("").to_dict("records")
            
        except Exception as e:
            if engine:
                warnings.append(f"Kunne ikke parse med {engine}: {str(e)}")
            continue
    
    # If all engines failed
    raise ValueError("Kunne ikke parse Excel fil med nogen af de tilgængelige engines")


def _parse_csv_robust(content: bytes, warnings: List[str]) -> List[Dict[str, Any]]:
    """
    Robust CSV parsing with multiple encoding and delimiter attempts.
    
    Args:
        content: CSV file content
        warnings: List to append warnings to
        
    Returns:
        List of dictionaries with parsed data
    """
    encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
    delimiters = [",", ";", "\t"]
    
    best_df = None
    best_score = 0
    best_config = None
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    io.BytesIO(content), 
                    encoding=encoding, 
                    delimiter=delimiter,
                    skipinitialspace=True
                )
                
                # Score this attempt based on reasonable criteria
                score = _score_csv_parse(df)
                
                if score > best_score:
                    best_df = df
                    best_score = score
                    best_config = (encoding, delimiter)
                    
            except Exception:
                continue
    
    if best_df is None:
        raise ValueError("Kunne ikke parse CSV fil med nogen af de understøttede encodings eller delimitere")
    
    # Add info about successful parsing
    encoding, delimiter = best_config
    if encoding != "utf-8" or delimiter != ",":
        warnings.append(f"CSV parseret med encoding: {encoding}, delimiter: '{delimiter}'")
    
    return best_df.fillna("").to_dict("records")


def _score_csv_parse(df: pd.DataFrame) -> float:
    """
    Scores a CSV parse attempt based on data quality indicators.
    
    Args:
        df: Parsed DataFrame
        
    Returns:
        Quality score (higher is better)
    """
    if df.empty:
        return 0.0
    
    score = 0.0
    
    # More columns usually means better delimiter detection
    score += min(len(df.columns) / 10, 1.0) * 30
    
    # More rows with data is good
    score += min(len(df) / 100, 1.0) * 20
    
    # Penalty for having too many empty columns
    empty_cols = sum(1 for col in df.columns if df[col].isna().all())
    score -= empty_cols * 5
    
    # Bonus for having expected column names
    expected_cols = set(MANDATORY_FIELDS)
    found_cols = set(df.columns)
    overlap = len(expected_cols.intersection(found_cols))
    score += overlap * 15
    
    # Penalty for very wide data (probably wrong delimiter)
    if len(df.columns) > 50:
        score -= 20
    
    return max(score, 0.0)


def _normalize_column_names(data: List[Dict[str, Any]], warnings: List[str]) -> List[Dict[str, Any]]:
    """
    Normalizes column names and provides mapping suggestions.
    
    Args:
        data: Parsed data with potentially messy column names
        warnings: List to append warnings to
        
    Returns:
        Data with normalized column names
    """
    if not data:
        return data
    
    # Create mapping for common column name variations
    column_mapping = {
        # Address fields
        "adresse": "Adresse",
        "gade": "Adresse", 
        "vejnavn": "Adresse",
        "street": "Adresse",
        
        # Postal code
        "postnummer": "Postnummer",
        "postnr": "Postnummer",
        "zip": "Postnummer",
        "postal_code": "Postnummer",
        
        # City
        "postdistrikt": "PostDistrikt",
        "by": "PostDistrikt",
        "city": "PostDistrikt",
        "bynavn": "PostDistrikt",
        
        # Receiver ID
        "modtageranlaegid": "ModtageranlægID",
        "modtager_anlaeg_id": "ModtageranlægID",
        "receiver_id": "ModtageranlægID",
        "anlaeg_id": "ModtageranlægID",
        
        # End address (new flexible field)
        "slutadresse": "SlutAdresse",
        "slut_adresse": "SlutAdresse",
        "end_address": "SlutAdresse",
        "destination": "SlutAdresse",
        "til": "SlutAdresse",
        
        # Optional fields
        "navn": "Navn",
        "name": "Navn",
        "firma": "Navn",
        "company": "Navn",
        
        "dato": "Dato",
        "date": "Dato",
        
        "koeretoejstype": "KøretøjsType",
        "vehicle_type": "KøretøjsType",
        "bil_type": "KøretøjsType",
        
        "lastvaegt": "LastVægt",
        "vaegt": "LastVægt",
        "weight": "LastVægt",
        "load_weight": "LastVægt",
        
        "braendstoftype": "Brændstoftype",
        "fuel_type": "Brændstoftype",
        "braendstof": "Brændstoftype"
    }
    
    # Get original column names
    original_columns = list(data[0].keys()) if data else []
    
    # Apply mapping
    normalized_data = []
    mappings_applied = {}
    
    for row in data:
        new_row = {}
        for old_col, value in row.items():
            # Normalize column name (remove spaces, lowercase for lookup)
            normalized_key = old_col.strip().lower().replace(" ", "")
            
            # Check if we have a mapping
            if normalized_key in column_mapping:
                new_col = column_mapping[normalized_key]
                new_row[new_col] = value
                if old_col != new_col:
                    mappings_applied[old_col] = new_col
            else:
                # Keep original if no mapping found
                new_row[old_col] = value
        
        normalized_data.append(new_row)
    
    # Report mappings applied
    if mappings_applied:
        mapping_info = ", ".join([f"'{old}' -> '{new}'" for old, new in mappings_applied.items()])
        warnings.append(f"Kolonne navne normaliseret: {mapping_info}")
    
    return normalized_data


def create_route_row_from_template_data(row: Dict[str, Any]) -> RouteRow:
    """
    Creates a RouteRow object from standardized template data.
    Supports flexible end address formats: address, coordinates, or receiver ID.
    
    Args:
        row: Dictionary with template-structured data
        
    Returns:
        RouteRow object
    """
    # Build start address from mandatory fields
    start_address = _fmt_start_address(row)
    
    # Find end address using flexible lookup - supports multiple formats
    end_address, company_name = _resolve_flexible_end_address(row)
    
    # Fallback company name if not resolved from end address lookup
    if not company_name:
        company_name = str(row.get("Navn") or "").strip() or "Ukendt virksomhed"
    
    # Extract and validate fuel type using new template values
    fuel_type = _normalize_fuel_type(row.get("Brændstoftype"))
    
    # Extract load mass from new template field
    load_mass = _extract_load_weight(row.get("LastVægt"))
    
    # Map vehicle type to vehicle class
    vehicle_class = _map_vehicle_type_to_class(row.get("KøretøjsType"))
    
    # Create RouteRow object
    route_row = RouteRow(
        company_name=company_name,
        start_address=start_address,
        end_address=end_address,
        fuel_type=fuel_type,
        load_mass_kg=load_mass,
        vehicle_class=vehicle_class,
        raw_data=row
    )
    
    return route_row


def _normalize_fuel_type(fuel_input: Any) -> str:
    """
    Normalizes fuel type input to standard values.
    
    Args:
        fuel_input: Raw fuel type input
        
    Returns:
        Standardized fuel type
    """
    if not fuel_input:
        return "diesel"  # Default
        
    fuel_str = str(fuel_input).strip().lower()
    
    # Direct matches
    if fuel_str in VALID_FUEL_TYPES:
        return fuel_str
    
    # Common variations
    fuel_mapping = {
        "gasoil": "diesel",
        "gasoline": "benzin",
        "petrol": "benzin",
        "electric": "el",
        "electricity": "el",
        "hybrid": "hybrid"
    }
    
    return fuel_mapping.get(fuel_str, "diesel")


def _extract_load_weight(weight_input: Any) -> float:
    """
    Extracts and validates load weight.
    
    Args:
        weight_input: Raw weight input
        
    Returns:
        Load weight in kg (0.0 if invalid)
    """
    if not weight_input:
        return 0.0
        
    try:
        weight = float(str(weight_input).replace(",", "."))  # Handle comma decimal separator
        return max(weight, 0.0)  # Ensure non-negative
    except (ValueError, TypeError):
        return 0.0


def _map_vehicle_type_to_class(vehicle_input: Any) -> str:
    """
    Maps template vehicle type to RouteRow vehicle class.
    
    Args:
        vehicle_input: Raw vehicle type from template
        
    Returns:
        Standardized vehicle class
    """
    if not vehicle_input:
        return "standard"
        
    vehicle_str = str(vehicle_input).strip().lower()
    
    # Mapping from template vehicle types to route classes
    type_mapping = {
        "personbil": "standard",
        "varebil": "vans",
        "lastbil": "truck",
        "trailer": "hgv",
        # English variants
        "car": "standard",
        "van": "vans", 
        "truck": "truck",
        "hgv": "hgv",
        "large": "large"
    }
    
    return type_mapping.get(vehicle_str, "standard")


def _fmt_start_address(row: Dict[str, Any]) -> str:
    """
    Bygger startadressen ud fra K (Adresse), L (Postnummer), M (PostDistrikt).
    """
    street = str(row.get("Adresse") or "").strip()
    postnr_raw = row.get("Postnummer")
    try:
        postnr = int(float(postnr_raw)) if str(postnr_raw) != "" else None
    except Exception:
        postnr = None
    by = str(row.get("PostDistrikt") or "").strip()
    if street and postnr and by:
        return f"{street}, {postnr} {by}"
    if street and by:
        return f"{street}, {by}"
    if street and postnr:
        return f"{street}, {postnr}"
    return street


def _resolve_flexible_end_address(row: Dict[str, Any]) -> Tuple[str, str]:
    """
    Resolves end address from multiple possible sources with flexible formats.
    
    Supports three formats for end address:
    1. Regular address string (e.g., "Rugvænget 18, 8444 Grenå")  
    2. Coordinates (e.g., "56.4167,10.7833" or "56.4167, 10.7833")
    3. Modtager anlæg ID (e.g., "1061") - looked up in address database
    
    Args:
        row: Dictionary with template data
        
    Returns:
        Tuple of (end_address, company_name)
    """
    # First check if there's a direct SlutAdresse field
    slut_adresse = str(row.get("SlutAdresse") or "").strip()
    
    # Also check ModtageranlægID field for backwards compatibility
    receiver_id = str(row.get("ModtageranlægID") or "").strip()
    
    # Use SlutAdresse if available, otherwise fall back to ModtageranlægID
    end_address_input = slut_adresse or receiver_id
    
    if not end_address_input:
        return "", ""
    
    # Try to detect what format we have
    format_type = _detect_end_address_format(end_address_input)
    
    if format_type == "coordinates":
        return _handle_coordinate_end_address(end_address_input)
    elif format_type == "receiver_id":
        return _handle_receiver_id_lookup(end_address_input)
    else:  # format_type == "address"
        return _handle_direct_address(end_address_input, row)


def _detect_end_address_format(address_input: str) -> str:
    """
    Detects the format of the end address input.
    
    Args:
        address_input: Raw input string
        
    Returns:
        Format type: "coordinates", "receiver_id", or "address"
    """
    import re
    
    # Check for coordinates pattern (two numbers separated by comma)
    coord_pattern = r'^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$'
    if re.match(coord_pattern, address_input):
        return "coordinates"
    
    # Check if it's just a number (likely receiver ID)
    if address_input.strip().isdigit():
        return "receiver_id"
    
    # Check if it looks like a short ID (alphanumeric, up to 10 chars)
    if len(address_input.strip()) <= 10 and address_input.strip().replace(" ", "").isalnum():
        # Could be receiver ID, but let's try to look it up first
        try:
            # Try to look it up as receiver ID
            lookup_result = get_receiver_address_by_id(address_input.strip())
            if lookup_result:
                return "receiver_id"
        except:
            pass
    
    # Default to treating as direct address
    return "address"


def _handle_coordinate_end_address(coord_input: str) -> Tuple[str, str]:
    """
    Handles coordinate-based end addresses.
    
    Args:
        coord_input: Coordinate string like "56.4167,10.7833"
        
    Returns:
        Tuple of (coordinate_string, empty_company_name)
    """
    import re
    
    # Extract and validate coordinates
    coord_pattern = r'^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$'
    match = re.match(coord_pattern, coord_input)
    
    if not match:
        return coord_input, ""  # Return as-is if parsing fails
        
    lat, lng = match.groups()
    
    try:
        lat_float = float(lat)
        lng_float = float(lng) 
        
        # Basic validation for Danish coordinates
        if 54.0 <= lat_float <= 58.0 and 8.0 <= lng_float <= 15.0:
            # Format nicely as coordinate string
            return f"{lat_float},{lng_float}", ""
        else:
            # Coordinates outside Denmark - might still be valid
            return f"{lat_float},{lng_float}", ""
            
    except ValueError:
        # If conversion fails, return original
        return coord_input, ""


def _handle_receiver_id_lookup(receiver_id: str) -> Tuple[str, str]:
    """
    Handles receiver ID lookup in address database.
    
    Args:
        receiver_id: Receiver facility ID
        
    Returns:
        Tuple of (end_address, company_name) from lookup
    """
    try:
        end_address = get_receiver_address_by_id(receiver_id) or ""
        company_name = get_receiver_name_by_id(receiver_id) or ""
        
        if not end_address:
            # If lookup fails, return the ID as-is with a note
            return f"Anlæg ID: {receiver_id}", ""
            
        return end_address, company_name
        
    except Exception:
        # If lookup fails completely, return the ID as-is
        return f"Anlæg ID: {receiver_id}", ""


def _handle_direct_address(address_input: str, row: Dict[str, Any]) -> Tuple[str, str]:
    """
    Handles direct address input.
    
    Args:
        address_input: Direct address string
        row: Full row data for additional context
        
    Returns:
        Tuple of (end_address, company_name_if_available)
    """
    # For direct addresses, use the input as-is
    # Try to get company name from row data if available
    company_name = str(row.get("Navn") or "").strip()
    
    return address_input, company_name

def validate_file_against_template(file: Any) -> Dict[str, Any]:
    """
    Validates an uploaded file against the standardized template.
    
    Args:
        file: File to validate
        
    Returns:
        Comprehensive validation report
    """
    try:
        # Parse file with enhanced error handling
        raw_data, parsing_warnings = parse_file_enhanced(file)
        
        # Run comprehensive validation
        validation_result = validate_uploaded_data(raw_data)
        
        # Check template compatibility
        compatibility = check_template_compatibility(raw_data)
        
        # Create comprehensive report
        report = {
            "parsing_successful": True,
            "parsing_warnings": parsing_warnings,
            "validation_result": asdict(validation_result),
            "compatibility_report": compatibility,
            "is_template_compatible": compatibility["compatible"],
            "overall_status": validation_result.is_valid and compatibility["compatible"],
            "row_count": len(raw_data),
            "recommendations": _generate_validation_recommendations(validation_result, compatibility)
        }
        
    except Exception as e:
        report = {
            "parsing_successful": False,
            "error": str(e),
            "validation_result": None,
            "compatibility_report": None,
            "is_template_compatible": False,
            "overall_status": False,
            "row_count": 0,
            "recommendations": ["Ret parsefejlen og prøv igen"]
        }
    
    return report


def _generate_validation_recommendations(validation_result: ValidationResult, compatibility: Dict[str, Any]) -> List[str]:
    """
    Generates actionable recommendations based on validation results.
    
    Args:
        validation_result: Validation result object
        compatibility: Template compatibility report
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Parsing and structure recommendations
    if not compatibility["compatible"]:
        recommendations.append("Download den officielle skabelon fra systemet")
        
    if compatibility["missing_mandatory"]:
        recommendations.append(f"Tilføj manglende obligatoriske kolonner: {', '.join(compatibility['missing_mandatory'])}")
        
    # Error-specific recommendations
    error_fields = validation_result.get_error_summary()
    if "Postnummer" in error_fields:
        recommendations.append("Kontroller at postnumre er 4-cifrede tal mellem 1000-9999")
        
    if "ModtageranlægID" in error_fields:
        recommendations.append("Kontroller at ModtageranlægID matcher de tilladte værdier i systemet")
        
    if "Adresse" in error_fields:
        recommendations.append("Sørg for at adresser indeholder både gadenavne og husnumre")
    
    # General recommendations
    if validation_result.has_warnings:
        recommendations.append("Gennemgå advarsler for at forbedre datakvaliteten")
        
    if len(recommendations) == 0 and validation_result.is_valid:
        recommendations.append("Data er klar til behandling - ingen yderligere handlinger påkrævet")
    
    return recommendations


def extract_route_data(file_data: List[Dict[str, Any]], _: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Backwards compatibility function. 
    Konverterer rå data til rute-data.
    Slutadresse slås op via ModtageranlægID i hardkodet mapping.
    """
    route_data: List[Dict[str, Any]] = []
    for i, row in enumerate(file_data):
        start_address = _fmt_start_address(row)
        receiver_id = row.get("ModtageranlægID")
        end_address = get_receiver_address_by_id(receiver_id)
        company_name = get_receiver_name_by_id(receiver_id) or str(row.get("Modtageranlæg navn") or row.get("Navn") or "")

        route_data.append({
            "id": str(i),
            "company_name": company_name,
            "start_address": start_address,
            "end_address": end_address,
            "start_coordinates": None,
            "end_coordinates": None,
            "raw_data": row,
        })
    return route_data
