"""
Rapport generator for RuteBeregner applikationen.
Nu kun tekstrapporter - PDF removed pga. Windows compatibility issues.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ReportGeneratorError(Exception):
    """Custom exception for report generation errors."""
    pass


def calculate_summary_statistics(routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Beregner sammenfatningsststatistikker for ruterne.
    
    Args:
        routes: Liste af rute dictionaries
        
    Returns:
        Dictionary med sammenfatningssttatistikker
    """
    if not routes:
        return {
            "total_routes": 0,
            "total_distance": 0.0,
            "total_co2": 0.0,
            "longest_route": None,
            "fuel_types": {},
            "vehicle_classes": {},
            "calculated_routes": 0,
            "routes_with_errors": 0
        }
    
    total_distance = 0.0
    total_co2 = 0.0
    longest_route = None
    longest_distance = 0.0
    fuel_types = {}
    vehicle_classes = {}
    calculated_routes = 0
    routes_with_errors = 0
    
    for route in routes:
        # Distance statistikker
        distance = route.get('distance_km', 0)
        if distance > 0:
            total_distance += distance
            calculated_routes += 1
            
            if distance > longest_distance:
                longest_distance = distance
                longest_route = {
                    'start_address': route.get('start_address', ''),
                    'end_address': route.get('end_address', ''),
                    'distance_km': distance,
                    'company_name': route.get('company_name', '')
                }
        
        # CO2 statistikker
        co2 = route.get('co2_kg', 0)
        if co2 > 0:
            total_co2 += co2
        
        # Fuel type statistikker
        fuel_type = route.get('fuel_type', 'unknown')
        fuel_types[fuel_type] = fuel_types.get(fuel_type, 0) + 1
        
        # Vehicle class statistikker
        vehicle_class = route.get('vehicle_class', 'unknown')
        vehicle_classes[vehicle_class] = vehicle_classes.get(vehicle_class, 0) + 1
        
        # Fejl statistikker
        if route.get('error_status') or route.get('co2_error'):
            routes_with_errors += 1
    
    return {
        "total_routes": len(routes),
        "total_distance": round(total_distance, 2),
        "total_co2": round(total_co2, 2),
        "longest_route": longest_route,
        "fuel_types": fuel_types,
        "vehicle_classes": vehicle_classes,
        "calculated_routes": calculated_routes,
        "routes_with_errors": routes_with_errors
    }


def calculate_co2_comparison(routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Beregner CO2 sammenligning mellem diesel og el for ruterne.
    
    Args:
        routes: Liste af rute dictionaries
        
    Returns:
        Dictionary med CO2 sammenligningsdata
    """
    try:
        from utils.co2_calculator import calculate_scenario_comparison
    except ImportError:
        logger.warning("CO2 calculator ikke tilgængelig for sammenligning")
        return {
            "diesel_total": 0.0,
            "electric_total": 0.0,
            "savings": 0.0,
            "percent_reduction": 0.0,
            "routes_compared": 0
        }
    
    # Filter ruter med distance data
    routes_with_distance = [
        route for route in routes 
        if route.get('distance_km', 0) > 0
    ]
    
    if not routes_with_distance:
        return {
            "diesel_total": 0.0,
            "electric_total": 0.0,
            "savings": 0.0,
            "percent_reduction": 0.0,
            "routes_compared": 0
        }
    
    try:
        comparison = calculate_scenario_comparison(routes_with_distance, 'diesel', 'el')
        
        if 'error' in comparison:
            logger.error(f"CO2 sammenligning fejl: {comparison['error']}")
            return {
                "diesel_total": 0.0,
                "electric_total": 0.0,
                "savings": 0.0,
                "percent_reduction": 0.0,
                "routes_compared": 0
            }
        
        diesel_total = comparison.get('scenario_a_total', 0.0)
        electric_total = comparison.get('scenario_b_total', 0.0)
        savings = diesel_total - electric_total
        percent_reduction = abs(comparison.get('percent_change', 0.0))
        
        return {
            "diesel_total": round(diesel_total, 2),
            "electric_total": round(electric_total, 2),
            "savings": round(savings, 2),
            "percent_reduction": round(percent_reduction, 1),
            "routes_compared": len(routes_with_distance)
        }
        
    except Exception as e:
        logger.error(f"Fejl ved CO2 sammenligning: {e}")
        return {
            "diesel_total": 0.0,
            "electric_total": 0.0,
            "savings": 0.0,
            "percent_reduction": 0.0,
            "routes_compared": 0
        }


def get_html_template() -> str:
    """Returnerer HTML template for PDF rapporten."""
    return """
<!DOCTYPE html>
<html lang="da">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ruteberegning Rapport</title>
    <style>
        {{ css_styles }}
    </style>
</head>
<body>
    <!-- Forside -->
    <div class="cover-page">
        <div class="header">
            <div class="logo-section">
                <h1>Teknik og Miljø</h1>
                <p class="subtitle">Beregning af kørte afstande</p>
            </div>
            <div class="date-section">
                <p>{{ report_date }}</p>
            </div>
        </div>
        
        <div class="cover-content">
            <h2>Ruterapport</h2>
            
            <div class="key-metrics">
                <div class="metric-card">
                    <h3>{{ stats.total_routes }}</h3>
                    <p>Antal ruter</p>
                </div>
                <div class="metric-card">
                    <h3>{{ stats.total_distance }} km</h3>
                    <p>Samlet afstand</p>
                </div>
                <div class="metric-card">
                    <h3>{{ stats.calculated_routes }}</h3>
                    <p>Beregnede ruter</p>
                </div>
                <div class="metric-card">
                    <h3>{{ stats.total_co2 }} kg</h3>
                    <p>Total CO₂ udslip</p>
                </div>
            </div>
            
            {% if stats.longest_route %}
            <div class="longest-route">
                <h3>Længste rute</h3>
                <p><strong>{{ stats.longest_route.company_name }}</strong></p>
                <p>{{ stats.longest_route.start_address }} → {{ stats.longest_route.end_address }}</p>
                <p><strong>{{ stats.longest_route.distance_km }} km</strong></p>
            </div>
            {% endif %}
            
            {% if co2_comparison.routes_compared > 0 %}
            <div class="co2-comparison">
                <h3>CO₂ Sammenligning: Diesel vs. Elbiler</h3>
                <div class="comparison-stats">
                    <div class="comparison-item">
                        <span class="fuel-type diesel">Diesel:</span>
                        <span class="co2-value">{{ co2_comparison.diesel_total }} kg CO₂</span>
                    </div>
                    <div class="comparison-item">
                        <span class="fuel-type electric">Elbiler:</span>
                        <span class="co2-value">{{ co2_comparison.electric_total }} kg CO₂</span>
                    </div>
                    <div class="comparison-savings">
                        <span class="savings-label">Besparelse:</span>
                        <span class="savings-value">{{ co2_comparison.savings }} kg CO₂ ({{ co2_comparison.percent_reduction }}%)</span>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
    
    <!-- Side med detaljeret ruteliste -->
    <div class="page-break"></div>
    
    <div class="routes-page">
        <h2>Detaljeret Ruteliste</h2>
        
        {% if routes %}
        <table class="routes-table">
            <thead>
                <tr>
                    <th>Nr.</th>
                    <th>Virksomhed</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th>Afstand</th>
                    <th>Brændstof</th>
                    <th>CO₂</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for route in routes %}
                <tr class="{% if route.error_status or route.co2_error %}error-row{% endif %}">
                    <td>{{ loop.index }}</td>
                    <td>{{ route.company_name or '-' }}</td>
                    <td>{{ route.start_address or '-' }}</td>
                    <td>{{ route.end_address or '-' }}</td>
                    <td>
                        {% if route.distance_km %}
                            {{ "%.2f"|format(route.distance_km) }} km
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td>{{ route.fuel_type or 'diesel' }}</td>
                    <td>
                        {% if route.co2_kg %}
                            {{ "%.2f"|format(route.co2_kg) }} kg
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td>
                        {% if route.error_status %}
                            <span class="error">Fejl</span>
                        {% elif route.co2_error %}
                            <span class="warning">CO₂ fejl</span>
                        {% elif route.distance_km %}
                            <span class="success">OK</span>
                        {% else %}
                            <span class="pending">Venter</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="no-routes">Ingen ruter at vise.</p>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>Genereret {{ report_date }} | Teknik og Miljø</p>
    </div>
</body>
</html>
"""


def get_css_styles() -> str:
    """Returnerer CSS stilarter for PDF rapporten."""
    return """
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .cover-page {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 3cm;
            padding-bottom: 1cm;
            border-bottom: 3px solid #2563eb;
        }
        
        .logo-section h1 {
            font-size: 2.5rem;
            color: #2563eb;
            margin: 0;
            font-weight: bold;
        }
        
        .logo-section .subtitle {
            font-size: 1.2rem;
            color: #6b7280;
            margin: 0.5rem 0 0 0;
        }
        
        .date-section p {
            font-size: 1rem;
            color: #6b7280;
            margin: 0;
        }
        
        .cover-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .cover-content h2 {
            font-size: 3rem;
            color: #1f2937;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .key-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .metric-card {
            background: #f8fafc;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
        }
        
        .metric-card h3 {
            font-size: 2.5rem;
            color: #2563eb;
            margin: 0 0 0.5rem 0;
            font-weight: bold;
        }
        
        .metric-card p {
            font-size: 1.1rem;
            color: #6b7280;
            margin: 0;
        }
        
        .longest-route {
            background: #fef3c7;
            border: 2px solid #f59e0b;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .longest-route h3 {
            color: #92400e;
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        .longest-route p {
            margin: 0.5rem 0;
            color: #78350f;
        }
        
        .co2-comparison {
            background: #ecfdf5;
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 2rem;
        }
        
        .co2-comparison h3 {
            color: #064e3b;
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        .comparison-stats {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .comparison-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
        }
        
        .fuel-type.diesel {
            color: #dc2626;
            font-weight: bold;
        }
        
        .fuel-type.electric {
            color: #059669;
            font-weight: bold;
        }
        
        .comparison-savings {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            border-top: 2px solid #10b981;
            margin-top: 1rem;
            font-weight: bold;
        }
        
        .savings-label {
            color: #064e3b;
        }
        
        .savings-value {
            color: #059669;
            font-size: 1.2rem;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .routes-page h2 {
            color: #2563eb;
            font-size: 2rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.5rem;
        }
        
        .routes-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        
        .routes-table th,
        .routes-table td {
            border: 1px solid #d1d5db;
            padding: 0.75rem;
            text-align: left;
            vertical-align: top;
        }
        
        .routes-table th {
            background-color: #2563eb;
            color: white;
            font-weight: bold;
        }
        
        .routes-table tr:nth-child(even) {
            background-color: #f9fafb;
        }
        
        .routes-table tr.error-row {
            background-color: #fef2f2;
        }
        
        .status-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .success {
            color: #065f46;
            background-color: #d1fae5;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .error {
            color: #991b1b;
            background-color: #fee2e2;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .warning {
            color: #92400e;
            background-color: #fef3c7;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .pending {
            color: #6b7280;
            background-color: #f3f4f6;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .no-routes {
            text-align: center;
            color: #6b7280;
            font-style: italic;
            padding: 3rem;
        }
        
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.9rem;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
            padding: 1rem;
            background: white;
        }
    """


def generate_report(routes: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> bytes:
    """
    PDF generation er ikke længere understøttet.
    
    Args:
        routes: Liste af rute dictionaries
        metadata: Valgfri metadata for rapporten
        
    Returns:
        PDF som bytes
        
    Raises:
        ReportGeneratorError: PDF ikke understøttet
    """
    raise ReportGeneratorError("PDF generation er fjernet pga. Windows compatibility. Brug tekstrapport i stedet.")


def generate_fallback_report(routes: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Genererer tekstbaseret rapport som fallback hvis PDF generering fejler.
    
    Args:
        routes: Liste af rute dictionaries
        metadata: Valgfri metadata for rapporten
        
    Returns:
        Rapport som tekst streng
    """
    stats = calculate_summary_statistics(routes)
    co2_comparison = calculate_co2_comparison(routes)
    
    report_lines = [
        "=" * 60,
        "TEKNIK OG MILJØ - RUTERAPPORT",
        "=" * 60,
        f"Genereret: {datetime.now().strftime('%d. %B %Y')}",
        "",
        "NØGLETAL:",
        f"  Antal ruter: {stats['total_routes']}",
        f"  Samlet afstand: {stats['total_distance']} km",
        f"  Beregnede ruter: {stats['calculated_routes']}",
        f"  Total CO₂ udslip: {stats['total_co2']} kg",
        "",
    ]
    
    if stats['longest_route']:
        report_lines.extend([
            "LÆNGSTE RUTE:",
            f"  Virksomhed: {stats['longest_route']['company_name']}",
            f"  Fra: {stats['longest_route']['start_address']}",
            f"  Til: {stats['longest_route']['end_address']}",
            f"  Afstand: {stats['longest_route']['distance_km']} km",
            "",
        ])
    
    if co2_comparison['routes_compared'] > 0:
        report_lines.extend([
            "CO₂ SAMMENLIGNING (Diesel vs. Elbiler):",
            f"  Diesel: {co2_comparison['diesel_total']} kg CO₂",
            f"  Elbiler: {co2_comparison['electric_total']} kg CO₂",
            f"  Besparelse: {co2_comparison['savings']} kg CO₂ ({co2_comparison['percent_reduction']}%)",
            "",
        ])
    
    report_lines.extend([
        "DETALJERET RUTELISTE:",
        "-" * 60,
    ])
    
    for i, route in enumerate(routes, 1):
        status = "Fejl" if route.get('error_status') else "OK" if route.get('distance_km') else "Venter"
        distance = f"{route.get('distance_km', 0):.2f} km" if route.get('distance_km') else "-"
        co2 = f"{route.get('co2_kg', 0):.2f} kg" if route.get('co2_kg') else "-"
        
        report_lines.extend([
            f"{i:3d}. {route.get('company_name', '-')}",
            f"     Fra: {route.get('start_address', '-')}",
            f"     Til: {route.get('end_address', '-')}",
            f"     Afstand: {distance}, CO₂: {co2}, Status: {status}",
            "",
        ])
    
    return "\n".join(report_lines)