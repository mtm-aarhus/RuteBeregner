"""
Cache system for optimeret performance af geocoding og rute beregninger.
"""
import logging
import hashlib
import time
from typing import Any, Optional, Tuple, Dict
from collections import OrderedDict
from threading import Lock

logger = logging.getLogger(__name__)


class LRUCache:
    """
    Generic LRU (Least Recently Used) cache implementering med thread safety.
    
    Bruger OrderedDict for O(1) operations på get/set og LRU eviction.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maksimal antal entries i cache
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.lock = Lock()  # Thread safety
        
        # Cache statistikker
        self.hit_count = 0
        self.miss_count = 0
        self.total_requests = 0
        self.created_at = time.time()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Henter værdi fra cache og opdaterer LRU order.
        
        Args:
            key: Cache nøgle
            
        Returns:
            Cached værdi eller None hvis ikke fundet
        """
        with self.lock:
            self.total_requests += 1
            
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hit_count += 1
                logger.debug(f"Cache HIT for key: {key[:50]}...")
                return value
            else:
                self.miss_count += 1
                logger.debug(f"Cache MISS for key: {key[:50]}...")
                return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Sætter værdi i cache og evict hvis nødvendigt.
        
        Args:
            key: Cache nøgle
            value: Værdi at cache
        """
        with self.lock:
            if key in self.cache:
                # Update existing key - move to end
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used item
                oldest_key, _ = self.cache.popitem(last=False)
                logger.debug(f"Cache evicted LRU key: {oldest_key[:50]}...")
            
            self.cache[key] = value
            logger.debug(f"Cache SET for key: {key[:50]}...")
    
    def clear(self) -> None:
        """Rydder al cache data og nulstiller statistikker."""
        with self.lock:
            self.cache.clear()
            self.hit_count = 0
            self.miss_count = 0
            self.total_requests = 0
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returnerer cache statistikker.
        
        Returns:
            Dictionary med cache statistikker
        """
        with self.lock:
            hit_rate = (self.hit_count / max(self.total_requests, 1)) * 100
            uptime = time.time() - self.created_at
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "total_requests": self.total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "uptime_seconds": round(uptime, 2)
            }
    
    def __len__(self) -> int:
        """Returnerer antal entries i cache."""
        with self.lock:
            return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """Checker om nøgle eksisterer i cache uden at opdatere LRU order."""
        with self.lock:
            return key in self.cache


class GeocodeCache(LRUCache):
    """
    Specialiseret cache for geocoding adresse -> koordinater.
    """
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        logger.info(f"GeocodeCache initialized med max_size={max_size}")
    
    def _normalize_address(self, address: str) -> str:
        """
        Normaliser adresse til konsistent cache nøgle.
        
        Args:
            address: Raw adresse string
            
        Returns:
            Normaliseret adresse nøgle
        """
        # Convert to lowercase, strip whitespace, normalize spaces
        normalized = " ".join(address.lower().strip().split())
        # Create hash for long addresses to keep keys manageable
        if len(normalized) > 100:
            return f"addr_{hashlib.md5(normalized.encode()).hexdigest()}"
        return f"addr_{normalized}"
    
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Henter koordinater for adresse fra cache.
        
        Args:
            address: Adresse string
            
        Returns:
            (latitude, longitude) tuple eller None
        """
        key = self._normalize_address(address)
        return self.get(key)
    
    def set_coordinates(self, address: str, lat: float, lon: float) -> None:
        """
        Cacher koordinater for adresse.
        
        Args:
            address: Adresse string
            lat: Latitude
            lon: Longitude
        """
        key = self._normalize_address(address)
        self.set(key, (lat, lon))


class RouteCache(LRUCache):
    """
    Specialiseret cache for rute beregninger koordinater -> distance.
    """
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        logger.info(f"RouteCache initialized med max_size={max_size}")
    
    def _create_route_key(self, start_coords: Tuple[float, float], 
                         end_coords: Tuple[float, float]) -> str:
        """
        Opretter konsistent cache nøgle for rute.
        
        Args:
            start_coords: (lat, lon) for start
            end_coords: (lat, lon) for slut
            
        Returns:
            Cache nøgle string
        """
        # Round coordinates to 6 decimal places for consistency (about 10cm precision)
        start_lat, start_lon = round(start_coords[0], 6), round(start_coords[1], 6)
        end_lat, end_lon = round(end_coords[0], 6), round(end_coords[1], 6)
        
        # Sort coordinates to make route bidirectional (A->B same as B->A)
        coord_pair = sorted([(start_lat, start_lon), (end_lat, end_lon)])
        
        return f"route_{coord_pair[0][0]},{coord_pair[0][1]}_to_{coord_pair[1][0]},{coord_pair[1][1]}"
    
    def get_distance(self, start_coords: Tuple[float, float], 
                    end_coords: Tuple[float, float]) -> Optional[float]:
        """
        Henter cached distance mellem koordinater.
        
        Args:
            start_coords: Start koordinater (lat, lon)
            end_coords: Slut koordinater (lat, lon)
            
        Returns:
            Distance i km eller None
        """
        key = self._create_route_key(start_coords, end_coords)
        return self.get(key)
    
    def set_distance(self, start_coords: Tuple[float, float], 
                    end_coords: Tuple[float, float], distance_km: float) -> None:
        """
        Cacher distance mellem koordinater.
        
        Args:
            start_coords: Start koordinater (lat, lon)
            end_coords: Slut koordinater (lat, lon)
            distance_km: Beregnede distance i kilometer
        """
        key = self._create_route_key(start_coords, end_coords)
        self.set(key, distance_km)


# Global cache instances
_geocode_cache: Optional[GeocodeCache] = None
_route_cache: Optional[RouteCache] = None


def get_geocode_cache(max_size: int = 1000) -> GeocodeCache:
    """
    Returnerer global geocode cache instance.
    
    Args:
        max_size: Maksimal cache størrelse (kun brugt ved første opkald)
        
    Returns:
        GeocodeCache instance
    """
    global _geocode_cache
    if _geocode_cache is None:
        _geocode_cache = GeocodeCache(max_size)
    return _geocode_cache


def get_route_cache(max_size: int = 1000) -> RouteCache:
    """
    Returnerer global route cache instance.
    
    Args:
        max_size: Maksimal cache størrelse (kun brugt ved første opkald)
        
    Returns:
        RouteCache instance
    """
    global _route_cache
    if _route_cache is None:
        _route_cache = RouteCache(max_size)
    return _route_cache


def clear_all_caches() -> None:
    """Rydder alle caches."""
    global _geocode_cache, _route_cache
    
    if _geocode_cache:
        _geocode_cache.clear()
    if _route_cache:
        _route_cache.clear()
        
    logger.info("All caches cleared")


def get_all_cache_stats() -> Dict[str, Dict[str, Any]]:
    """
    Returnerer statistikker for alle caches.
    
    Returns:
        Dictionary med cache statistikker
    """
    stats = {}
    
    if _geocode_cache:
        stats["geocode"] = _geocode_cache.get_stats()
    
    if _route_cache:
        stats["route"] = _route_cache.get_stats()
    
    return stats