import time
from typing import Dict, Optional, List
import logging

from .models import Post
from .utils.config import API_CONFIG

logger = logging.getLogger(__name__)

class Cache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, ttl: int = None):
        self.ttl = ttl or API_CONFIG['cache_ttl']
        self.cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
    
    def get(self, key: str) -> Optional[List[Post]]:
        """
        Get data from cache if it exists and hasn't expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        
        # Check if cache entry has expired
        if time.time() - timestamp > self.ttl:
            logger.debug(f"Cache entry expired for key: {key}")
            del self.cache[key]
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return data
    
    def set(self, key: str, data: List[Post]) -> None:
        """
        Set data in cache with current timestamp
        
        Args:
            key: Cache key
            data: Data to cache
        """
        self.cache[key] = (data, time.time())
        logger.debug(f"Cached data for key: {key}")
    
    def delete(self, key: str) -> bool:
        """
        Delete data from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if key didn't exist
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache entry for key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        current_time = time.time()
        total_entries = len(self.cache)
        expired_entries = 0
        
        for _, (_, timestamp) in self.cache.items():
            if current_time - timestamp > self.ttl:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'valid_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'ttl': self.ttl
        }
    
    def size(self) -> int:
        """Get current cache size (number of entries)"""
        return len(self.cache)
