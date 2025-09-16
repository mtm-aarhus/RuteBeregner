"""
TxtFileDatabase for address storage using CSV format
"""
import csv
import os
import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from models.address import AddressModel


class AddressStorageError(Exception):
    """Custom exception for address storage errors"""
    pass


class TxtFileDatabase:
    """
    Database klasse til at gemme og håndtere adresser i en CSV-baseret txt fil.
    """
    
    def __init__(self, file_path: str = "data/addresses.txt"):
        """
        Initialiserer database med den angivne fil sti.
        
        Args:
            file_path: Sti til txt filen hvor adresser gemmes
        """
        self.file_path = Path(file_path)
        self.ensure_data_directory()
        self.ensure_file_exists()
    
    def ensure_data_directory(self):
        """Sikrer at data directory eksisterer."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def ensure_file_exists(self):
        """Sikrer at CSV filen eksisterer med korrekte headers."""
        if not self.file_path.exists():
            self.create_empty_file()
    
    def create_empty_file(self):
        """Opretter en ny tom CSV fil med headers."""
        headers = ["id", "anlaeg_id", "navn", "adresse", "postnr", "by", "created_at", "updated_at"]
        
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
        except Exception as e:
            raise AddressStorageError(f"Kunne ikke oprette address fil: {str(e)}")
    
    def load_addresses(self) -> List[AddressModel]:
        """
        Indlæser alle adresser fra txt filen.
        
        Returns:
            Liste af AddressModel objekter
            
        Raises:
            AddressStorageError: Hvis filen ikke kan læses
        """
        addresses = []
        
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    try:
                        address = AddressModel.from_dict(row)
                        addresses.append(address)
                    except Exception as e:
                        # Log warning but continue processing
                        print(f"Warning: Kunne ikke parse address row: {row}. Error: {str(e)}")
                        
        except FileNotFoundError:
            # Return empty list if file doesn't exist yet
            return []
        except Exception as e:
            raise AddressStorageError(f"Kunne ikke indlæse adresser: {str(e)}")
        
        return addresses
    
    def save_address(self, address: AddressModel) -> None:
        """
        Gemmer en ny adresse til filen.
        
        Args:
            address: AddressModel objekt der skal gemmes
            
        Raises:
            AddressStorageError: Hvis adressen ikke kan gemmes
        """
        # Check if address with same anlaeg_id already exists
        existing_addresses = self.load_addresses()
        if any(addr.anlaeg_id == address.anlaeg_id for addr in existing_addresses):
            raise AddressStorageError(f"Adresse med anlæg ID '{address.anlaeg_id}' eksisterer allerede")
        
        # Set timestamps
        now = datetime.datetime.now().isoformat()
        address.created_at = now
        address.updated_at = now
        
        # Add to existing addresses
        existing_addresses.append(address)
        self._save_all_addresses(existing_addresses)
    
    def update_address(self, address: AddressModel) -> None:
        """
        Opdaterer en eksisterende adresse.
        
        Args:
            address: AddressModel objekt med opdaterede data
            
        Raises:
            AddressStorageError: Hvis adressen ikke kan opdateres
        """
        addresses = self.load_addresses()
        updated = False
        
        for i, existing_address in enumerate(addresses):
            if existing_address.id == address.id:
                # Update timestamp
                address.updated_at = datetime.datetime.now().isoformat()
                # Keep original created_at if it exists
                if existing_address.created_at:
                    address.created_at = existing_address.created_at
                
                addresses[i] = address
                updated = True
                break
        
        if not updated:
            raise AddressStorageError(f"Adresse med ID '{address.id}' ikke fundet")
        
        self._save_all_addresses(addresses)
    
    def delete_address(self, anlaeg_id: str) -> None:
        """
        Sletter en adresse baseret på anlæg ID.
        
        Args:
            anlaeg_id: Modtager anlæg ID der skal slettes
            
        Raises:
            AddressStorageError: Hvis adressen ikke kan slettes
        """
        addresses = self.load_addresses()
        original_count = len(addresses)
        
        # Filter out the address to delete
        addresses = [addr for addr in addresses if addr.anlaeg_id != anlaeg_id]
        
        if len(addresses) == original_count:
            raise AddressStorageError(f"Adresse med anlæg ID '{anlaeg_id}' ikke fundet")
        
        self._save_all_addresses(addresses)
    
    def get_address(self, anlaeg_id: str) -> Optional[AddressModel]:
        """
        Henter en specifik adresse baseret på anlæg ID.
        
        Args:
            anlaeg_id: Modtager anlæg ID at søge efter
            
        Returns:
            AddressModel hvis fundet, None hvis ikke fundet
        """
        addresses = self.load_addresses()
        
        for address in addresses:
            if address.anlaeg_id == anlaeg_id:
                return address
        
        return None
    
    def search_addresses(self, search_term: str) -> List[AddressModel]:
        """
        Søger efter adresser baseret på søgeterm.
        
        Args:
            search_term: Tekst at søge efter i navn, adresse eller by
            
        Returns:
            Liste af matchende AddressModel objekter
        """
        if not search_term.strip():
            return self.load_addresses()
        
        addresses = self.load_addresses()
        search_lower = search_term.lower().strip()
        
        matching_addresses = []
        for address in addresses:
            if (search_lower in address.navn.lower() or
                search_lower in address.adresse.lower() or
                search_lower in address.by.lower() or
                search_lower in address.anlaeg_id.lower()):
                matching_addresses.append(address)
        
        return matching_addresses
    
    def get_all_anlaeg_ids(self) -> List[str]:
        """
        Returnerer alle anlæg IDs i databasen.
        
        Returns:
            Liste af anlæg ID strings
        """
        addresses = self.load_addresses()
        return [addr.anlaeg_id for addr in addresses]
    
    def _save_all_addresses(self, addresses: List[AddressModel]) -> None:
        """
        Gemmer alle adresser til filen (internal method).
        
        Args:
            addresses: Liste af AddressModel objekter at gemme
            
        Raises:
            AddressStorageError: Hvis adresserne ikke kan gemmes
        """
        headers = ["id", "anlaeg_id", "navn", "adresse", "postnr", "by", "created_at", "updated_at"]
        
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                
                for address in addresses:
                    writer.writerow(address.to_dict())
                    
        except Exception as e:
            raise AddressStorageError(f"Kunne ikke gemme adresser: {str(e)}")
    
    def backup_database(self) -> str:
        """
        Opretter en backup af den aktuelle database.
        
        Returns:
            Sti til backup filen
            
        Raises:
            AddressStorageError: Hvis backup ikke kan oprettes
        """
        if not self.file_path.exists():
            raise AddressStorageError("Database fil eksisterer ikke")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.file_path.parent / f"addresses_backup_{timestamp}.txt"
        
        try:
            import shutil
            shutil.copy2(self.file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            raise AddressStorageError(f"Kunne ikke oprette backup: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returnerer statistik om address databasen.
        
        Returns:
            Dictionary med statistik information
        """
        addresses = self.load_addresses()
        
        return {
            "total_addresses": len(addresses),
            "file_path": str(self.file_path),
            "file_exists": self.file_path.exists(),
            "file_size_bytes": self.file_path.stat().st_size if self.file_path.exists() else 0,
            "unique_cities": len(set(addr.by for addr in addresses if addr.by.strip())),
            "unique_postal_codes": len(set(addr.postnr for addr in addresses if addr.postnr.strip())),
        }