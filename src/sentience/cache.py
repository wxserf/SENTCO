"""
Caching functionality for ESI data
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DataCache:
    """Simple in-memory cache for ESI data"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
        
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.utcnow() - timestamp < self.ttl:
                logger.debug(f"Cache hit for key: {key}")
                return data
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self.cache[key]
        logger.debug(f"Cache miss for key: {key}")
        return None
        
    def set(self, key: str, data: Any) -> None:
        """Store data in cache"""
        self.cache[key] = (data, datetime.utcnow())
        logger.debug(f"Cached data for key: {key}")
        
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")
        
    def remove(self, key: str) -> None:
        """Remove specific key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Removed key from cache: {key}")
