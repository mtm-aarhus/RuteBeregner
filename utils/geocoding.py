"""
Modul til håndtering af geocoding og afstandsberegning mellem adresser eller koordinater.
"""
import geopy.distance
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError, GeocoderTimedOut, GeocoderUnavailable
from typing import Union, Tuple, Dict, Any, Optional
import re
import requests
import logging
import time
import random
from functools import wraps

# Import cache system
try:
    from .cache import get_geocode_cache, get_route_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    get_geocode_cache = None
    get_route_cache = None

# Opsætning af logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Konstanter
USER_AGENT = 'RuteBeregner/1.0'
TIMEOUT = 10
OSRM_BASE_URL = 'https://router.project-osrm.org/route/v1/driving'
RETRY_MAX_ATTEMPTS = 3
RETRY_INITIAL_DELAY = 1  # sekunder
RETRY_MAX_DELAY = 60     # sekunder

# Opsætning af geocoder med brugerdefineret user-agent
geocoder = Nominatim(user_agent=USER_AGENT, timeout=TIMEOUT)


def retry_with_backoff(max_retries: int = RETRY_MAX_ATTEMPTS, 
                      initial_delay: float = RETRY_INITIAL_DELAY,
                      max_delay: float = RETRY_MAX_DELAY):
    """
    Decorator til retry logik med exponential backoff.
    
    Args:
        max_retries: Maksimalt antal retry-forsøg
        initial_delay: Initial forsinkelse i sekunder
        max_delay: Maksimal forsinkelse i sekunder
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, requests.Timeout) as e:
                    if attempt == max_retries:
                        logger.error(f"Alle {max_retries} retry-forsøg fejlede for {func.__name__}: {e}")
                        raise
                    
                    # Check if it's a rate limit or server error
                    if hasattr(e, 'response') and e.response is not None:
                        status_code = e.response.status_code
                        if status_code in [429, 503, 502, 504]:  # Rate limit or server errors
                            # Add jitter to avoid thundering herd
                            jitter = random.uniform(0.1, 0.3) * delay
                            sleep_time = min(delay + jitter, max_delay)
                            logger.warning(f"HTTP {status_code} fejl for {func.__name__}, retry {attempt + 1}/{max_retries} efter {sleep_time:.1f}s")
                            time.sleep(sleep_time)
                            delay = min(delay * 2, max_delay)  # Exponential backoff
                            continue
                    
                    # For other errors, retry with backoff
                    if attempt < max_retries:
                        jitter = random.uniform(0.1, 0.3) * delay
                        sleep_time = min(delay + jitter, max_delay)
                        logger.warning(f"Fejl for {func.__name__}, retry {attempt + 1}/{max_retries} efter {sleep_time:.1f}s: {e}")
                        time.sleep(sleep_time)
                        delay = min(delay * 2, max_delay)
                    else:
                        raise
                        
            return None
        return wrapper
    return decorator


@retry_with_backoff()
def _osrm_api_request(start_coords: Tuple[float, float], 
                     end_coords: Tuple[float, float]) -> Optional[float]:
    """
    Udfører OSRM API forespørgsel med retry logik.
    
    Args:
        start_coords: Start koordinater (lat, lon)
        end_coords: End koordinater (lat, lon)
        
    Returns:
        Afstand i kilometer eller None hvis forespørgslen fejler
    """
    s_lat, s_lng = start_coords
    e_lat, e_lng = end_coords
    
    # OSRM forventer lon,lat format
    url = f"{OSRM_BASE_URL}/{s_lng},{s_lat};{e_lng},{e_lat}?overview=false&alternatives=false"
    
    logger.debug(f"OSRM API forespørgsel: {url}")
    
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()  # Kaster exception ved HTTP fejl
    
    data = response.json()
    routes = data.get("routes", [])
    
    if not routes:
        logger.warning("OSRM API returnerede ingen ruter")
        return None
        
    # distance er i meter, konverter til kilometer
    distance_m = routes[0].get("distance", 0)
    distance_km = distance_m / 1000.0
    
    logger.info(f"OSRM rute-afstand: {distance_km:.2f} km")
    return distance_km

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validerer om latitude og longitude er inden for gyldige rammer.
    
    Args:
        lat: Latitude værdi
        lon: Longitude værdi
        
    Returns:
        True hvis koordinaterne er gyldige, False ellers
    """
    try:
        is_valid = -90 <= lat <= 90 and -180 <= lon <= 180
        if not is_valid:
            logger.warning(f"Ugyldige koordinater: lat={lat}, lon={lon}")
        return is_valid
    except (TypeError, ValueError) as e:
        logger.error(f"Fejl ved validering af koordinater lat={lat}, lon={lon}: {e}")
        return False


def parse_coordinates(coord_str: str) -> Optional[Tuple[float, float]]:
    """
    Konverterer en koordinat-streng til en tuple af latitude og longitude.
    Understøtter formater som '55.676, 12.568' eller '55.676 N, 12.568 E'.
    
    Args:
        coord_str: Koordinat-streng (f.eks. "55.676098, 12.568337" eller "55.676 N, 12.568 E")
        
    Returns:
        Tuple af (latitude, longitude) eller None hvis parsing fejler
    """
    if not coord_str:
        logger.debug("Tom koordinat-streng modtaget")
        return None
        
    try:
        logger.debug(f"Forsøger at parse koordinater: '{coord_str}'")
        
        # Håndter formater som '55.676 N, 12.568 E' eller '55° 40' 36.35" N, 12° 34' 6.01" E'
        # Fjern eventuelle grader, minutter, sekunder markeringer og retningsangivelser
        cleaned = re.sub(r'[°\'"NSEW]', '', coord_str)
        # Fjern eventuelle paranteser og andre ikke-numeriske tegn (undtagen komma, punktum og minus)
        cleaned = re.sub(r'[^\d., -]', '', cleaned)
        
        # Prøv forskellige separatorer (komma, mellemrum)
        parts = None
        for sep in [',', ' ']:
            parts = cleaned.split(sep)
            if len(parts) >= 2:
                try:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    
                    # Validér latitude og longitude ranges
                    if validate_coordinates(lat, lng):
                        logger.debug(f"Succesfuldt parset koordinater: ({lat}, {lng})")
                        return (lat, lng)
                except ValueError as e:
                    logger.debug(f"Kunne ikke konvertere til float: {e}")
                    continue
        
        logger.warning(f"Kunne ikke parse koordinater fra: '{coord_str}'")
        return None
        
    except Exception as e:
        logger.error(f"Uventet fejl ved parsing af koordinater '{coord_str}': {e}")
        return None

def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Konverterer en adresse til koordinater ved hjælp af Nominatim geocoding.
    Prioriterer danske resultater ved at tilføje 'Denmark' til søgningen hvis ikke specificeret.
    Benytter caching for at optimere performance ved gentagne opslag.
    
    Args:
        address: Adresse at konvertere
        
    Returns:
        Tuple af (latitude, longitude) eller None hvis geocoding fejler
    """
    if not address:
        logger.debug("Tom adresse modtaget til geocoding")
        return None
        
    try:
        logger.debug(f"Forsøger geocoding af adresse: '{address}'")
        
        # Tjek først om adressen allerede er koordinater
        coords = parse_coordinates(address)
        if coords:
            logger.debug("Adresse blev genkendt som koordinater")
            return coords
        
        # Check cache first
        if CACHE_AVAILABLE and get_geocode_cache:
            geocode_cache = get_geocode_cache()
            cached_coords = geocode_cache.get_coordinates(address)
            if cached_coords:
                logger.debug(f"Cache hit for geocoding: {address}")
                return cached_coords
            
        # Forbered adresse for søgning - tilføj Danmark hvis ikke specificeret
        search_address = address
        if 'denmark' not in address.lower() and 'danmark' not in address.lower():
            search_address = f"{address}, Denmark"
            logger.debug(f"Tilføjede Danmark til søgning: '{search_address}'")
            
        # Prøv geocoding med timeout håndtering
        location = geocoder.geocode(search_address, timeout=TIMEOUT)
        if location:
            result = (location.latitude, location.longitude)
            
            # Cache the result
            if CACHE_AVAILABLE and get_geocode_cache:
                geocode_cache = get_geocode_cache()
                geocode_cache.set_coordinates(address, result[0], result[1])
                logger.debug(f"Cached geocoding result for: {address}")
            
            logger.info(f"Succesfuld geocoding af '{address}' til {result}")
            return result
        else:
            logger.warning(f"Geocoding returnerede intet resultat for: '{address}'")
            
    except GeocoderTimedOut:
        logger.error(f"Geocoding timeout for adresse: '{address}'")
    except GeocoderUnavailable:
        logger.error(f"Geocoding service utilgængelig for adresse: '{address}'")
    except GeopyError as e:
        logger.error(f"Geocoding fejl for adresse '{address}': {e}")
    except Exception as e:
        logger.error(f"Uventet fejl ved geocoding af adresse '{address}': {e}")
    
    return None

def calculate_distance(start: Union[str, Tuple[float, float]], 
                      end: Union[str, Tuple[float, float]]) -> float:
    """
    Beregner afstanden mellem to lokationer (adresse eller koordinater).
    
    Args:
        start: Start lokation (adresse eller koordinater)
        end: Slut lokation (adresse eller koordinater)
        
    Returns:
        Afstand i kilometer eller 0 hvis beregning fejler
    """
    try:
        logger.debug(f"Beregner afstand fra {start} til {end}")
        
        # Konverter start lokation til koordinater hvis det er en streng
        if isinstance(start, str):
            start_coords = geocode_address(start)
            if not start_coords:
                logger.error(f"Kunne ikke geocode startadresse: '{start}'")
                return 0.0
        else:
            start_coords = start
            
        # Konverter end lokation til koordinater hvis det er en streng
        if isinstance(end, str):
            end_coords = geocode_address(end)
            if not end_coords:
                logger.error(f"Kunne ikke geocode slutadresse: '{end}'")
                return 0.0
        else:
            end_coords = end
        
        # Beregn afstand hvis begge koordinater er tilgængelige
        if start_coords and end_coords:
            # Check cache first
            if CACHE_AVAILABLE and get_route_cache:
                route_cache = get_route_cache()
                cached_distance = route_cache.get_distance(start_coords, end_coords)
                if cached_distance is not None:
                    logger.debug(f"Cache hit for route distance: {start_coords} -> {end_coords}")
                    return cached_distance
            
            # 1) Forsøg kørselsafstand via OSRM med retry logik
            try:
                distance_km = _osrm_api_request(start_coords, end_coords)
                if distance_km is not None:
                    # Cache the OSRM result
                    if CACHE_AVAILABLE and get_route_cache:
                        route_cache = get_route_cache()
                        route_cache.set_distance(start_coords, end_coords, distance_km)
                        logger.debug(f"Cached OSRM route distance: {start_coords} -> {end_coords}")
                    return distance_km
            except Exception as e:
                logger.warning(f"OSRM rute-API fejlede efter retry-forsøg: {e}")
            
            # 2) Fallback: luftlinje (geodesic)
            try:
                distance_km = geopy.distance.geodesic(start_coords, end_coords).kilometers
                
                # Cache the geodesic result too
                if CACHE_AVAILABLE and get_route_cache:
                    route_cache = get_route_cache()
                    route_cache.set_distance(start_coords, end_coords, distance_km)
                    logger.debug(f"Cached geodesic route distance: {start_coords} -> {end_coords}")
                
                logger.info(f"Geodesic luftlinjeafstand: {distance_km:.2f} km")
                return distance_km
            except Exception as e:
                logger.error(f"Afstandsberegning (geodesic) fejl: {e}")
                
            logger.error("Alle afstandsberegningsmetoder fejlede")
            return 0.0
    
    except Exception as e:
        logger.error(f"Uventet fejl i calculate_distance: {e}")
        return 0.0


def geocode(input_str: str) -> Optional[Tuple[float, float]]:
    """
    Integreret geocoding funktion der først forsøger koordinat parsing, 
    derefter adresse geocoding.
    
    Args:
        input_str: Input streng - enten koordinater eller adresse
        
    Returns:
        Tuple af (latitude, longitude) eller None hvis både parsing og geocoding fejler
        
    Examples:
        >>> geocode("55.676, 12.568")  # Koordinater
        (55.676, 12.568)
        >>> geocode("Rådhuspladsen 1, København")  # Adresse
        (55.6760968, 12.5683372)
    """
    if not input_str:
        logger.debug("Tom input til geocode funktion")
        return None
    
    logger.debug(f"Geocoding input: '{input_str}'")
    
    # Forsøg først koordinat parsing
    coords = parse_coordinates(input_str)
    if coords:
        logger.debug("Input blev succesfuldt parset som koordinater")
        return coords
    
    # Hvis parsing fejler, forsøg geocoding som adresse
    logger.debug("Koordinat parsing fejlede, forsøger geocoding som adresse")
    return geocode_address(input_str)


def get_cache_statistics() -> Dict[str, Any]:
    """
    Returnerer cache statistikker for debugging og monitoring.
    
    Returns:
        Dictionary med cache statistikker
    """
    if not CACHE_AVAILABLE:
        return {"cache_available": False, "message": "Cache system ikke tilgængeligt"}
    
    try:
        from .cache import get_all_cache_stats
        stats = get_all_cache_stats()
        stats["cache_available"] = True
        return stats
    except Exception as e:
        logger.error(f"Fejl ved hentning af cache statistikker: {e}")
        return {"cache_available": False, "error": str(e)}


def clear_geocoding_caches() -> Dict[str, str]:
    """
    Rydder alle geocoding og rute caches.
    
    Returns:
        Status besked
    """
    if not CACHE_AVAILABLE:
        return {"status": "error", "message": "Cache system ikke tilgængeligt"}
    
    try:
        from .cache import clear_all_caches
        clear_all_caches()
        logger.info("Alle geocoding caches er ryddet")
        return {"status": "success", "message": "Alle caches ryddet"}
    except Exception as e:
        logger.error(f"Fejl ved rydning af caches: {e}")
        return {"status": "error", "message": str(e)}


def warm_cache_from_routes(routes: list) -> Dict[str, Any]:
    """
    Pre-populerer cache med geocoding data fra rute liste.
    
    Args:
        routes: Liste af ruter med adresse data
        
    Returns:
        Statistikker for cache warm-up processen
    """
    if not CACHE_AVAILABLE or not routes:
        return {"processed": 0, "geocoded": 0, "message": "Cache ikke tilgængeligt eller ingen ruter"}
    
    geocoded_count = 0
    processed_count = 0
    
    try:
        for route in routes:
            processed_count += 1
            
            # Geocode start address if present
            start_addr = route.get("start_address")
            if start_addr and isinstance(start_addr, str):
                coords = geocode_address(start_addr)
                if coords:
                    geocoded_count += 1
            
            # Geocode end address if present
            end_addr = route.get("end_address") 
            if end_addr and isinstance(end_addr, str):
                coords = geocode_address(end_addr)
                if coords:
                    geocoded_count += 1
        
        logger.info(f"Cache warm-up complete: {geocoded_count} adresser geocodet fra {processed_count} ruter")
        return {
            "processed": processed_count,
            "geocoded": geocoded_count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Fejl ved cache warm-up: {e}")
        return {
            "processed": processed_count,
            "geocoded": geocoded_count,
            "status": "error",
            "error": str(e)
        }
