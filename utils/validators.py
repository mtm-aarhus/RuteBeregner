"""
Comprehensive data validation system for the Jord Transport application.

This module provides ValidationError and ValidationWarning classes along with 
a DataValidator class that performs real-time validation of uploaded data.
"""
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ValidationError:
    """Represents a validation error that prevents data processing."""
    field: str
    message: str
    row_number: Optional[int] = None
    value: Any = None
    severity: str = "error"
    
    def __str__(self) -> str:
        """String representation of the validation error."""
        if self.row_number is not None:
            return f"Række {self.row_number}, felt '{self.field}': {self.message}"
        return f"Felt '{self.field}': {self.message}"


@dataclass 
class ValidationWarning:
    """Represents a validation warning that indicates potential issues."""
    field: str
    message: str
    row_number: Optional[int] = None
    value: Any = None
    severity: str = "warning"
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the validation warning."""
        base_msg = f"Række {self.row_number}, felt '{self.field}': {self.message}" if self.row_number is not None else f"Felt '{self.field}': {self.message}"
        if self.suggestion:
            return f"{base_msg} (Forslag: {self.suggestion})"
        return base_msg


@dataclass
class ValidationResult:
    """Complete validation result with errors, warnings and metadata."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    row_count: int = 0
    field_count: int = 0
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def has_errors(self) -> bool:
        """Returns True if there are validation errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Returns True if there are validation warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> Dict[str, int]:
        """Returns a summary of error types and counts."""
        summary = {}
        for error in self.errors:
            summary[error.field] = summary.get(error.field, 0) + 1
        return summary
    
    def get_formatted_report(self) -> str:
        """Returns a formatted validation report."""
        lines = []
        
        if self.is_valid:
            lines.append("✓ VALIDERING GENNEMFØRT SUCCESFULDT")
            lines.append(f"  Antal rækker: {self.row_count}")
            lines.append(f"  Antal felter: {self.field_count}")
        else:
            lines.append("✗ VALIDERING FEJLEDE")
            lines.append(f"  Antal fejl: {len(self.errors)}")
            lines.append(f"  Antal advarsler: {len(self.warnings)}")
            
        if self.errors:
            lines.append("\nFEJL:")
            for error in self.errors:
                lines.append(f"  • {error}")
                
        if self.warnings:
            lines.append("\nADVARSLER:")
            for warning in self.warnings:
                lines.append(f"  • {warning}")
                
        return "\n".join(lines)


class DataValidator:
    """
    Main validation class that validates uploaded data against template requirements.
    
    Provides real-time validation with comprehensive error and warning reporting.
    """
    
    def __init__(self):
        """Initialize the validator with template configuration."""
        # Import template configuration
        from utils.template_utils import (
            MANDATORY_FIELDS, OPTIONAL_FIELDS, ALL_FIELDS,
            VALID_FUEL_TYPES, VALID_VEHICLE_TYPES, VALID_RECEIVER_IDS
        )
        
        self.mandatory_fields = MANDATORY_FIELDS
        self.optional_fields = OPTIONAL_FIELDS
        self.all_fields = ALL_FIELDS
        self.valid_fuel_types = VALID_FUEL_TYPES
        self.valid_vehicle_types = VALID_VEHICLE_TYPES 
        self.valid_receiver_ids = VALID_RECEIVER_IDS
        
        # Regex patterns for validation
        self.postal_code_pattern = re.compile(r'^\d{4}$')
        self.address_pattern = re.compile(r'^.+\s+\d+.*$')  # Street name + number pattern
        
    def validate_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        Comprehensive validation of DataFrame data.
        
        Args:
            df: Pandas DataFrame with uploaded data
            
        Returns:
            ValidationResult with errors, warnings and metadata
        """
        result = ValidationResult(
            is_valid=True,
            row_count=len(df),
            field_count=len(df.columns)
        )
        
        # Validate structure first
        structure_errors = self.validate_structure(df)
        result.errors.extend(structure_errors)
        
        # Only continue with content validation if structure is valid
        if not structure_errors:
            # Validate required fields content
            required_errors = self.validate_required_fields(df)
            result.errors.extend(required_errors)
            
            # Validate optional fields (generates warnings)
            optional_warnings = self.validate_optional_fields(df)
            result.warnings.extend(optional_warnings)
            
            # Type and format validation
            format_errors, format_warnings = self.validate_formats_and_types(df)
            result.errors.extend(format_errors)
            result.warnings.extend(format_warnings)
        
        # Set final validation status
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def validate_structure(self, df: pd.DataFrame) -> List[ValidationError]:
        """
        Validates the basic structure and presence of required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append(ValidationError(
                field="structure",
                message="Filen indeholder ingen data"
            ))
            return errors
        
        # Check for required columns
        missing_columns = []
        df_columns = [col.strip() for col in df.columns]  # Remove whitespace
        
        for field in self.mandatory_fields:
            if field not in df_columns:
                missing_columns.append(field)
        
        if missing_columns:
            errors.append(ValidationError(
                field="structure",
                message=f"Manglende obligatoriske kolonner: {', '.join(missing_columns)}"
            ))
        
        # Check for duplicate columns
        if len(df.columns) != len(set(df.columns)):
            duplicates = [col for col in df.columns if list(df.columns).count(col) > 1]
            errors.append(ValidationError(
                field="structure", 
                message=f"Duplikerede kolonner fundet: {', '.join(set(duplicates))}"
            ))
        
        return errors
    
    def validate_required_fields(self, df: pd.DataFrame) -> List[ValidationError]:
        """
        Validates that all required fields contain valid data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of validation errors for required fields
        """
        errors = []
        
        for index, row in df.iterrows():
            row_number = index + 1
            
            for field in self.mandatory_fields:
                if field not in df.columns:
                    continue  # Skip if column doesn't exist (handled in structure validation)
                    
                value = row[field]
                
                # Check for empty values
                if pd.isna(value) or str(value).strip() == "":
                    errors.append(ValidationError(
                        field=field,
                        message="Obligatorisk felt er tomt",
                        row_number=row_number,
                        value=value
                    ))
                    continue
                
                # Field-specific validation
                if field == "Postnummer":
                    errors.extend(self._validate_postal_code(value, row_number))
                elif field == "SlutAdresse":
                    errors.extend(self._validate_slut_adresse(value, row_number))
                elif field == "Adresse":
                    errors.extend(self._validate_address_format(value, row_number))
        
        return errors
    
    def validate_optional_fields(self, df: pd.DataFrame) -> List[ValidationWarning]:
        """
        Validates optional fields and provides warnings for missing or suspicious data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            List of validation warnings for optional fields
        """
        warnings = []
        
        # Check for missing useful optional fields
        missing_useful_fields = []
        useful_optional_fields = ["Navn", "Brændstoftype", "LastVægt", "KøretøjsType"]
        
        for field in useful_optional_fields:
            if field not in df.columns:
                missing_useful_fields.append(field)
        
        if missing_useful_fields:
            warnings.append(ValidationWarning(
                field="optional_fields",
                message=f"Manglende nyttige kolonner: {', '.join(missing_useful_fields)}",
                suggestion="Tilføj disse kolonner for bedre rapportering"
            ))
        
        # Validate existing optional field contents
        for index, row in df.iterrows():
            row_number = index + 1
            
            for field in self.optional_fields:
                if field not in df.columns:
                    continue
                    
                value = row[field]
                
                # Skip empty values for optional fields
                if pd.isna(value) or str(value).strip() == "":
                    continue
                
                # Field-specific optional validation
                if field == "Brændstoftype":
                    warnings.extend(self._validate_fuel_type(value, row_number))
                elif field == "KøretøjsType":
                    warnings.extend(self._validate_vehicle_type(value, row_number))
                elif field == "LastVægt":
                    warnings.extend(self._validate_load_weight(value, row_number))
                elif field == "Dato":
                    warnings.extend(self._validate_date_format(value, row_number))
        
        return warnings
    
    def validate_formats_and_types(self, df: pd.DataFrame) -> Tuple[List[ValidationError], List[ValidationWarning]]:
        """
        Validates data types and formats across all fields.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (errors, warnings) lists
        """
        errors = []
        warnings = []
        
        # Check for rows with all missing values
        for index, row in df.iterrows():
            row_number = index + 1
            non_empty_values = sum(1 for val in row.values if not pd.isna(val) and str(val).strip() != "")
            
            if non_empty_values == 0:
                errors.append(ValidationError(
                    field="row_data",
                    message="Række indeholder ingen data",
                    row_number=row_number
                ))
            elif non_empty_values < len(self.mandatory_fields):
                warnings.append(ValidationWarning(
                    field="row_data", 
                    message=f"Række har kun {non_empty_values} udfyldte felter",
                    row_number=row_number,
                    suggestion="Kontroller at alle obligatoriske felter er udfyldt"
                ))
        
        # Check for suspicious patterns
        for column in df.columns:
            if column not in self.all_fields:
                warnings.append(ValidationWarning(
                    field=column,
                    message=f"Ukendt kolonne '{column}' fundet",
                    suggestion="Fjern eller omdøb kolonne for bedre kompatibilitet"
                ))
        
        return errors, warnings
    
    def validate_address_format(self, address: str) -> bool:
        """
        Validates if an address string has a reasonable format.
        
        Args:
            address: Address string to validate
            
        Returns:
            True if address format appears valid
        """
        if not address or not isinstance(address, str):
            return False
            
        address = address.strip()
        
        # Basic checks
        if len(address) < 5:  # Too short to be a real address
            return False
        
        if len(address) > 200:  # Unreasonably long
            return False
        
        # Should contain at least letters and numbers
        has_letters = bool(re.search(r'[a-zA-ZæøåÆØÅ]', address))
        has_numbers = bool(re.search(r'\d', address))
        
        return has_letters and has_numbers
    
    def _validate_postal_code(self, value: Any, row_number: int) -> List[ValidationError]:
        """Validates postal code format and range."""
        errors = []
        
        try:
            # Convert to int, handling float strings
            postal_code = int(float(str(value)))
            
            if postal_code < 1000 or postal_code > 9999:
                errors.append(ValidationError(
                    field="Postnummer",
                    message=f"Postnummer {postal_code} er ikke i det gyldige område (1000-9999)",
                    row_number=row_number,
                    value=value
                ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                field="Postnummer", 
                message=f"Ugyldigt postnummer format: '{value}'",
                row_number=row_number,
                value=value
            ))
            
        return errors
    
    def _validate_slut_adresse(self, value: Any, row_number: int) -> List[ValidationError]:
        """Validates SlutAdresse - can be address, coordinates, or facility ID."""
        errors = []
        
        if not value or str(value).strip() == "":
            return errors
            
        slut_adresse_str = str(value).strip()
        
        # Check if it's a facility ID (pure number)
        try:
            facility_id = int(float(slut_adresse_str))
            if facility_id not in self.valid_receiver_ids:
                errors.append(ValidationError(
                    field="SlutAdresse",
                    message=f"Ugyldigt anlæg ID: {facility_id}. Gyldige værdier: {self.valid_receiver_ids}",
                    row_number=row_number,
                    value=value
                ))
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
                            errors.append(ValidationError(
                                field="SlutAdresse",
                                message=f"Koordinater ligger uden for Danmarks område: {slut_adresse_str}",
                                row_number=row_number,
                                value=value
                            ))
                    # If parts contain letters or spaces, it's likely an address, not coordinates
                except (ValueError, TypeError):
                    # If conversion fails, it's likely an address, not coordinates
                    pass
            elif len(slut_adresse_str) < 5:
                errors.append(ValidationError(
                    field="SlutAdresse",
                    message=f"SlutAdresse for kort: '{slut_adresse_str}'. Skal være adresse, koordinater eller anlæg ID",
                    row_number=row_number,
                    value=value
                ))
            # If it's not coordinates or facility ID, assume it's an address (no further validation needed)
            
        return errors
    
    def _validate_address_format(self, value: Any, row_number: int) -> List[ValidationError]:
        """Validates address format."""
        errors = []
        
        if not self.validate_address_format(value):
            errors.append(ValidationError(
                field="Adresse",
                message=f"Adresse format ser ikke korrekt ud: '{value}'",
                row_number=row_number,
                value=value
            ))
            
        return errors
    
    def _validate_fuel_type(self, value: Any, row_number: int) -> List[ValidationWarning]:
        """Validates fuel type against known types."""
        warnings = []
        
        fuel_type = str(value).strip().lower()
        
        if fuel_type not in self.valid_fuel_types:
            warnings.append(ValidationWarning(
                field="Brændstoftype",
                message=f"Ukendt brændstoftype: '{value}'",
                row_number=row_number,
                value=value,
                suggestion=f"Gyldige værdier: {', '.join(self.valid_fuel_types)}"
            ))
            
        return warnings
    
    def _validate_vehicle_type(self, value: Any, row_number: int) -> List[ValidationWarning]:
        """Validates vehicle type against known types.""" 
        warnings = []
        
        vehicle_type = str(value).strip()
        
        if vehicle_type not in self.valid_vehicle_types:
            warnings.append(ValidationWarning(
                field="KøretøjsType",
                message=f"Ukendt køretøjstype: '{value}'",
                row_number=row_number,
                value=value,
                suggestion=f"Gyldige værdier: {', '.join(self.valid_vehicle_types)}"
            ))
            
        return warnings
    
    def _validate_load_weight(self, value: Any, row_number: int) -> List[ValidationWarning]:
        """Validates load weight format and reasonableness."""
        warnings = []
        
        try:
            weight = float(value)
            
            if weight < 0:
                warnings.append(ValidationWarning(
                    field="LastVægt",
                    message=f"Negativ vægt: {weight} kg",
                    row_number=row_number,
                    value=value,
                    suggestion="LastVægt skal være et positivt tal"
                ))
            elif weight > 50000:  # 50 tonnes seems excessive
                warnings.append(ValidationWarning(
                    field="LastVægt",
                    message=f"Meget høj vægt: {weight} kg",
                    row_number=row_number,
                    value=value,
                    suggestion="Kontroller at vægten er korrekt"
                ))
        except (ValueError, TypeError):
            warnings.append(ValidationWarning(
                field="LastVægt",
                message=f"Ugyldigt vægt format: '{value}'",
                row_number=row_number,
                value=value,
                suggestion="LastVægt skal være et tal"
            ))
            
        return warnings
    
    def _validate_date_format(self, value: Any, row_number: int) -> List[ValidationWarning]:
        """Validates date format."""
        warnings = []
        
        # Try to parse various date formats
        date_formats = [
            "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", 
            "%d.%m.%Y", "%Y/%m/%d", "%m/%d/%Y"
        ]
        
        date_str = str(value).strip()
        valid_date = False
        
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                valid_date = True
                break
            except ValueError:
                continue
        
        if not valid_date:
            warnings.append(ValidationWarning(
                field="Dato",
                message=f"Ugyldigt datoformat: '{value}'",
                row_number=row_number,
                value=value,
                suggestion="Brug format som YYYY-MM-DD eller DD/MM/YYYY"
            ))
            
        return warnings


def validate_uploaded_data(data: List[Dict[str, Any]]) -> ValidationResult:
    """
    Convenience function to validate uploaded data using the DataValidator.
    
    Args:
        data: List of dictionaries from uploaded file
        
    Returns:
        ValidationResult with comprehensive validation information
    """
    if not data:
        result = ValidationResult(is_valid=False)
        result.errors.append(ValidationError(
            field="data",
            message="Ingen data fundet i den uploadede fil"
        ))
        return result
    
    # Convert to DataFrame for validation
    df = pd.DataFrame(data)
    
    # Use DataValidator
    validator = DataValidator()
    return validator.validate_data(df)


def get_validation_summary(result: ValidationResult) -> Dict[str, Any]:
    """
    Generates a summary dictionary from validation results.
    
    Args:
        result: ValidationResult to summarize
        
    Returns:
        Dictionary with validation summary information
    """
    return {
        "is_valid": result.is_valid,
        "total_errors": len(result.errors),
        "total_warnings": len(result.warnings),
        "row_count": result.row_count,
        "field_count": result.field_count,
        "error_fields": list(result.get_error_summary().keys()),
        "validation_timestamp": result.validation_timestamp.isoformat(),
        "formatted_report": result.get_formatted_report()
    }