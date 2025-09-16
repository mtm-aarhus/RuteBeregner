"""
Datamodeller for adresse håndtering
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid


@dataclass
class AddressModel:
    """Dataklasse der repræsenterer en modtager adresse med alle nødvendige felter."""
    
    # Identificering
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Modtager information
    anlaeg_id: str = ""  # Modtager anlæg id (unikt nummer)
    navn: str = ""
    adresse: str = ""
    postnr: str = ""
    by: str = ""
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konverterer AddressModel til dictionary for serialisering."""
        return {
            "id": self.id,
            "anlaeg_id": self.anlaeg_id,
            "navn": self.navn,
            "adresse": self.adresse,
            "postnr": self.postnr,
            "by": self.by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AddressModel':
        """Opretter AddressModel fra dictionary data."""
        # Filtrer kun kendte felter
        valid_fields = {
            field.name for field in cls.__dataclass_fields__.values()
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def is_valid(self) -> bool:
        """Checker om adressen har alle nødvendige felter."""
        return bool(
            self.anlaeg_id.strip() and
            self.navn.strip() and
            self.adresse.strip() and
            self.postnr.strip() and
            self.by.strip()
        )
    
    def get_full_address(self) -> str:
        """Returnerer den fulde adresse som en formateret streng."""
        return f"{self.adresse}, {self.postnr} {self.by}".strip()
    
    def get_display_name(self) -> str:
        """Returnerer et display navn til UI brug."""
        return f"{self.anlaeg_id} - {self.navn}"
    
    def validate_postnr(self) -> bool:
        """Validerer at postnummeret er gyldigt (4 cifre)."""
        return bool(self.postnr.isdigit() and len(self.postnr) == 4)
    
    def validate_anlaeg_id(self) -> bool:
        """Validerer at anlægs ID er gyldigt (ikke tomt)."""
        return bool(self.anlaeg_id.strip())