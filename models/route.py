"""
Datamodeller for rute håndtering
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
import uuid


@dataclass
class RouteRow:
    """Dataklasse der repræsenterer en enkelt transportrute med metadata og beregningsresultater."""
    
    # Identificering
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Firma information
    company_name: str = ""
    
    # Adresser
    start_address: str = ""
    end_address: str = ""
    
    # Koordinater (latitude, longitude)
    start_coordinates: Optional[Tuple[float, float]] = None
    end_coordinates: Optional[Tuple[float, float]] = None
    
    # Afstand beregning
    distance_km: Optional[float] = None
    distance_label: str = ""  # Formateret streng for UI visning
    
    # Transport detaljer
    fuel_type: str = "diesel"  # diesel, benzin, el, hybrid
    load_mass_kg: float = 0.0
    vehicle_class: str = "standard"  # standard, large, truck
    
    # CO₂ beregning
    co2_kg: Optional[float] = None
    
    # Rå data fra upload
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konverterer RouteRow til dictionary for serialisering."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "start_address": self.start_address,
            "end_address": self.end_address,
            "start_coordinates": self.start_coordinates,
            "end_coordinates": self.end_coordinates,
            "distance_km": self.distance_km,
            "distance_label": self.distance_label,
            "fuel_type": self.fuel_type,
            "load_mass_kg": self.load_mass_kg,
            "vehicle_class": self.vehicle_class,
            "co2_kg": self.co2_kg,
            "raw_data": self.raw_data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RouteRow':
        """Opretter RouteRow fra dictionary data."""
        # Filtrer kun kendte felter
        valid_fields = {
            field.name for field in cls.__dataclass_fields__.values()
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def has_coordinates(self) -> bool:
        """Checker om ruten har gyldige start og slut koordinater."""
        return (
            self.start_coordinates is not None 
            and self.end_coordinates is not None
            and len(self.start_coordinates) == 2
            and len(self.end_coordinates) == 2
        )
    
    def has_addresses(self) -> bool:
        """Checker om ruten har gyldige start og slut adresser."""
        return bool(self.start_address.strip() and self.end_address.strip())
    
    def is_complete(self) -> bool:
        """Checker om ruten har enten koordinater eller adresser til beregning."""
        return self.has_coordinates() or self.has_addresses()