"""
CO2 beregningsmodul til beregning af CO2 udslip baseret på brændstoftype og køretøjsparametre.
"""
import json
import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CO2ConfigError(Exception):
    """Custom exception for CO2 configuration errors."""
    pass


class CO2ConfigLoader:
    """Klasse til indlæsning og håndtering af CO2 emissionskonfiguration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CO2 configuration loader.
        
        Args:
            config_path: Path to CO2 configuration file. If None, uses default path.
        """
        if config_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "co2_emissions.json"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load CO2 configuration from JSON file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"CO2 config file not found: {self.config_path}")
                self._use_fallback_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self._validate_config()
            logger.info(f"CO2 configuration loaded from {self.config_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in CO2 config file: {e}")
            self._use_fallback_config()
        except Exception as e:
            logger.error(f"Error loading CO2 config: {e}")
            self._use_fallback_config()
    
    def _validate_config(self):
        """Validate loaded configuration structure."""
        required_keys = ['emission_factors', 'fuel_consumption', 'load_multipliers']
        
        for key in required_keys:
            if key not in self.config:
                raise CO2ConfigError(f"Missing required config section: {key}")
        
        # Validate emission factors
        emission_factors = self.config['emission_factors']
        for fuel_type in ['diesel', 'benzin', 'el']:
            if fuel_type not in emission_factors:
                raise CO2ConfigError(f"Missing emission factor for fuel type: {fuel_type}")
            
            if not isinstance(emission_factors[fuel_type], (int, float)):
                raise CO2ConfigError(f"Invalid emission factor for {fuel_type}")
        
        logger.debug("CO2 configuration validation passed")
    
    def _use_fallback_config(self):
        """Use hardcoded fallback configuration."""
        logger.warning("Using fallback CO2 configuration")
        self.config = {
            "emission_factors": {
                "diesel": 2.68,
                "benzin": 2.31,
                "el": 0.15,
                "hybrid": 1.5
            },
            "fuel_consumption": {
                "vans": {"diesel": 8.5, "benzin": 9.2, "el": 20.0, "hybrid": 6.5},
                "truck": {"diesel": 25.0, "benzin": 28.0, "el": 50.0, "hybrid": 20.0},
                "hgv": {"diesel": 35.0, "benzin": 40.0, "el": 80.0, "hybrid": 28.0},
                "standard": {"diesel": 7.0, "benzin": 8.0, "el": 18.0, "hybrid": 5.5}
            },
            "load_multipliers": {
                "ranges": [
                    {"max_kg": 500, "multiplier": 1.0},
                    {"max_kg": 1000, "multiplier": 1.1},
                    {"max_kg": 2000, "multiplier": 1.2},
                    {"max_kg": 5000, "multiplier": 1.4},
                    {"max_kg": 10000, "multiplier": 1.6},
                    {"max_kg": 999999, "multiplier": 1.8}
                ]
            }
        }
    
    def get_emission_factor(self, fuel_type: str) -> float:
        """
        Get emission factor for a specific fuel type.
        
        Args:
            fuel_type: Type of fuel (diesel, benzin, el, hybrid)
            
        Returns:
            Emission factor in kg CO2e per liter
        """
        fuel_type = fuel_type.lower()
        emission_factors = self.config.get('emission_factors', {})
        
        if fuel_type in emission_factors:
            return float(emission_factors[fuel_type])
        
        # Fallback values
        fallback_factors = {
            'diesel': 2.68,
            'benzin': 2.31,
            'el': 0.15,
            'hybrid': 1.5
        }
        
        if fuel_type in fallback_factors:
            logger.warning(f"Using fallback emission factor for {fuel_type}")
            return fallback_factors[fuel_type]
        
        logger.warning(f"Unknown fuel type {fuel_type}, using diesel fallback")
        return fallback_factors['diesel']
    
    def get_fuel_consumption(self, vehicle_class: str, fuel_type: str) -> float:
        """
        Get fuel consumption for a specific vehicle class and fuel type.
        
        Args:
            vehicle_class: Class of vehicle (vans, truck, hgv, standard)
            fuel_type: Type of fuel (diesel, benzin, el, hybrid)
            
        Returns:
            Fuel consumption in liters per 100km (or kWh per 100km for electric)
        """
        vehicle_class = vehicle_class.lower()
        fuel_type = fuel_type.lower()
        
        fuel_consumption = self.config.get('fuel_consumption', {})
        
        # Normalize vehicle class names
        if vehicle_class in ['van', 'vans']:
            vehicle_class = 'vans'
        elif vehicle_class in ['truck', 'trucks']:
            vehicle_class = 'truck'
        elif vehicle_class in ['hgv', 'heavy']:
            vehicle_class = 'hgv'
        else:
            vehicle_class = 'standard'
        
        if vehicle_class in fuel_consumption and fuel_type in fuel_consumption[vehicle_class]:
            return float(fuel_consumption[vehicle_class][fuel_type])
        
        # Fallback to standard vehicle class
        if fuel_type in fuel_consumption.get('standard', {}):
            logger.warning(f"Using standard vehicle class consumption for {vehicle_class}")
            return float(fuel_consumption['standard'][fuel_type])
        
        # Ultimate fallback values
        fallback_consumption = {
            'diesel': 7.0,
            'benzin': 8.0,
            'el': 18.0,
            'hybrid': 5.5
        }
        
        consumption = fallback_consumption.get(fuel_type, 7.0)
        logger.warning(f"Using fallback consumption for {vehicle_class}/{fuel_type}: {consumption}")
        return consumption
    
    def get_load_multiplier(self, load_mass_kg: float) -> float:
        """
        Get load multiplier based on cargo mass.
        
        Args:
            load_mass_kg: Load mass in kilograms
            
        Returns:
            Multiplier factor for fuel consumption adjustment
        """
        if load_mass_kg < 0:
            return 1.0
        
        load_multipliers = self.config.get('load_multipliers', {})
        ranges = load_multipliers.get('ranges', [])
        
        for range_config in ranges:
            if load_mass_kg <= range_config.get('max_kg', 0):
                return float(range_config.get('multiplier', 1.0))
        
        # Fallback for very heavy loads
        return 1.8


# Global configuration loader instance
_config_loader: Optional[CO2ConfigLoader] = None


def get_config_loader() -> CO2ConfigLoader:
    """Get global CO2 configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = CO2ConfigLoader()
    return _config_loader


def calculate_co2(distance_km: float, fuel_type: str, load_mass_kg: float = 0.0, 
                  vehicle_class: str = "standard") -> float:
    """
    Calculate CO2 emissions for a route based on distance and vehicle parameters.
    
    Args:
        distance_km: Distance in kilometers
        fuel_type: Type of fuel (diesel, benzin, el, hybrid)
        load_mass_kg: Load mass in kilograms (default: 0.0)
        vehicle_class: Vehicle class (vans, truck, hgv, standard) (default: standard)
        
    Returns:
        CO2 emissions in kg CO2e
    """
    if distance_km <= 0:
        return 0.0
    
    config = get_config_loader()
    
    try:
        # Get base fuel consumption for vehicle class and fuel type
        base_consumption = config.get_fuel_consumption(vehicle_class, fuel_type)
        
        # Apply load multiplier
        load_multiplier = config.get_load_multiplier(load_mass_kg)
        adjusted_consumption = base_consumption * load_multiplier
        
        # Calculate actual fuel used (liters or kWh per 100km)
        fuel_used = (distance_km / 100.0) * adjusted_consumption
        
        # Get emission factor
        emission_factor = config.get_emission_factor(fuel_type)
        
        # Calculate total CO2 emissions
        co2_emissions = fuel_used * emission_factor
        
        logger.debug(f"CO2 calculation: {distance_km}km, {fuel_type}, {load_mass_kg}kg, {vehicle_class} = {co2_emissions:.2f}kg CO2e")
        
        return co2_emissions
        
    except Exception as e:
        logger.error(f"Error calculating CO2 emissions: {e}")
        return 0.0


def calculate_co2_for_route(route: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate CO2 emissions for a route dictionary.
    
    Args:
        route: Route dictionary containing distance and vehicle parameters
        
    Returns:
        Tuple of (co2_emissions, calculation_details)
    """
    try:
        distance_km = route.get('distance_km', 0.0)
        fuel_type = route.get('fuel_type', 'diesel')
        load_mass_kg = route.get('load_mass_kg', 0.0)
        vehicle_class = route.get('vehicle_class', 'standard')
        
        if distance_km <= 0:
            return 0.0, {"error": "Distance not available"}
        
        co2_emissions = calculate_co2(distance_km, fuel_type, load_mass_kg, vehicle_class)
        
        # Calculation details for transparency
        config = get_config_loader()
        details = {
            "distance_km": distance_km,
            "fuel_type": fuel_type,
            "load_mass_kg": load_mass_kg,
            "vehicle_class": vehicle_class,
            "base_consumption": config.get_fuel_consumption(vehicle_class, fuel_type),
            "load_multiplier": config.get_load_multiplier(load_mass_kg),
            "emission_factor": config.get_emission_factor(fuel_type),
            "co2_kg": co2_emissions
        }
        
        return co2_emissions, details
        
    except Exception as e:
        logger.error(f"Error calculating CO2 for route: {e}")
        return 0.0, {"error": str(e)}


def calculate_scenario_comparison(routes: list, fuel_type_a: str, fuel_type_b: str) -> Dict[str, Any]:
    """
    Compare CO2 emissions between two fuel type scenarios.
    
    Args:
        routes: List of route dictionaries
        fuel_type_a: First fuel type to compare
        fuel_type_b: Second fuel type to compare
        
    Returns:
        Dictionary with comparison results
    """
    try:
        scenario_a_total = 0.0
        scenario_b_total = 0.0
        route_comparisons = []
        
        for route in routes:
            if route.get('distance_km', 0) <= 0:
                continue
                
            # Calculate for scenario A
            route_a = route.copy()
            route_a['fuel_type'] = fuel_type_a
            co2_a, _ = calculate_co2_for_route(route_a)
            
            # Calculate for scenario B
            route_b = route.copy()
            route_b['fuel_type'] = fuel_type_b
            co2_b, _ = calculate_co2_for_route(route_b)
            
            scenario_a_total += co2_a
            scenario_b_total += co2_b
            
            route_comparisons.append({
                "route_id": route.get('id', ''),
                "distance_km": route.get('distance_km', 0),
                f"{fuel_type_a}_co2": co2_a,
                f"{fuel_type_b}_co2": co2_b,
                "difference": co2_b - co2_a,
                "percent_change": ((co2_b - co2_a) / co2_a * 100) if co2_a > 0 else 0
            })
        
        total_difference = scenario_b_total - scenario_a_total
        percent_change = (total_difference / scenario_a_total * 100) if scenario_a_total > 0 else 0
        
        return {
            "fuel_type_a": fuel_type_a,
            "fuel_type_b": fuel_type_b,
            "scenario_a_total": scenario_a_total,
            "scenario_b_total": scenario_b_total,
            "total_difference": total_difference,
            "percent_change": percent_change,
            "routes_processed": len([r for r in routes if r.get('distance_km', 0) > 0]),
            "route_comparisons": route_comparisons
        }
        
    except Exception as e:
        logger.error(f"Error in scenario comparison: {e}")
        return {
            "error": str(e),
            "fuel_type_a": fuel_type_a,
            "fuel_type_b": fuel_type_b
        }