"""
RuteBeregner - Hovedapplikation
"""
import reflex as rx
from typing import Any, Dict, List, Optional, Literal
import io   
import base64
import logging
from models.route import RouteRow
from utils.validators import ValidationResult

# Setup logger
logger = logging.getLogger(__name__)

# Robust import af mapping (bagudkompatibelt med din kode)
try:
    from components.address_mapping import company_address_mapping  # type: ignore
except Exception:
    company_address_mapping: Dict[str, Dict[str, str]] = {}


# Applikationsstate
class State(rx.State):
    """State til RuteBeregner applikationen."""

    # Fil upload
    uploaded_file: str = ""

    # Rute data (liste af RouteRow objekter - konverteret til dict for Reflex)
    route_data: List[Dict[str, Any]] = []
    
    # Beregningsresultater (kan beholdes til evt. andre formål)
    distance_results: Dict[str, Any] = {}
    
    # Manuel input felter
    current_start_address: str = ""
    current_end_address: str = ""
    
    # CO₂ beregningsfelter
    current_fuel_type: str = "ikke_valgt"
    current_load_mass_kg: float = 0.0
    current_vehicle_class: str = "ikke_valgt"
    
    # Tab navigation
    current_tab: str = "manual"
    
    # Progress tracking for bulk operations
    calculation_progress: Dict[str, Any] = {}
    
    # Toast notification system
    toast_message: str = ""
    toast_type: str = "info"  # success, error, info, warning
    show_toast: bool = False
    
    # Table filtering and pagination
    table_filters: Dict[str, Any] = {}
    current_page: int = 1
    rows_per_page: int = 100
    selected_routes: List[str] = []  # string UUIDs of selected routes
    search_text: str = ""
    
    # CO₂ calculation and scenario comparison
    scenario_comparison: Dict[str, Any] = {}
    
    # Address management
    addresses: List[Dict[str, Any]] = []
    filtered_addresses: List[Dict[str, Any]] = []
    current_address_anlaeg_id: str = ""
    current_address_navn: str = ""
    current_address_adresse: str = ""
    current_address_postnr: str = ""
    current_address_by: str = ""
    is_editing_address: bool = False
    editing_address_id: str = ""
    address_search_text: str = ""
    use_address_dropdown: bool = False
    
    # Color mode management
    color_mode: Literal["system", "light", "dark"] = "system"
    system_preference: Literal["light", "dark"] = "light"  # Tracks actual system preference
    
    # Data validation state
    validation_result: Optional[ValidationResult] = None
    validation_errors: List[Dict[str, Any]] = []
    validation_warnings: List[Dict[str, Any]] = []
    validation_in_progress: bool = False
    last_validation_timestamp: str = ""
    
    # Upload progress tracking
    upload_progress: float = 0.0
    upload_status: str = ""  # "idle", "uploading", "parsing", "validating", "complete", "error"
    upload_in_progress: bool = False
    current_file_name: str = ""
    file_size: int = 0
    bytes_processed: int = 0
    
    # Selected route for operations
    selected_route_index: int = -1
    selected_route_id: str = ""

    def show_toast_notification(self, message: str, toast_type: str = "info"):
        """Viser en toast notifikation til brugeren."""
        self.toast_message = message
        self.toast_type = toast_type
        self.show_toast = True
    
    def hide_toast_notification(self):
        """Skjuler toast notifikationen."""
        self.show_toast = False
        self.toast_message = ""
        self.toast_type = "info"
    
    def perform_data_validation(self, data: List[Dict[str, Any]]) -> bool:
        """
        Performs comprehensive validation on uploaded data using the DataValidator.
        
        Args:
            data: List of dictionaries from uploaded file
            
        Returns:
            True if validation passed, False otherwise
        """
        self.validation_in_progress = True
        
        try:
            from utils.validators import validate_uploaded_data
            
            # Perform validation
            result = validate_uploaded_data(data)
            
            # Store validation result
            self.validation_result = result
            self.last_validation_timestamp = result.validation_timestamp.isoformat()
            
            # Convert errors and warnings to serializable format for Reflex
            self.validation_errors = []
            self.validation_warnings = []
            
            for error in result.errors:
                self.validation_errors.append({
                    "field": error.field,
                    "message": error.message,
                    "row_number": error.row_number,
                    "value": str(error.value) if error.value is not None else None,
                    "severity": error.severity
                })
            
            for warning in result.warnings:
                self.validation_warnings.append({
                    "field": warning.field,
                    "message": warning.message,
                    "row_number": warning.row_number,
                    "value": str(warning.value) if warning.value is not None else None,
                    "severity": warning.severity,
                    "suggestion": warning.suggestion
                })
            
            # Show validation summary in toast
            if result.is_valid:
                msg = f"✓ Validering gennemført: {result.row_count} rækker, {len(result.warnings)} advarsler"
                self.show_toast_notification(msg, "success")
            else:
                error_count = len(result.errors)
                warning_count = len(result.warnings)
                msg = f"✗ Validering fejlede: {error_count} fejl, {warning_count} advarsler"
                self.show_toast_notification(msg, "error")
                
            return result.is_valid
            
        except Exception as e:
            self.show_toast_notification(f"Fejl under validering: {str(e)}", "error")
            return False
        finally:
            self.validation_in_progress = False
    
    def clear_validation_state(self):
        """Clears all validation-related state."""
        self.validation_result = None
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_in_progress = False
        self.last_validation_timestamp = ""
        
    def clear_upload_progress(self):
        """Clears upload progress state."""
        self.upload_progress = 0.0
        self.upload_status = ""
        self.upload_in_progress = False
        self.current_file_name = ""
        self.file_size = 0
        self.bytes_processed = 0

    def start_upload_progress(self, filename: str, file_size: int):
        """Starts upload progress tracking."""
        self.upload_in_progress = True
        self.upload_status = "uploading"
        self.current_file_name = filename
        self.file_size = file_size
        self.bytes_processed = 0
        self.upload_progress = 0.0
        
    def update_upload_progress(self, bytes_processed: int, status: str = ""):
        """Updates upload progress."""
        self.bytes_processed = bytes_processed
        if self.file_size > 0:
            self.upload_progress = min(100.0, (bytes_processed / self.file_size) * 100.0)
        if status:
            self.upload_status = status
            
    def finish_upload_progress(self, success: bool = True):
        """Finishes upload progress."""
        self.upload_progress = 100.0
        self.upload_status = "complete" if success else "error"
        self.upload_in_progress = False
    
    def revalidate_current_data(self):
        """Re-runs validation on the current route data if available."""
        if not self.route_data:
            self.show_toast_notification("Ingen data at validere", "warning")
            return
        
        # Extract raw data from route data
        raw_data = [route.get("raw_data", {}) for route in self.route_data]
        
        # Perform validation
        self.perform_data_validation(raw_data)

    def handle_file_upload(self, files: list[rx.UploadFile]):
        """Enhanced file upload handler with progress tracking and validation."""
        if not files:
            self.show_toast_notification("Ingen fil valgt", "error")
            return

        # Tag første fil
        f0 = files[0]

        # Ekstrahér navn (hvis muligt)
        name = getattr(f0, "filename", "uploaded_file")
        data: bytes | None = None
        file_size = 0

        try:
            # Get file size if possible
            if hasattr(f0, "size"):
                file_size = f0.size
            
            # Start upload progress tracking
            self.start_upload_progress(name, file_size)
            
            # Extract file data - rx.UploadFile has content property for sync access
            if hasattr(f0, "content"):
                data = f0.content
                self.update_upload_progress(len(data) if data else 0, "parsing")
            else:
                # Fallback - try to get data from file attribute
                try:
                    if hasattr(f0, "file"):
                        data = f0.file.read()
                        self.update_upload_progress(len(data) if data else 0, "parsing")
                except Exception as e:
                    self.finish_upload_progress(False)
                    self.show_toast_notification(f"Fejl ved læsning af fil: {str(e)}", "error")
                    return

            if data is None:
                self.finish_upload_progress(False)
                self.show_toast_notification("Kunne ikke læse filens indhold fra upload", "error")
                return

            # Update progress for parsing stage
            self.uploaded_file = str(name)
            self.update_upload_progress(len(data), "parsing")

            # Import required parsers
            try:
                from utils.parsers import parse_file_to_routes, parse_file
            except Exception:
                self.finish_upload_progress(False)
                self.show_toast_notification("Parser-modul mangler (utils.parsers)", "error")
                return

            # Parse to raw data first
            try:
                raw_data = parse_file(data)
                self.update_upload_progress(len(data), "validating")
                
                # Perform comprehensive validation
                validation_passed = self.perform_data_validation(raw_data)
                
                if not validation_passed and self.validation_result and len(self.validation_result.errors) > 0:
                    # If validation failed with errors, don't proceed
                    self.finish_upload_progress(False)
                    self.show_toast_notification("Upload stoppet på grund af valideringsfejl. Ret fejlene og prøv igen.", "error")
                    return
                
                # Parse to RouteRow objects (validation passed or only warnings)
                route_rows = parse_file_to_routes(data)
                self.route_data = [route.to_dict() for route in route_rows]
                
                # Finish with success
                self.finish_upload_progress(True)
                
                # Show success message with validation info
                if self.validation_result and len(self.validation_result.warnings) > 0:
                    self.show_toast_notification(
                        f"Upload og validering gennemført!\n\n{self.uploaded_file}\n\n100%\n\n{len(route_rows)} ruter med {len(self.validation_result.warnings)} advarsler", 
                        "warning"
                    )
                else:
                    self.show_toast_notification(f"Upload og validering gennemført!\n\n{self.uploaded_file}\n\n100%\n\n{len(route_rows)} ruter indlæst", "success")
                
            except Exception as parse_error:
                # First parse attempt failed, try fallback with file-like object
                try:
                    bio = io.BytesIO(data)
                    try:
                        setattr(bio, "name", self.uploaded_file)
                    except Exception:
                        pass
                    
                    self.update_upload_progress(len(data), "parsing")
                    
                    # Parse raw data for validation
                    raw_data = parse_file(bio)
                    self.update_upload_progress(len(data), "validating")
                    
                    validation_passed = self.perform_data_validation(raw_data)
                    
                    if not validation_passed and self.validation_result and len(self.validation_result.errors) > 0:
                        self.finish_upload_progress(False)
                        self.show_toast_notification("Upload stoppet på grund af valideringsfejl. Ret fejlene og prøv igen.", "error")
                        return
                    
                    route_rows = parse_file_to_routes(bio)
                    self.route_data = [route.to_dict() for route in route_rows]
                    
                    # Finish with success
                    self.finish_upload_progress(True)
                    
                    if self.validation_result and len(self.validation_result.warnings) > 0:
                        self.show_toast_notification(
                            f"{len(route_rows)} ruter indlæst med {len(self.validation_result.warnings)} advarsler", 
                            "warning"
                        )
                    else:
                        self.show_toast_notification(f"Upload og validering gennemført!\n\n{self.uploaded_file}\n\n100%\n\n{len(route_rows)} ruter indlæst", "success")
                        
                except Exception as fallback_error:
                    self.finish_upload_progress(False)
                    self.show_toast_notification(f"Fejl ved parsing af fil: {str(fallback_error)}", "error")
                    return
                    
        except Exception as upload_error:
            # Outer exception handler for file reading issues
            self.finish_upload_progress(False)
            self.show_toast_notification(f"Fejl ved fil upload: {str(upload_error)}", "error")
            return


    def set_and_calculate_route(self, route_id: str):
        """Sætter selected route ID og beregner afstanden."""
        self.selected_route_id = route_id
        self.calculate_single_distance(route_id)

    def calculate_single_distance_by_index(self, index: int):
        """Beregner afstand for en enkelt rute baseret på index."""
        if index < 0 or index >= self.route_data_length:
            self.show_toast_notification("Ugyldig rute index", "error")
            return
            
        route = self.route_data[index]
        
        try:
            from utils.geocoding import calculate_distance, geocode_address  # type: ignore
        except ImportError:
            route["error_status"] = "Geocoder-modul mangler"
            self.show_toast_notification("Geocoder-modul mangler (utils.geocoding)", "error")
            return

        # Hent start og slut adresser/koordinater
        start_address = route.get("start_address", "").strip()
        end_address = route.get("end_address", "").strip()
        start_coords = route.get("start_coordinates")
        end_coords = route.get("end_coordinates")

        if not start_address and not start_coords:
            route["error_status"] = "Manglende startadresse"
            self.show_toast_notification("Manglende startadresse for rute", "error")
            return
            
        if not end_address and not end_coords:
            route["error_status"] = "Manglende slutadresse"
            self.show_toast_notification("Manglende slutadresse for rute", "error")
            return

        try:
            # Geocode adresser hvis koordinater ikke allerede er til stede
            if not start_coords and start_address:
                start_result = geocode_address(start_address)
                if start_result and 'lat' in start_result and 'lng' in start_result:
                    start_coords = (start_result['lat'], start_result['lng'])
                    route["start_coordinates"] = start_coords
                else:
                    route["error_status"] = f"Kunne ikke geocode startadresse: {start_address}"
                    self.show_toast_notification(f"Kunne ikke finde startadresse: {start_address}", "error")
                    return

            if not end_coords and end_address:
                end_result = geocode_address(end_address)
                if end_result and 'lat' in end_result and 'lng' in end_result:
                    end_coords = (end_result['lat'], end_result['lng'])
                    route["end_coordinates"] = end_coords
                else:
                    route["error_status"] = f"Kunne ikke geocode slutadresse: {end_address}"
                    self.show_toast_notification(f"Kunne ikke finde slutadresse: {end_address}", "error")
                    return

            # Beregn afstand
            if start_coords and end_coords:
                distance_km = calculate_distance(start_coords, end_coords)
                route["distance_km"] = round(distance_km, 2)
                route["distance_label"] = f"{distance_km:.1f} km"
                route["error_status"] = None  # Ryd fejlstatus
                
                self.show_toast_notification(f"Afstand beregnet: {distance_km:.1f} km", "success")
            else:
                route["error_status"] = "Manglende koordinater"
                self.show_toast_notification("Kunne ikke beregne afstand - manglende koordinater", "error")

        except Exception as e:
            error_msg = f"Fejl ved afstandsberegning: {str(e)}"
            route["error_status"] = error_msg
            self.show_toast_notification(error_msg, "error")

    def calculate_single_distance(self, route_id: str):
        """Beregner afstand for en enkelt rute og opdaterer label med forbedret fejlhåndtering."""
        if not any(route["id"] == route_id for route in self.route_data):
            self.show_toast_notification("Ugyldig rute ID", "error")
            return
            
        route = next((route for route in self.route_data if route["id"] == route_id), None)
        
        try:
            from utils.geocoding import calculate_distance, geocode_address  # type: ignore
        except ImportError:
            route["error_status"] = "Geocoder-modul mangler"
            self.show_toast_notification("Geocoder-modul mangler (utils.geocoding)", "error")
            return

        # Hent start og slut adresser/koordinater
        start_address = route.get("start_address", "").strip()
        end_address = route.get("end_address", "").strip()
        start_coords = route.get("start_coordinates")
        end_coords = route.get("end_coordinates")

        if not start_address and not start_coords:
            route["error_status"] = "Manglende startadresse"
            self.show_toast_notification("Manglende startadresse for rute", "error")
            return
            
        if not end_address and not end_coords:
            route["error_status"] = "Manglende slutadresse"
            self.show_toast_notification("Manglende slutadresse for rute", "error")
            return

        try:
            # Geocode adresser hvis koordinater mangler
            start_input = start_coords if start_coords else start_address
            end_input = end_coords if end_coords else end_address
            
            # Hvis vi ikke har koordinater, prøv at geocode adresserne først
            if not start_coords and start_address:
                try:
                    start_coords = geocode_address(start_address)
                    if start_coords:
                        route["start_coordinates"] = start_coords
                except Exception as e:
                    route["error_status"] = f"Kunne ikke geocode startadresse: {str(e)}"
                    self.show_toast_notification(f"Kunne ikke geocode startadresse: {start_address}", "error")
                    return
                    
            if not end_coords and end_address:
                try:
                    end_coords = geocode_address(end_address)
                    if end_coords:
                        route["end_coordinates"] = end_coords
                except Exception as e:
                    route["error_status"] = f"Kunne ikke geocode slutadresse: {str(e)}"
                    self.show_toast_notification(f"Kunne ikke geocode slutadresse: {end_address}", "error")
                    return

            # Beregn afstand
            distance = calculate_distance(start_input, end_input)
            
            if distance is not None and distance > 0:
                # Opdater rute data
                self.distance_results[route_id] = distance
                route["distance_km"] = distance
                route["distance_label"] = f"{distance:.2f} km"
                route.pop("error_status", None)  # Fjern eventuelle tidligere fejl
                
                self.show_toast_notification(f"Afstand beregnet: {distance:.2f} km", "success")
            else:
                route["error_status"] = "Ugyldig afstand beregnet"
                self.show_toast_notification("Kunne ikke beregne gyldig afstand", "error")
                
        except Exception as e:
            route["error_status"] = f"Fejl ved afstandsberegning: {str(e)}"
            self.show_toast_notification(f"Fejl ved beregning af afstand: {str(e)}", "error")

    def calculate_all_distances(self):
        """Beregner afstande for alle ruter med progress tracking og forbedret fejlhåndtering."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at beregne", "warning")
            return
            
        try:
            from utils.geocoding import calculate_distance, geocode_address  # type: ignore
        except ImportError:
            self.show_toast_notification("Geocoder-modul mangler (utils.geocoding)", "error")
            return

        total_routes = self.route_data_length
        successful_calculations = 0
        failed_calculations = 0
        
        # Initialiser progress tracking
        self.calculation_progress = {
            "current": 0,
            "total": total_routes,
            "successful": 0,
            "failed": 0,
            "in_progress": True
        }
        
        # Tving UI opdatering for at vise loading state
        yield

        results: Dict[str, float] = {}
        
        for route in self.route_data:
            # Opdater progress
            self.calculation_progress["current"] += 1
            
            try:
                # Hent adresser og koordinater
                start_address = route.get("start_address", "").strip()
                end_address = route.get("end_address", "").strip()
                start_coords = route.get("start_coordinates")
                end_coords = route.get("end_coordinates")

                # Valider at vi har nødvendige data
                if not start_address and not start_coords:
                    route["error_status"] = "Manglende startadresse"
                    route["distance_label"] = "Fejl"
                    failed_calculations += 1
                    continue
                    
                if not end_address and not end_coords:
                    route["error_status"] = "Manglende slutadresse"
                    route["distance_label"] = "Fejl"
                    failed_calculations += 1
                    continue

                # Geocode adresser hvis nødvendigt
                start_input = start_coords if start_coords else start_address
                end_input = end_coords if end_coords else end_address
                
                # Geocode startadresse hvis nødvendigt
                if not start_coords and start_address:
                    try:
                        geocoded_start = geocode_address(start_address)
                        if geocoded_start:
                            route["start_coordinates"] = geocoded_start
                            start_input = geocoded_start
                    except Exception:
                        # Fortsæt med adresse som string hvis geocoding fejler
                        pass
                        
                # Geocode slutadresse hvis nødvendigt
                if not end_coords and end_address:
                    try:
                        geocoded_end = geocode_address(end_address)
                        if geocoded_end:
                            route["end_coordinates"] = geocoded_end
                            end_input = geocoded_end
                    except Exception:
                        # Fortsæt med adresse som string hvis geocoding fejler
                        pass

                # Beregn afstand
                distance = calculate_distance(start_input, end_input)
                
                if distance is not None and distance > 0:
                    results[route["id"]] = distance
                    route["distance_km"] = distance
                    route["distance_label"] = f"{distance:.2f} km"
                    route.pop("error_status", None)  # Fjern eventuelle tidligere fejl
                    successful_calculations += 1
                else:
                    route["error_status"] = "Kunne ikke beregne afstand"
                    route["distance_label"] = "Fejl"
                    failed_calculations += 1
                    
            except Exception as e:
                route["error_status"] = f"Fejl: {str(e)}"
                route["distance_label"] = "Fejl"
                failed_calculations += 1
        
        # Afslut progress tracking
        self.calculation_progress.update({
            "successful": successful_calculations,
            "failed": failed_calculations,
            "in_progress": False
        })
        
        # Opdater distance_results
        self.distance_results = results

        # Vis resultat toast
        if successful_calculations > 0 and failed_calculations == 0:
            self.show_toast_notification(f"Alle {successful_calculations} afstande beregnet succesfuldt", "success")
        elif successful_calculations > 0 and failed_calculations > 0:
            self.show_toast_notification(f"{successful_calculations} afstande beregnet, {failed_calculations} fejlede", "warning")
        else:
            self.show_toast_notification(f"Ingen afstande kunne beregnes ({failed_calculations} fejl)", "error")

    def add_manual_route(self):
        """Tilføjer en ny rute til listen baseret på bruger input."""
        # Valider at begge adresser er angivet
        start = self.current_start_address.strip()
        end = self.current_end_address.strip()
        
        if not start or not end:
            self.show_toast_notification("Både start- og slutadresse skal angives", "error")
            return
        
        # CO₂ valg er nu valgfrie - ingen validering nødvendig
        
        # Opret ny RouteRow med start/slut adresser og CO₂ data fra input felter
        new_route = RouteRow(
            start_address=start,
            end_address=end,
            fuel_type=self.current_fuel_type,
            load_mass_kg=self.current_load_mass_kg,
            vehicle_class=self.current_vehicle_class
        )
        
        # Tilføj til route_data som dict
        self.route_data.append(new_route.to_dict())
        
        # Ryd input felter
        self.current_start_address = ""
        self.current_end_address = ""
        
        self.show_toast_notification(f"Rute tilføjet: {start} → {end}", "success")

    def clear_inputs(self):
        """Rydder alle bruger input felter."""
        self.current_start_address = ""
        self.current_end_address = ""
        self.current_fuel_type = "ikke_valgt"
        self.current_load_mass_kg = 0.0
        self.current_vehicle_class = "ikke_valgt"

    def delete_route(self, route_id: str):
        """Sletter en specifik rute baseret på ID."""
        self.route_data = [route for route in self.route_data if route["id"] != route_id]
        if route_id in self.selected_routes:
            self.selected_routes.remove(route_id)
        self.show_toast_notification("Rute slettet", "info")
    
    def delete_all_routes(self):
        """Sletter alle ruter."""
        count = self.route_data_length
        self.route_data.clear()
        self.selected_routes.clear()
        self.uploaded_file = ""
        self.show_toast_notification(f"{count} ruter slettet", "info")
    
    def export_results(self):
        """Eksporterer resultater - viser CSV eksport som standard."""
        # Use CSV export as default for the upload panel
        self.export_to_csv()
    
    def generate_pdf(self):
        """Genererer tekstrapport (PDF ikke tilgængelig på Windows)."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at generere rapport for", "warning")
            logger.warning("Rapport generation forsøgt uden rutedata")
            return
            
        logger.info(f"Genererer tekstrapport for {len(self.route_data)} ruter")
        
        # Generer tekstrapport direkte (PDF ikke støttet på dette system)
        self._generate_text_report_fallback()

    
    def _generate_text_report_fallback(self):
        """Genererer tekstrapport som fallback når PDF fejler."""
        try:
            from utils.export_utils import generate_export_filename  # type: ignore
            import os
            from datetime import datetime
            
            # Generate simple text report without importing pdf_generator
            text_report = self._create_simple_text_report()
            filename = generate_export_filename('txt')
            
            # Save file locally
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            file_path = os.path.join(downloads_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_report)
            
            success_msg = f"Rapport gemt: {file_path}"
            self.show_toast_notification(success_msg, "success")
            logger.info(f"Tekstrapport gemt til: {file_path}")
            
            # Also try to open the downloads folder
            try:
                os.startfile(downloads_dir)
            except:
                pass  # Ignore if can't open folder
                
            return rx.fragment()
            
        except Exception as e:
            error_msg = f"Rapport generation fejlede helt: {str(e)}"
            self.show_toast_notification(error_msg, "error")
            logger.error(f"Fallback rapport fejl: {error_msg}")
            import traceback
            logger.error(f"Fallback rapport stacktrace: {traceback.format_exc()}")
    
    def _create_simple_text_report(self) -> str:
        """Opretter en simpel tekstrapport uden eksterne dependencies."""
        from datetime import datetime
        
        report_lines = [
            "=" * 60,
            "TEKNIK OG MILJØ - RUTERAPPORT", 
            "=" * 60,
            f"Genereret: {datetime.now().strftime('%d. %B %Y')}",
            "",
            "NØGLETAL:",
            f"  Antal ruter: {len(self.route_data)}",
            "",
        ]
        
        # Calculate basic stats (handle None values safely)
        total_distance = sum(route.get('distance_km', 0) or 0 for route in self.route_data)
        calculated_routes = len([r for r in self.route_data if (r.get('distance_km', 0) or 0) > 0])
        total_co2 = sum(route.get('co2_kg', 0) or 0 for route in self.route_data)
        
        report_lines.extend([
            f"  Samlet afstand: {total_distance:.2f} km",
            f"  Beregnede ruter: {calculated_routes}",
            f"  Total CO₂ udslip: {total_co2:.2f} kg",
            "",
            "DETALJERET RUTELISTE:",
            "-" * 60,
        ])
        
        for i, route in enumerate(self.route_data, 1):
            status = "Fejl" if route.get('error_status') else "OK" if (route.get('distance_km', 0) or 0) > 0 else "Venter"
            distance_val = route.get('distance_km', 0) or 0
            co2_val = route.get('co2_kg', 0) or 0
            distance = f"{distance_val:.2f} km" if distance_val > 0 else "-"
            co2 = f"{co2_val:.2f} kg" if co2_val > 0 else "-"
            
            report_lines.extend([
                f"{i:3d}. {route.get('company_name', '-')}",
                f"     Fra: {route.get('start_address', '-')}",
                f"     Til: {route.get('end_address', '-')}",
                f"     Afstand: {distance}, CO₂: {co2}, Status: {status}",
                "",
            ])
        
        return "\n".join(report_lines)

    def update_address(self, route_id: str, field: str, value: str):
        """Opdaterer en adresse eller koordinat værdi."""
        for route in self.route_data:
            if route["id"] == route_id:
                route[field] = value

    def set_current_tab(self, tab_name: str):
        """Skifter til den specificerede tab."""
        # Validér tab navn
        valid_tabs = ["manual", "routes", "upload", "addresses"]
        if tab_name in valid_tabs:
            self.current_tab = tab_name
            
            # Auto-load addresses when switching to addresses tab
            if tab_name == "addresses":
                self.load_addresses()
                # Populate with hardcoded addresses if empty
                if self.addresses_length == 0:
                    self.populate_addresses_from_hardcoded()
        else:
            # Fallback til default tab
            self.current_tab = "manual"
    
    def set_current_start_address(self, address: str):
        """Opdaterer start adresse input."""
        self.current_start_address = address
    
    def set_current_end_address(self, address: str):
        """Opdaterer slut adresse input."""
        self.current_end_address = address
    
    def set_current_fuel_type(self, fuel_type: str):
        """Opdaterer brændstof type."""
        self.current_fuel_type = fuel_type
    
    def set_current_load_mass_kg(self, mass: str):
        """Opdaterer last masse i kg."""
        try:
            self.current_load_mass_kg = float(mass) if mass else 0.0
        except ValueError:
            self.current_load_mass_kg = 0.0
    
    def set_current_vehicle_class(self, vehicle_class: str):
        """Opdaterer køretøjsklasse."""
        self.current_vehicle_class = vehicle_class
    
    def filter_routes(self) -> List[Dict[str, Any]]:
        """Filtrerer route_data baseret på aktive filtre og søgning."""
        filtered_routes = self.route_data.copy()
        
        # Tekstsøgning på virksomhedsnavn og postdistrikt
        if self.search_text.strip():
            search_lower = self.search_text.lower().strip()
            filtered_routes = [
                route for route in filtered_routes
                if (search_lower in route.get("company_name", "").lower() or 
                    search_lower in route.get("start_address", "").lower() or
                    search_lower in route.get("end_address", "").lower())
            ]
        
        # Anvend filtre
        for filter_key, filter_value in self.table_filters.items():
            if not filter_value:  # Skip inactive filters
                continue
                
            if filter_key == "missing_start":
                filtered_routes = [
                    route for route in filtered_routes 
                    if not route.get("start_address", "").strip()
                ]
            elif filter_key == "missing_end":
                filtered_routes = [
                    route for route in filtered_routes 
                    if not route.get("end_address", "").strip()
                ]
            elif filter_key == "missing_both":
                filtered_routes = [
                    route for route in filtered_routes 
                    if (not route.get("start_address", "").strip() and 
                        not route.get("end_address", "").strip())
                ]
            elif filter_key == "has_errors":
                filtered_routes = [
                    route for route in filtered_routes 
                    if route.get("error_status", "").strip()
                ]
            elif filter_key == "calculated":
                filtered_routes = [
                    route for route in filtered_routes 
                    if route.get("distance_label", "").strip() and 
                       not route.get("error_status", "").strip()
                ]
        
        return filtered_routes
    
    @rx.var
    def get_total_pages(self) -> int:
        """Beregner det samlede antal sider baseret på filtrerede data."""
        filtered_count = len(self.filter_routes())
        return max(1, (filtered_count + self.rows_per_page - 1) // self.rows_per_page)
    
    @rx.var
    def get_paginated_routes(self) -> List[Dict[str, Any]]:
        """Returnerer den aktuelle sides filtrerede ruter."""
        filtered_routes = self.filter_routes()
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        return filtered_routes[start_idx:end_idx]
    
    def set_table_filter(self, filter_key: str, value: bool):
        """Opdaterer en tabel filter og nulstiller til første side."""
        self.table_filters[filter_key] = value
        self.current_page = 1
        self.selected_routes.clear()  # Clear selections when filters change
    
    def set_search_text(self, text: str):
        """Opdaterer søgetekst og nulstiller til første side."""
        self.search_text = text
        self.current_page = 1
        self.selected_routes.clear()  # Clear selections when search changes
    
    def set_current_page(self, page: int):
        """Skifter til specificeret side."""
        total_pages = self.get_total_pages()
        if 1 <= page <= total_pages:
            self.current_page = page
    
    def toggle_route_selection(self, route_id: str):
        """Toggler selection af en rute."""
        if route_id in self.selected_routes:
            self.selected_routes.remove(route_id)
        else:
            self.selected_routes.append(route_id)
    
    def select_all_filtered_routes(self):
        """Vælger alle ruter på den aktuelle filtrerede liste."""
        filtered_routes = self.filter_routes()
        self.selected_routes = [route["id"] for route in filtered_routes]
    
    def clear_all_selections(self):
        """Rydder alle valgte ruter."""
        self.selected_routes.clear()
    
    def clear_all_routes(self):
        """Rydder alle ruter fra route_data."""
        self.route_data.clear()
        self.selected_routes.clear()
        self.uploaded_file = ""
        self.show_toast_notification("Alle ruter ryddet", "info")
    
    def switch_to_routes_tab(self):
        """Skifter til ruter tab."""
        self.current_tab = "routes"
    
    def switch_to_upload_tab(self):
        """Skifter til upload tab."""
        self.current_tab = "upload"
    
    def reset_upload_state(self):
        """Nulstiller upload state."""
        self.uploaded_file = ""
        self.route_data.clear()
        self.clear_validation_state()
        self.clear_upload_progress()
    
    def clear_uploaded_file(self):
        """Rydder uploaded file."""
        self.uploaded_file = ""
    
    @rx.var
    def calculated_routes_count(self) -> int:
        """Returnerer antal beregnede ruter."""
        return len([r for r in self.route_data if r.get('distance_label', '') != ''])
    
    @rx.var
    def error_routes_count(self) -> int:
        """Returnerer antal ruter med fejl."""
        return len([r for r in self.route_data if r.get('error_status', '') != ''])
    
    def toggle_table_filter(self, filter_name: str):
        """Toggler en table filter."""
        current_value = self.table_filters.get(filter_name, False)
        self.table_filters[filter_name] = not current_value
    
    @rx.var
    def selected_routes_count(self) -> int:
        """Returnerer antal valgte ruter."""
        return self.selected_routes_length
    
    @rx.var
    def filtered_routes_count(self) -> int:
        """Returnerer antal filterede ruter."""
        return len(self.filter_routes())
    
    @rx.var
    def paginated_routes_count(self) -> int:
        """Returnerer antal ruter på current page."""
        return len(self.get_paginated_routes)
    
    @rx.var
    def all_paginated_routes_selected(self) -> bool:
        """Returnerer om alle ruter på current page er valgt."""
        paginated = self.get_paginated_routes
        return self.selected_routes_length == len(paginated) and len(paginated) > 0
    
    @rx.var
    def all_filtered_routes_selected(self) -> bool:
        """Returnerer om alle filterede ruter er valgt."""
        filtered = self.filter_routes()
        return self.selected_routes_length == len(filtered)
    
    def delete_selected_routes(self):
        """Sletter valgte ruter fra route_data."""
        if not self.selected_routes:
            self.show_toast_notification("Ingen ruter valgt til sletning", "warning")
            return
        
        # Sort in reverse order to delete from end to avoid index shifting
        selected_routes = sorted(self.selected_routes, reverse=True)
        count = 0
        
        for route_id in selected_routes:
            if any(route["id"] == route_id for route in self.route_data):
                self.route_data = [route for route in self.route_data if route["id"] != route_id]
                count += 1
        
        self.selected_routes.clear()
        self.show_toast_notification(f"{count} ruter slettet", "info")
    
    def calculate_selected_routes(self):
        """Beregner afstande for valgte ruter."""
        if not self.selected_routes:
            self.show_toast_notification("Ingen ruter valgt til beregning", "warning")
            return
        
        successful = 0
        failed = 0
        
        for route_id in self.selected_routes:
            if any(route["id"] == route_id for route in self.route_data):
                try:
                    # Use existing single distance calculation logic
                    old_error_status = next(route for route in self.route_data if route["id"] == route_id).get("error_status", "")
                    self.calculate_single_distance(route_id)
                    # Check if calculation was successful (no new error status)
                    if not next(route for route in self.route_data if route["id"] == route_id).get("error_status", ""):
                        successful += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        
        if successful > 0 and failed == 0:
            self.show_toast_notification(f"{successful} ruter beregnet succesfuldt", "success")
        elif successful > 0 and failed > 0:
            self.show_toast_notification(f"{successful} beregnet, {failed} fejlede", "warning")
        else:
            self.show_toast_notification(f"Kunne ikke beregne ruter ({failed} fejl)", "error")
    
    def calculate_co2_for_route(self, route_id: str):
        """Beregner CO₂ udslip for en enkelt rute."""
        if not any(route["id"] == route_id for route in self.route_data):
            self.show_toast_notification("Ugyldig rute ID", "error")
            return
            
        route = next(route for route in self.route_data if route["id"] == route_id)
        
        try:
            from utils.co2_calculator import calculate_co2_for_route  # type: ignore
        except ImportError:
            self.show_toast_notification("CO₂ beregningsmodul mangler", "error")
            return
        
        try:
            co2_emissions, details = calculate_co2_for_route(route)
            
            if 'error' in details:
                route['co2_error'] = details['error']
                self.show_toast_notification(f"CO₂ beregningsfejl: {details['error']}", "error")
            else:
                route['co2_kg'] = co2_emissions
                route['co2_details'] = details
                route.pop('co2_error', None)  # Remove any previous error
                
                self.show_toast_notification(f"CO₂ beregnet: {co2_emissions:.2f} kg CO₂e", "success")
                
        except Exception as e:
            route['co2_error'] = str(e)
            self.show_toast_notification(f"Fejl ved CO₂ beregning: {str(e)}", "error")
    
    def update_all_co2(self):
        """Beregner CO₂ udslip for alle ruter med distance data."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at beregne CO₂ for", "warning")
            return
            
        try:
            from utils.co2_calculator import calculate_co2_for_route  # type: ignore
        except ImportError:
            self.show_toast_notification("CO₂ beregningsmodul mangler", "error")
            return

        successful = 0
        failed = 0
        
        # Initialiser progress tracking
        self.calculation_progress = {
            "current": 0,
            "total": self.route_data_length,
            "successful": 0,
            "failed": 0,
            "in_progress": True,
            "operation": "co2_calculation"
        }
        
        for route in self.route_data:
            # Opdater progress
            self.calculation_progress["current"] += 1
            
            try:
                co2_emissions, details = calculate_co2_for_route(route)
                
                if 'error' in details:
                    route['co2_error'] = details['error']
                    failed += 1
                else:
                    route['co2_kg'] = co2_emissions
                    route['co2_details'] = details
                    route.pop('co2_error', None)
                    successful += 1
                    
            except Exception as e:
                route['co2_error'] = str(e)
                failed += 1
        
        # Afslut progress tracking
        self.calculation_progress.update({
            "successful": successful,
            "failed": failed,
            "in_progress": False
        })
        
        # Vis resultat toast
        if successful > 0 and failed == 0:
            self.show_toast_notification(f"CO₂ beregnet for alle {successful} ruter", "success")
        elif successful > 0 and failed > 0:
            self.show_toast_notification(f"CO₂ beregnet for {successful} ruter, {failed} fejlede", "warning")
        else:
            self.show_toast_notification(f"Kunne ikke beregne CO₂ for ruter ({failed} fejl)", "error")
    
    def calculate_scenario_comparison(self, fuel_type_a: str, fuel_type_b: str):
        """Sammenligner CO₂ udslip mellem to brændstoftyper."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at sammenligne", "warning")
            return {}
            
        try:
            from utils.co2_calculator import calculate_scenario_comparison  # type: ignore
        except ImportError:
            self.show_toast_notification("CO₂ beregningsmodul mangler", "error")
            return {}
        
        try:
            # Only include routes with distance data
            routes_with_distance = [
                route for route in self.route_data 
                if route.get('distance_km', 0) > 0
            ]
            
            if not routes_with_distance:
                self.show_toast_notification("Ingen ruter med afstandsdata til sammenligning", "warning")
                return {}
            
            comparison = calculate_scenario_comparison(routes_with_distance, fuel_type_a, fuel_type_b)
            
            if 'error' in comparison:
                self.show_toast_notification(f"Fejl ved scenarie sammenligning: {comparison['error']}", "error")
            else:
                # Store comparison results for UI display
                self.scenario_comparison = comparison
                
                total_diff = comparison['total_difference']
                percent_change = comparison['percent_change']
                
                if abs(total_diff) < 0.01:
                    message = f"Ingen betydelig forskel mellem {fuel_type_a} og {fuel_type_b}"
                elif total_diff > 0:
                    message = f"{fuel_type_b} udslipper {abs(total_diff):.2f} kg mere CO₂ ({abs(percent_change):.1f}% stigning)"
                else:
                    message = f"{fuel_type_b} udslipper {abs(total_diff):.2f} kg mindre CO₂ ({abs(percent_change):.1f}% reduktion)"
                
                self.show_toast_notification(message, "info")
            
            return comparison
            
        except Exception as e:
            self.show_toast_notification(f"Fejl ved scenarie sammenligning: {str(e)}", "error")
            return {}
    
    def download_pdf_report(self) -> rx.Component:
        """Downloader PDF rapport af ruter."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at generere rapport for", "warning")
            return rx.fragment()
            
        try:
            from utils.pdf_generator import generate_report, PDFGeneratorError  # type: ignore
        except ImportError:
            self.show_toast_notification("PDF generator modul mangler", "error")
            return rx.fragment()
        
        try:
            # Generate PDF
            pdf_bytes = generate_report(
                routes=self.route_data,
                metadata={
                    "generated_by": "RuteBeregner",
                    "total_routes": self.route_data_length,
                    "calculated_routes": len([r for r in self.route_data if r.get('distance_km', 0) > 0])
                }
            )
            
            # Create download response
            from datetime import datetime
            filename = f"ruterapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Convert to base64 for download
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            self.show_toast_notification("PDF rapport genereret", "success")
            
            # Return download component
            return rx.download(
                data=pdf_base64,
                filename=filename
            )
            
        except PDFGeneratorError as e:
            self.show_toast_notification(f"PDF generering fejlede: {str(e)}", "error")
            return rx.fragment()
        except Exception as e:
            self.show_toast_notification(f"Uventet fejl ved PDF generering: {str(e)}", "error")
            return rx.fragment()
    
    def export_to_csv(self):
        """Eksporterer rutedata til CSV format."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at eksportere", "warning")
            logger.warning("CSV eksport forsøgt uden rutedata")
            return
            
        try:
            from utils.export_utils import export_to_csv_bytes, generate_export_filename  # type: ignore
            import base64
        except ImportError as e:
            error_msg = f"Export modul mangler: {str(e)}"
            self.show_toast_notification("Export funktionalitet ikke tilgængelig", "error")
            logger.error(error_msg)
            return
        
        try:
            logger.info(f"Starter CSV eksport for {len(self.route_data)} ruter")
            import os
            
            # Generer CSV data
            csv_bytes = export_to_csv_bytes(self.route_data)
            filename = generate_export_filename('csv')
            
            # Save file locally
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)
            file_path = os.path.join(downloads_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(csv_bytes)
            
            success_msg = f"CSV fil gemt: {file_path}"
            self.show_toast_notification(success_msg, "success")
            logger.info(f"CSV eksport gemt til: {file_path}")
            
            # Try to open the downloads folder
            try:
                os.startfile(downloads_dir)
            except:
                pass  # Ignore if can't open folder
                
            return rx.fragment()
            
        except Exception as e:
            error_msg = f"Fejl ved CSV eksport: {str(e)}"
            self.show_toast_notification(error_msg, "error")
            logger.error(f"CSV eksport fejl: {error_msg}")
            import traceback
            logger.error(f"CSV eksport stacktrace: {traceback.format_exc()}")
    
    def export_to_excel(self):
        """Eksporterer rutedata til Excel format."""
        if not self.route_data:
            self.show_toast_notification("Ingen ruter at eksportere", "warning")
            return
            
        try:
            from utils.export_utils import export_to_excel_bytes, generate_export_filename  # type: ignore
        except ImportError:
            self.show_toast_notification("Export modul mangler", "error")
            return
        
        try:
            # Generer Excel data
            excel_bytes = export_to_excel_bytes(self.route_data)
            filename = generate_export_filename('excel')
            
            # Konverter til base64 for download
            excel_base64 = base64.b64encode(excel_bytes).decode('utf-8')
            
            self.show_toast_notification(f"Excel fil genereret med {self.route_data_length} ruter", "success")
            
            # Trigger download via JavaScript
            yield rx.download(
                data=excel_base64,
                filename=filename
            )
            
        except Exception as e:
            self.show_toast_notification(f"Fejl ved Excel eksport: {str(e)}", "error")
    
    # =====================
    # ADDRESS MANAGEMENT
    # =====================
    
    def load_addresses(self):
        """Indlæser alle adresser fra databasen."""
        try:
            from utils.address_storage import TxtFileDatabase  # type: ignore
            db = TxtFileDatabase()
            address_models = db.load_addresses()
            
            # Konverter til dict format for Reflex State
            self.addresses = [addr.to_dict() for addr in address_models]
            self.filtered_addresses = self.addresses.copy()
            
            # Debug logging
            logger.info(f"Indlæst {len(self.addresses)} adresser")
            for i, addr in enumerate(self.addresses[:3]):  # Log første 3 adresser
                logger.info(f"Adresse {i}: anlaeg_id='{addr.get('anlaeg_id')}', navn='{addr.get('navn')}'")
            
            self.show_toast_notification(f"{self.addresses_length} adresser indlæst", "success")
        except Exception as e:
            logger.error(f"Fejl ved indlæsning af adresser: {str(e)}")
            self.show_toast_notification(f"Fejl ved indlæsning af adresser: {str(e)}", "error")
    
    def add_address_entry(self):
        """Tilføjer en ny adresse til databasen."""
        # Valider input
        if not all([
            self.current_address_anlaeg_id.strip(),
            self.current_address_navn.strip(),
            self.current_address_adresse.strip(),
            self.current_address_postnr.strip(),
            self.current_address_by.strip()
        ]):
            self.show_toast_notification("Alle felter skal udfyldes", "error")
            return
        
        # Valider postnummer
        if not (self.current_address_postnr.isdigit() and len(self.current_address_postnr) == 4):
            self.show_toast_notification("Postnummer skal være 4 cifre", "error")
            return
        
        try:
            from utils.address_storage import TxtFileDatabase, AddressStorageError  # type: ignore
            from models.address import AddressModel  # type: ignore
            
            db = TxtFileDatabase()
            
            # Opret ny adresse model
            new_address = AddressModel(
                anlaeg_id=self.current_address_anlaeg_id.strip(),
                navn=self.current_address_navn.strip(),
                adresse=self.current_address_adresse.strip(),
                postnr=self.current_address_postnr.strip(),
                by=self.current_address_by.strip()
            )
            
            # Gem til database
            db.save_address(new_address)
            
            # Ryd form
            self.clear_address_form()
            
            # Genindlæs adresser
            self.load_addresses()
            
            self.show_toast_notification(f"Adresse tilføjet: {new_address.anlaeg_id}", "success")
            
        except AddressStorageError as e:
            self.show_toast_notification(str(e), "error")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved tilføjelse: {str(e)}", "error")
    
    def start_editing_address(self, anlaeg_id: str):
        """Starter redigering af en adresse."""
        # Find adressen i listen
        address_dict = None
        for addr in self.addresses:
            if addr["anlaeg_id"] == anlaeg_id:
                address_dict = addr
                break
        
        if not address_dict:
            self.show_toast_notification("Adresse ikke fundet", "error")
            return
        
        # Fyld form med eksisterende data
        self.current_address_anlaeg_id = address_dict["anlaeg_id"]
        self.current_address_navn = address_dict["navn"]
        self.current_address_adresse = address_dict["adresse"]
        self.current_address_postnr = address_dict["postnr"]
        self.current_address_by = address_dict["by"]
        self.editing_address_id = address_dict["id"]
        self.is_editing_address = True
    
    def update_address_entry(self):
        """Opdaterer en eksisterende adresse."""
        if not self.is_editing_address:
            return
        
        # Valider input
        if not all([
            self.current_address_anlaeg_id.strip(),
            self.current_address_navn.strip(),
            self.current_address_adresse.strip(),
            self.current_address_postnr.strip(),
            self.current_address_by.strip()
        ]):
            self.show_toast_notification("Alle felter skal udfyldes", "error")
            return
        
        # Valider postnummer
        if not (self.current_address_postnr.isdigit() and len(self.current_address_postnr) == 4):
            self.show_toast_notification("Postnummer skal være 4 cifre", "error")
            return
        
        try:
            from utils.address_storage import TxtFileDatabase, AddressStorageError  # type: ignore
            from models.address import AddressModel  # type: ignore
            
            db = TxtFileDatabase()
            
            # Opret opdateret adresse model
            updated_address = AddressModel(
                id=self.editing_address_id,
                anlaeg_id=self.current_address_anlaeg_id.strip(),
                navn=self.current_address_navn.strip(),
                adresse=self.current_address_adresse.strip(),
                postnr=self.current_address_postnr.strip(),
                by=self.current_address_by.strip()
            )
            
            # Opdater i database
            db.update_address(updated_address)
            
            # Ryd form og exit edit mode
            self.cancel_address_editing()
            
            # Genindlæs adresser
            self.load_addresses()
            
            self.show_toast_notification(f"Adresse opdateret: {updated_address.anlaeg_id}", "success")
            
        except AddressStorageError as e:
            self.show_toast_notification(str(e), "error")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved opdatering: {str(e)}", "error")
    
    def delete_address_entry(self, anlaeg_id: str):
        """Sletter en adresse fra databasen."""
        logger.info(f"Forsøger at slette adresse med anlæg_id: '{anlaeg_id}' (type: {type(anlaeg_id)})")
        
        # Check if anlaeg_id is None or empty
        if not anlaeg_id or anlaeg_id == "None":
            logger.error(f"Ugyldig anlæg_id modtaget: '{anlaeg_id}'")
            self.show_toast_notification("Kan ikke slette adresse - manglende anlæg ID", "error")
            return
            
        try:
            from utils.address_storage import TxtFileDatabase, AddressStorageError  # type: ignore
            
            db = TxtFileDatabase()
            db.delete_address(anlaeg_id)
            
            # Genindlæs adresser
            self.load_addresses()
            
            logger.info(f"Adresse med anlæg_id '{anlaeg_id}' slettet succesfuldt")
            self.show_toast_notification(f"Adresse slettet: {anlaeg_id}", "success")
            
        except AddressStorageError as e:
            logger.error(f"AddressStorageError ved sletning: {str(e)}")
            self.show_toast_notification(str(e), "error")
        except Exception as e:
            logger.error(f"Uventet fejl ved sletning af adresse: {str(e)}")
            self.show_toast_notification(f"Fejl ved sletning: {str(e)}", "error")

    def delete_address_by_index(self, index: int):
        """Sletter en adresse baseret på indeks i filtered_addresses."""
        logger.info(f"Forsøger at slette adresse med indeks: {index}")
        
        try:
            if index < 0 or index >= len(self.filtered_addresses):
                logger.error(f"Ugyldig indeks: {index} (længde: {len(self.filtered_addresses)})")
                self.show_toast_notification("Kan ikke slette adresse - ugyldig indeks", "error")
                return
                
            # Hent adressen fra det filtrerede array
            address_to_delete = self.filtered_addresses[index]
            anlaeg_id = address_to_delete.get('anlaeg_id')
            
            if not anlaeg_id:
                logger.error(f"Ingen anlæg_id fundet for adresse på indeks {index}")
                self.show_toast_notification("Kan ikke slette adresse - manglende anlæg ID", "error")
                return
            
            logger.info(f"Sletter adresse med anlæg_id: '{anlaeg_id}'")
            self.delete_address_entry(anlaeg_id)
            
        except Exception as e:
            logger.error(f"Fejl ved sletning af adresse med indeks {index}: {str(e)}")
            self.show_toast_notification(f"Fejl ved sletning: {str(e)}", "error")

    def start_editing_address_by_index(self, index: int):
        """Starter redigering af en adresse baseret på indeks."""
        logger.info(f"Starter redigering af adresse med indeks: {index}")
        
        try:
            if index < 0 or index >= len(self.filtered_addresses):
                logger.error(f"Ugyldig indeks: {index} (længde: {len(self.filtered_addresses)})")
                self.show_toast_notification("Kan ikke redigere adresse - ugyldig indeks", "error")
                return
                
            # Hent adressen fra det filtrerede array
            address_to_edit = self.filtered_addresses[index]
            anlaeg_id = address_to_edit.get('anlaeg_id')
            
            if not anlaeg_id:
                logger.error(f"Ingen anlæg_id fundet for adresse på indeks {index}")
                self.show_toast_notification("Kan ikke redigere adresse - manglende anlæg ID", "error")
                return
            
            logger.info(f"Redigerer adresse med anlæg_id: '{anlaeg_id}'")
            self.start_editing_address(anlaeg_id)
            
        except Exception as e:
            logger.error(f"Fejl ved start af redigering for indeks {index}: {str(e)}")
            self.show_toast_notification(f"Fejl ved redigering: {str(e)}", "error")
    
    def cancel_address_editing(self):
        """Annullerer address redigering og rydder form."""
        self.clear_address_form()
        self.is_editing_address = False
        self.editing_address_id = ""
    
    def clear_address_form(self):
        """Rydder alle address form felter."""
        self.current_address_anlaeg_id = ""
        self.current_address_navn = ""
        self.current_address_adresse = ""
        self.current_address_postnr = ""
        self.current_address_by = ""
    
    def search_addresses(self):
        """Søger efter adresser baseret på søgetekst."""
        if not self.address_search_text.strip():
            self.filtered_addresses = self.addresses.copy()
            return
        
        search_lower = self.address_search_text.lower().strip()
        self.filtered_addresses = [
            addr for addr in self.addresses
            if (search_lower in addr["anlaeg_id"].lower() or
                search_lower in addr["navn"].lower() or
                search_lower in addr["adresse"].lower() or
                search_lower in addr["by"].lower())
        ]
    
    def clear_address_search(self):
        """Rydder søgning og viser alle adresser."""
        self.address_search_text = ""
        self.filtered_addresses = self.addresses.copy()
    
    def set_address_search_text(self, text: str):
        """Opdaterer søgetekst og filtrerer automatisk."""
        self.address_search_text = text
        self.search_addresses()
    
    def set_current_address_anlaeg_id(self, value: str):
        """Opdaterer anlæg ID input."""
        self.current_address_anlaeg_id = value
    
    def set_current_address_navn(self, value: str):
        """Opdaterer navn input."""
        self.current_address_navn = value
    
    def set_current_address_adresse(self, value: str):
        """Opdaterer adresse input."""
        self.current_address_adresse = value
    
    def set_current_address_postnr(self, value: str):
        """Opdaterer postnr input."""
        self.current_address_postnr = value
    
    def set_current_address_by(self, value: str):
        """Opdaterer by input."""
        self.current_address_by = value
    
    @rx.var
    def unique_cities_count(self) -> int:
        """Returnerer antal unikke byer i address listen."""
        cities = set()
        for addr in self.addresses:
            if addr.get("by", "").strip():
                cities.add(addr["by"].strip())
        return len(cities)
    
    def import_addresses_from_excel(self):
        """Importerer adresser fra Excel filen '2024 data til Oguz.xlsx'."""
        try:
            import pandas as pd
            from utils.address_storage import TxtFileDatabase, AddressStorageError  # type: ignore
            from models.address import AddressModel  # type: ignore
            import os
            
            # Find Excel file
            excel_file_path = "2024 data til Oguz.xlsx"
            if not os.path.exists(excel_file_path):
                self.show_toast_notification("Excel fil '2024 data til Oguz.xlsx' ikke fundet", "error")
                return
            
            self.show_toast_notification("Læser Excel fil...", "info")
            
            # Read Excel file
            df = pd.read_excel(excel_file_path)
            
            # Expected columns: look for relevant address columns
            # Try to identify columns containing address information
            address_columns = []
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['modtager', 'anlæg', 'adresse', 'navn', 'virksomhed']):
                    address_columns.append(col)
            
            if not address_columns:
                self.show_toast_notification("Ingen relevante address kolonner fundet i Excel filen", "error")
                return
            
            self.show_toast_notification(f"Fandt {len(address_columns)} relevante kolonner: {', '.join(address_columns[:3])}...", "info")
            
            db = TxtFileDatabase()
            added_count = 0
            skipped_count = 0
            error_count = 0
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Try to extract address information from the row
                    # Look for specific patterns in the data
                    
                    # Try to find anlæg ID (numeric ID)
                    anlaeg_id = None
                    for col in df.columns:
                        if 'id' in str(col).lower() or 'anlæg' in str(col).lower():
                            value = row[col]
                            if pd.notna(value) and str(value).strip():
                                anlaeg_id = str(value).strip()
                                break
                    
                    # Try to find navn/virksomhed
                    navn = None
                    for col in df.columns:
                        if any(keyword in str(col).lower() for keyword in ['navn', 'virksomhed', 'modtager']):
                            value = row[col]
                            if pd.notna(value) and str(value).strip():
                                navn = str(value).strip()
                                break
                    
                    # Try to find adresse
                    adresse = None
                    for col in df.columns:
                        if 'adresse' in str(col).lower() and 'end' not in str(col).lower():
                            value = row[col]
                            if pd.notna(value) and str(value).strip():
                                adresse = str(value).strip()
                                break
                    
                    # If we don't have basic info, skip this row
                    if not anlaeg_id or not navn or not adresse:
                        skipped_count += 1
                        continue
                    
                    # Try to parse address for postal code and city
                    postnr = "0000"
                    by = "Unknown"
                    
                    # Simple parsing - look for 4 digits followed by text
                    import re
                    address_parts = adresse.split(',')
                    if len(address_parts) >= 2:
                        city_postal_part = address_parts[-1].strip()
                        postal_match = re.search(r'\b(\d{4})\s+(.+)', city_postal_part)
                        if postal_match:
                            postnr = postal_match.group(1)
                            by = postal_match.group(2).strip()
                            adresse = address_parts[0].strip()  # Remove city/postal from address
                    
                    # Create address model
                    new_address = AddressModel(
                        anlaeg_id=anlaeg_id,
                        navn=navn,
                        adresse=adresse,
                        postnr=postnr,
                        by=by
                    )
                    
                    # Try to save
                    try:
                        db.save_address(new_address)
                        added_count += 1
                    except AddressStorageError:
                        # Skip if already exists
                        skipped_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {idx}: {str(e)}")
                    continue
            
            # Show results
            if added_count > 0:
                self.load_addresses()
                self.show_toast_notification(
                    f"Excel import færdig: {added_count} tilføjet, {skipped_count} sprunget over, {error_count} fejl", 
                    "success"
                )
            elif skipped_count > 0:
                self.show_toast_notification(
                    f"Ingen nye adresser importeret: {skipped_count} eksisterede allerede", 
                    "info"
                )
            else:
                self.show_toast_notification("Ingen adresser kunne importeres fra Excel filen", "warning")
                
        except ImportError:
            self.show_toast_notification("pandas er nødvendig for Excel import. Installer med: pip install pandas openpyxl", "error")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved Excel import: {str(e)}", "error")
    
    def export_addresses_to_csv(self) -> rx.Component:
        """Eksporterer adresser til CSV fil."""
        if not self.addresses:
            self.show_toast_notification("Ingen adresser at eksportere", "warning")
            return rx.fragment()
            
        try:
            import csv
            import io
            import base64
            from datetime import datetime
            
            # Create CSV data in memory
            csv_buffer = io.StringIO()
            fieldnames = ["anlaeg_id", "navn", "adresse", "postnr", "by", "created_at", "updated_at"]
            
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write address data
            for address in self.addresses:
                writer.writerow({
                    field: address.get(field, "") for field in fieldnames
                })
            
            # Convert to bytes
            csv_content = csv_buffer.getvalue()
            csv_bytes = csv_content.encode('utf-8')
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adresseliste_{timestamp}.csv"
            
            # Convert to base64 for download
            csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
            
            self.show_toast_notification(f"CSV fil genereret med {self.addresses_length} adresser", "success")
            
            # Return download component
            return rx.download(
                data=csv_base64,
                filename=filename
            )
            
        except Exception as e:
            self.show_toast_notification(f"Fejl ved CSV eksport: {str(e)}", "error")
            return rx.fragment()
    
    def backup_address_database(self):
        """Opretter backup af address databasen."""
        try:
            from utils.address_storage import TxtFileDatabase  # type: ignore
            
            db = TxtFileDatabase()
            backup_path = db.backup_database()
            
            self.show_toast_notification(f"Backup oprettet: {backup_path}", "success")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved backup: {str(e)}", "error")
    
    def populate_addresses_from_hardcoded(self):
        """Populerer address database med eksisterende hardkodede adresser."""
        try:
            from components.address_mapping import receiver_mapping  # type: ignore
            from utils.address_storage import TxtFileDatabase  # type: ignore
            from models.address import AddressModel  # type: ignore
            
            db = TxtFileDatabase()
            added_count = 0
            
            for anlaeg_id, entry in receiver_mapping.items():
                try:
                    # Parse address to separate street and city/postal
                    full_address = entry["address"]
                    # Simple parsing - split by comma
                    parts = full_address.split(", ")
                    if len(parts) >= 2:
                        street = parts[0].strip()
                        city_postal = parts[-1].strip()
                        # Try to extract postal code (4 digits) and city
                        city_postal_parts = city_postal.split(" ", 1)
                        if len(city_postal_parts) >= 2 and city_postal_parts[0].isdigit():
                            postnr = city_postal_parts[0]
                            by = city_postal_parts[1]
                        else:
                            postnr = "0000"  # Default
                            by = city_postal
                    else:
                        street = full_address
                        postnr = "0000"
                        by = "Unknown"
                    
                    new_address = AddressModel(
                        anlaeg_id=str(anlaeg_id),
                        navn=entry["name"],
                        adresse=street,
                        postnr=postnr,
                        by=by
                    )
                    
                    try:
                        db.save_address(new_address)
                        added_count += 1
                    except Exception:
                        # Skip if already exists
                        pass
                        
                except Exception as e:
                    print(f"Could not parse address for {anlaeg_id}: {str(e)}")
                    continue
            
            if added_count > 0:
                self.load_addresses()
                self.show_toast_notification(f"{added_count} adresser importeret fra hardkodede data", "success")
            else:
                self.show_toast_notification("Ingen nye adresser at importere", "info")
                
        except Exception as e:
            self.show_toast_notification(f"Fejl ved import af hardkodede adresser: {str(e)}", "error")
    
    def toggle_address_dropdown(self):
        """Toggler mellem manual indtastning og address dropdown."""
        self.use_address_dropdown = not self.use_address_dropdown
        # Clear current end address when switching modes
        if self.use_address_dropdown:
            self.load_addresses()  # Ensure addresses are loaded
    
    def set_end_address_from_dropdown(self, anlaeg_id: str):
        """Sætter slutadresse baseret på valg fra address dropdown."""
        if not anlaeg_id or anlaeg_id == "":
            self.current_end_address = ""
            return
            
        # Find the address in the loaded addresses
        selected_address = None
        for addr in self.addresses:
            if addr.get("anlaeg_id") == anlaeg_id:
                selected_address = addr
                break
        
        if selected_address:
            # Set the full address as end address
            full_address = f"{selected_address['adresse']}, {selected_address['postnr']} {selected_address['by']}"
            self.current_end_address = full_address
            self.show_toast_notification(f"Slutadresse sat til: {selected_address['navn']}", "info")
        else:
            self.current_end_address = ""
            self.show_toast_notification("Adresse ikke fundet", "error")
    
    @rx.var
    def address_dropdown_labels(self) -> List[str]:
        """Returnerer labels til address dropdown."""
        if not self.addresses:
            return []
        
        labels = []
        for addr in self.addresses:
            label = f"{addr.get('anlaeg_id', '')} - {addr.get('navn', '')} ({addr.get('by', '')})"
            if label.strip() and label != " -  ()":  # Only add non-empty, valid labels
                labels.append(label)
        
        return labels
    
    def handle_address_dropdown_change(self, value: str):
        """Håndterer ændring i address dropdown."""
        if not value or value == "":
            self.current_end_address = ""
            return
        
        # Extract anlaeg_id from the label format "ID - Name (City)"
        try:
            anlaeg_id = value.split(" - ")[0].strip()
            self.set_end_address_from_dropdown(anlaeg_id)
        except Exception:
            self.show_toast_notification("Fejl ved parsing af address valg", "error")
    
    # =====================
    # COLOR MODE MANAGEMENT
    # =====================
    
    def set_color_mode(self, mode: str | list[str]):
        """Sætter color mode og gemmer preference i localStorage."""
        # Handle both single string and list input from segmented control
        selected_mode = mode if isinstance(mode, str) else (mode[0] if mode else "system")
        
        if selected_mode in ["system", "light", "dark"]:
            self.color_mode = selected_mode
            # Trigger color mode change with custom event
            return rx.call_script(f"""
                window.dispatchEvent(new CustomEvent('colorModeChange', {{ 
                    detail: '{selected_mode}' 
                }}));
            """)
    
    def detect_system_color_mode(self):
        """Detecter system color mode preference."""
        # This will be handled by client-side script that updates the state
        return rx.call_script("""
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            const colorMode = localStorage.getItem('color_mode') || 'system';
            
            function updateColorMode(mode) {
                if (mode === 'system') {
                    const systemMode = mediaQuery.matches ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-color-mode', systemMode);
                } else {
                    document.documentElement.setAttribute('data-color-mode', mode);
                }
            }
            
            // Initial setup
            updateColorMode(colorMode);
            
            // Listen for system preference changes
            mediaQuery.addEventListener('change', (e) => {
                if (localStorage.getItem('color_mode') === 'system') {
                    updateColorMode('system');
                }
            });
            
            // Update state with current preference
            if (colorMode !== 'system') {
                window.dispatchEvent(new CustomEvent('set_color_mode', { detail: colorMode }));
            }
        """)
    
    @rx.var
    def effective_color_mode(self) -> str:
        """Returnerer den effektive color mode (light/dark) baseret på preference."""
        if self.color_mode == "system":
            # Will be determined by client-side script
            return "light"  # Default fallback
        return self.color_mode
    
    def initialize_color_mode(self):
        """Initialiserer color mode ved app start."""
        # Load saved preference from localStorage and detect system preference
        return self.detect_system_color_mode()
    
    def sync_color_mode_from_client(self, mode: str):
        """Synkroniserer color mode fra client-side changes."""
        if mode in ["system", "light", "dark"]:
            self.color_mode = mode
    
    def handle_system_color_change(self):
        """Håndterer system color preference changes."""
        # This will be called when system preference changes
        if self.color_mode == "system":
            # Re-detect system preference
            return rx.call_script("""
                const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
                const systemMode = mediaQuery.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-color-mode', systemMode);
            """)
    
    def download_excel_template(self) -> rx.Component:
        """Download Excel template."""
        try:
            import os
            import base64
            from pathlib import Path
            
            # Direkte sti til template fil
            template_path = Path(__file__).parent.parent / "templates" / "jord_transport_template.xlsx"
            
            if template_path.exists():
                with open(template_path, "rb") as f:
                    file_data = f.read()
                
                excel_base64 = base64.b64encode(file_data).decode()
                self.show_toast_notification("Excel skabelon downloadet", "success")
                
                # Brug JavaScript til download for bedre kompatibilitet
                return rx.call_script(f"""
                    const byteCharacters = atob('{excel_base64}');
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{
                        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }});
                    
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'jord_transport_skabelon.xlsx';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                """)
            else:
                # Prøv at generere template
                try:
                    from templates.create_excel_template import create_excel_template
                    excel_path = create_excel_template()
                    
                    if excel_path and os.path.exists(excel_path):
                        with open(excel_path, "rb") as f:
                            file_data = f.read()
                        
                        excel_base64 = base64.b64encode(file_data).decode()
                        self.show_toast_notification("Excel skabelon genereret og downloadet", "success")
                        
                        return rx.call_script(f"""
                            const byteCharacters = atob('{excel_base64}');
                            const byteNumbers = new Array(byteCharacters.length);
                            for (let i = 0; i < byteCharacters.length; i++) {{
                                byteNumbers[i] = byteCharacters.charCodeAt(i);
                            }}
                            const byteArray = new Uint8Array(byteNumbers);
                            const blob = new Blob([byteArray], {{
                                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            }});
                            
                            const url = URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = 'jord_transport_skabelon.xlsx';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            URL.revokeObjectURL(url);
                        """)
                    else:
                        self.show_toast_notification("Kunne ikke generere Excel skabelon", "error")
                except Exception as gen_error:
                    self.show_toast_notification(f"Fejl ved generering: {str(gen_error)}", "error")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved Excel download: {str(e)}", "error")
    
    def download_csv_template(self) -> rx.Component:
        """Download CSV template."""
        try:
            import os
            import base64
            from pathlib import Path
            
            # Direkte sti til template fil
            template_path = Path(__file__).parent.parent / "templates" / "jord_transport_template.csv"
            
            if template_path.exists():
                with open(template_path, "rb") as f:
                    file_data = f.read()
                
                csv_base64 = base64.b64encode(file_data).decode()
                self.show_toast_notification("CSV skabelon downloadet", "success")
                
                # Brug JavaScript til download for bedre kompatibilitet
                return rx.call_script(f"""
                    const byteCharacters = atob('{csv_base64}');
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{
                        type: 'text/csv'
                    }});
                    
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'jord_transport_skabelon.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                """)
            else:
                # Prøv at generere template
                try:
                    from templates.create_excel_template import create_csv_template
                    csv_path = create_csv_template()
                    
                    if csv_path and os.path.exists(csv_path):
                        with open(csv_path, "rb") as f:
                            file_data = f.read()
                        
                        csv_base64 = base64.b64encode(file_data).decode()
                        self.show_toast_notification("CSV skabelon genereret og downloadet", "success")
                        
                        return rx.call_script(f"""
                            const byteCharacters = atob('{csv_base64}');
                            const byteNumbers = new Array(byteCharacters.length);
                            for (let i = 0; i < byteCharacters.length; i++) {{
                                byteNumbers[i] = byteCharacters.charCodeAt(i);
                            }}
                            const byteArray = new Uint8Array(byteNumbers);
                            const blob = new Blob([byteArray], {{
                                type: 'text/csv'
                            }});
                            
                            const url = URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = 'jord_transport_skabelon.csv';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            URL.revokeObjectURL(url);
                        """)
                    else:
                        self.show_toast_notification("Kunne ikke generere CSV skabelon", "error")
                except Exception as gen_error:
                    self.show_toast_notification(f"Fejl ved generering: {str(gen_error)}", "error")
        except Exception as e:
            self.show_toast_notification(f"Fejl ved CSV download: {str(e)}", "error")
    
    def update_system_preference(self, preference: str):
        """Opdaterer system preference tracking."""
        if preference in ["light", "dark"]:
            self.system_preference = preference
    
    @rx.var
    def current_effective_mode(self) -> str:
        """Returnerer den aktuelle effektive color mode."""
        if self.color_mode == "system":
            return self.system_preference
        return self.color_mode

    # ArrayCastedVar workaround computed variables for length operations
    @rx.var
    def route_data_length(self) -> int:
        """Returnerer længden af route_data som workaround for ArrayCastedVar .length()."""
        return len(self.route_data)
    
    @rx.var
    def addresses_length(self) -> int:
        """Returnerer længden af addresses som workaround for ArrayCastedVar .length()."""
        return len(self.addresses)
    
    @rx.var 
    def filtered_addresses_length(self) -> int:
        """Returnerer længden af filtered_addresses som workaround for ArrayCastedVar .length()."""
        return len(self.filtered_addresses)
    
    @rx.var
    def validation_errors_length(self) -> int:
        """Returnerer længden af validation_errors som workaround for ArrayCastedVar .length()."""
        return len(self.validation_errors)
    
    @rx.var
    def validation_warnings_length(self) -> int:
        """Returnerer længden af validation_warnings som workaround for ArrayCastedVar .length()."""
        return len(self.validation_warnings)
    
    @rx.var
    def selected_routes_length(self) -> int:
        """Returnerer længden af selected_routes som workaround for ArrayCastedVar .length()."""
        return len(self.selected_routes)
    
    # ArrayCastedVar workaround helper methods for contains operations
    @rx.var
    def selected_routes_set(self) -> set:
        """Returnerer selected_routes som set for hurtigere contains lookups."""
        return set(self.selected_routes)
    
    def route_is_selected(self, route_id: str) -> bool:
        """Tjekker om en rute er valgt - workaround for ArrayCastedVar .contains()."""
        return route_id in self.selected_routes


def index():
    """Hovedsiden for RuteBeregner applikationen."""
    # Try to load layout with error handling
    try:
        from components.layout import layout
        return layout()
    except Exception as e:
        # Import here to get full traceback
        import traceback
        import sys
        
        # Get detailed traceback information
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        full_traceback = ''.join(tb_lines)
        
        # Extract the most relevant error line
        tb_list = traceback.extract_tb(exc_traceback)
        error_location = "Ukendt location"
        if tb_list:
            last_frame = tb_list[-1]
            error_location = f"Fil: {last_frame.filename}, Linje: {last_frame.lineno}, Funktion: {last_frame.name}"
        
        # If layout fails, show debug information
        return rx.container(
            rx.vstack(
                rx.heading("Layout Debug Information", size="6", color="red"),
                rx.text(f"FEJL: {str(e)}", size="4", color="red", font_weight="bold"),
                rx.text(f"ERROR TYPE: {type(e).__name__}", size="3", color="orange"),
                rx.text(f"LOCATION: {error_location}", size="3", color="blue"),
                
                # Detailed traceback in a scrollable box
                rx.heading("Full Traceback:", size="4", margin_top="1rem"),
                rx.box(
                    rx.text(
                        full_traceback,
                        size="2",
                        font_family="mono",
                        white_space="pre-wrap"
                    ),
                    background="gray.100",
                    padding="1rem",
                    border_radius="md",
                    max_height="400px",
                    overflow_y="auto",
                    border="1px solid",
                    border_color="gray.300"
                ),
                
                spacing="4",
                align="start",
                width="100%"
            ),
            max_width="1200px",
            margin_x="auto",
            padding="2rem"
        )


# Definer app med tema konfiguration
from theme.custom_theme import get_base_theme

app = rx.App(
    theme=get_base_theme(),
    stylesheets=[
        "/styles.css"  # Include our custom CSS
    ]
)
app.add_page(index)
