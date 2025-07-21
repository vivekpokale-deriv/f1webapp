"""
Service for handling F1 session data.

This service provides caching and management of FastF1 sessions.
"""

import logging
import fastf1
from typing import Dict, Optional, Any
from collections import OrderedDict

logger = logging.getLogger('f1webapp')

class SessionService:
    """
    Service for handling F1 session data with caching.
    """
    
    def __init__(self, max_cache_size=10):
        """
        Initialize the session service.
        
        Args:
            max_cache_size: Maximum number of sessions to cache
        """
        self.max_cache_size = max_cache_size
        self.session_cache = OrderedDict()
        
    def get_session(self, year: int, race: str, session_type: str) -> fastf1.core.Session:
        """
        Get a FastF1 session, using cache if available.
        
        Args:
            year: The year of the session
            race: The race name or round number
            session_type: The session type (e.g., 'R', 'Q', 'FP1')
            
        Returns:
            fastf1.core.Session: The loaded session
        """
        cache_key = f"{year}_{race}_{session_type}"
        
        # Check if session is in cache
        if cache_key in self.session_cache:
            logger.info(f"Using cached session for {year} {race} {session_type}")
            # Move to end to mark as recently used
            self.session_cache.move_to_end(cache_key)
            return self.session_cache[cache_key]
        
        # Load session from FastF1
        logger.info(f"Loading session for {year} {race} {session_type}")
        session = fastf1.get_session(year, race, session_type)
        session.load()
        
        # Add to cache
        self.session_cache[cache_key] = session
        
        # Remove oldest session if cache is full
        if len(self.session_cache) > self.max_cache_size:
            self.session_cache.popitem(last=False)
        
        return session
    
    def clear_cache(self):
        """Clear the session cache."""
        self.session_cache.clear()
        logger.info("Session cache cleared")
