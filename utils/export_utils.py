"""
Export utility funktioner til CSV og Excel eksport af rutedata.
"""
import pandas as pd
import io
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def format_data_for_export(route_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Konverterer route_data til pandas DataFrame med alle relevante kolonner.
    
    Args:
        route_data: Liste af rute dictionaries
        
    Returns:
        pandas DataFrame med formateret data
    """
    if not route_data:
        return pd.DataFrame()
    
    # Definer kolonnenavne på dansk
    columns = [
        'Rute Nr.',
        'Virksomhed',
        'Start Adresse', 
        'Slut Adresse',
        'Afstand (km)',
        'Brændstoftype',
        'Køretøjsklasse', 
        'Last (kg)',
        'CO₂ Udslip (kg)',
        'Status',
        'Fejlbesked'
    ]
    
    formatted_data = []
    
    for idx, route in enumerate(route_data):
        # Beregn status baseret på tilgængelig data
        if route.get('error_status'):
            status = 'Fejl'
        elif route.get('distance_km', 0) > 0:
            status = 'Beregnet'
        else:
            status = 'Afventer'
            
        row = [
            idx + 1,  # Rute Nr.
            route.get('company_name', '') or '',  # Virksomhed
            route.get('start_address', '') or '',  # Start Adresse
            route.get('end_address', '') or '',   # Slut Adresse
            round(route.get('distance_km', 0), 2) if route.get('distance_km') else '',  # Afstand
            route.get('fuel_type', 'diesel') or 'diesel',  # Brændstoftype
            route.get('vehicle_class', 'standard') or 'standard',  # Køretøjsklasse
            route.get('load_mass_kg', 0) or 0,    # Last
            round(route.get('co2_kg', 0), 2) if route.get('co2_kg') else '',  # CO₂
            status,  # Status
            route.get('error_status', '') or ''   # Fejlbesked
        ]
        formatted_data.append(row)
    
    df = pd.DataFrame(formatted_data, columns=columns)
    return df


def export_to_csv_bytes(route_data: List[Dict[str, Any]], include_timestamp: bool = True) -> bytes:
    """
    Eksporterer rutedata til CSV format som bytes.
    
    Args:
        route_data: Liste af rute dictionaries
        include_timestamp: Om der skal inkluderes tidsstempel i filnavnet
        
    Returns:
        CSV data som bytes
    """
    try:
        df = format_data_for_export(route_data)
        
        if df.empty:
            raise ValueError("Ingen data at eksportere")
        
        # Opret CSV med UTF-8 BOM for Excel kompatibilitet
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig', sep=';', decimal=',')
        csv_content = output.getvalue()
        
        # Konverter til bytes med UTF-8 BOM
        csv_bytes = csv_content.encode('utf-8-sig')
        
        logger.info(f"CSV eksport færdig: {len(df)} ruter")
        return csv_bytes
        
    except Exception as e:
        logger.error(f"Fejl ved CSV eksport: {e}")
        raise


def export_to_excel_bytes(route_data: List[Dict[str, Any]], include_timestamp: bool = True) -> bytes:
    """
    Eksporterer rutedata til Excel format som bytes.
    
    Args:
        route_data: Liste af rute dictionaries
        include_timestamp: Om der skal inkluderes tidsstempel i filnavnet
        
    Returns:
        Excel data som bytes
    """
    try:
        df = format_data_for_export(route_data)
        
        if df.empty:
            raise ValueError("Ingen data at eksportere")
        
        # Opret Excel fil i hukommelsen
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Rutedata', index=False)
            
            # Tilføj formatering til Excel ark
            workbook = writer.book
            worksheet = writer.sheets['Rutedata']
            
            # Header formatering
            header_font = workbook.create_named_style("header")
            header_font.font.bold = True
            header_font.font.color = "FFFFFF"
            header_font.fill.patternType = "solid"
            header_font.fill.start_color = "2563EB"  # Blå farve
            
            # Anvend header formatering
            for cell in worksheet[1]:  # Første række (headers)
                cell.style = header_font
            
            # Auto-tilpas kolonnebredder
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Sæt bredde (med minimum og maksimum)
                adjusted_width = min(max(max_length + 2, 10), 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_bytes = output.getvalue()
        
        logger.info(f"Excel eksport færdig: {len(df)} ruter")
        return excel_bytes
        
    except Exception as e:
        logger.error(f"Fejl ved Excel eksport: {e}")
        raise


def generate_export_filename(format_type: str, include_timestamp: bool = True) -> str:
    """
    Genererer filnavn til eksport.
    
    Args:
        format_type: 'csv' eller 'excel'
        include_timestamp: Om der skal inkluderes tidsstempel
        
    Returns:
        Genereret filnavn
    """
    base_name = "rutedata"
    
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{base_name}_{timestamp}"
    
    if format_type.lower() == 'csv':
        return f"{base_name}.csv"
    elif format_type.lower() in ['excel', 'xlsx']:
        return f"{base_name}.xlsx"
    elif format_type.lower() == 'pdf':
        return f"{base_name}.pdf"
    elif format_type.lower() in ['txt', 'text']:
        return f"{base_name}.txt"
    else:
        raise ValueError(f"Ukendt format type: {format_type}")


def get_export_summary(route_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Returnerer sammenfatning af data der vil blive eksporteret.
    
    Args:
        route_data: Liste af rute dictionaries
        
    Returns:
        Dictionary med sammenfatning
    """
    if not route_data:
        return {
            "total_routes": 0,
            "calculated_routes": 0,
            "error_routes": 0,
            "pending_routes": 0
        }
    
    calculated_routes = len([r for r in route_data if r.get('distance_km', 0) > 0])
    error_routes = len([r for r in route_data if r.get('error_status')])
    pending_routes = len(route_data) - calculated_routes - error_routes
    
    return {
        "total_routes": len(route_data),
        "calculated_routes": calculated_routes,
        "error_routes": error_routes,
        "pending_routes": pending_routes
    }