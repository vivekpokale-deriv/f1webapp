"""
Service for handling F1 session data and selection.
"""

import logging
import datetime
import fastf1
from collections import OrderedDict
from api.config import get_config
from utils.color_mapping import get_driver_colors

logger = logging.getLogger('f1webapp')
config = get_config()

class SessionService:
    """
    Service for handling F1 session data and selection.
    """
    
    def __init__(self, max_cache_size=10):
        """
        Initialize the session service with a session cache.
        
        Args:
            max_cache_size: Maximum number of sessions to keep in cache (default: 10)
        """
        # Use OrderedDict for LRU cache implementation
        self._session_cache = OrderedDict()
        self._max_cache_size = max_cache_size
    
    def get_session(self, year, race, session_type):
        """
        Get a session, using cache if available.
        
        Args:
            year: The year of the session
            race: The name of the event
            session_type: The session type code
            
        Returns:
            fastf1.core.Session: The loaded session
        """
        cache_key = f"{year}_{race}_{session_type}"
        
        # Check if session is already in cache
        if cache_key in self._session_cache:
            logger.info(f"Using cached session for {year} {race} {session_type}")
            # Move to end to mark as most recently used
            session = self._session_cache.pop(cache_key)
            self._session_cache[cache_key] = session
            return session
        
        # If not in cache, load it from FastF1
        logger.info(f"Loading session from FastF1 for {year} {race} {session_type}")
        session = fastf1.get_session(year, race, session_type)
        session.load()
        
        # Add to cache
        self._session_cache[cache_key] = session
        
        # If cache is too large, remove the least recently used item
        if len(self._session_cache) > self._max_cache_size:
            self._session_cache.popitem(last=False)
        
        return session
    
    def get_available_years(self):
        """
        Get all available years from 2018 to present.
        
        Returns:
            list: List of available years
        """
        current_year = datetime.datetime.now().year
        # FastF1 has data from 2018 onwards
        return list(range(2018, current_year + 1))
    
    def get_events_for_year(self, year):
        """
        Get all events (races) for a specific year.
        
        Args:
            year: The year to get events for
            
        Returns:
            list: List of events with name and round number
        """
        try:
            logger.info(f"Getting events for year {year}")
            schedule = fastf1.get_event_schedule(year)
            
            events = []
            for _, event in schedule.iterrows():
                events.append({
                    'name': event['EventName'],
                    'round': event['RoundNumber'],
                    'country': event['Country'],
                    'location': event['Location'],
                    'date': event['EventDate'].strftime('%Y-%m-%d') if 'EventDate' in event else None
                })
            
            return events
        except Exception as e:
            logger.error(f"Error getting events for year {year}: {e}")
            return []
    
    def get_session_types(self, year, race):
        """
        Get available session types for a specific event.
        
        Args:
            year: The year of the event
            race: The name of the event
            
        Returns:
            list: List of session types
        """
        try:
            logger.info(f"Getting session types for {year} {race}")
            event = fastf1.get_event(year, race)
            
            sessions = []
            
            # Handle different FastF1 API versions
            if hasattr(event, 'get_session_info'):
                # Older FastF1 versions
                for session_name, session_obj in event.get_session_info().items():
                    if session_name not in ['Event', 'Testing']:
                        sessions.append({
                            'name': session_name,
                            'code': session_obj.name,
                            'date': session_obj.date.strftime('%Y-%m-%d') if hasattr(session_obj, 'date') else None
                        })
            else:
                # Newer FastF1 versions
                session_names = ['FP1', 'FP2', 'FP3', 'SQ', 'S', 'Q', 'R']
                for session_name in session_names:
                    try:
                        session_obj = event.get_session(session_name)
                        if session_obj:
                            sessions.append({
                                'name': session_obj.name,
                                'code': session_name,
                                'date': session_obj.date.strftime('%Y-%m-%d') if hasattr(session_obj, 'date') else None
                            })
                    except Exception as e:
                        logger.debug(f"Session {session_name} not available for {year} {race}: {e}")
            
            return sessions
        except Exception as e:
            logger.error(f"Error getting session types for {year} {race}: {e}")
            return []
    
    def get_drivers_in_session(self, year, race, session_type):
        """
        Get all drivers who participated in a specific session.
        
        Args:
            year: The year of the session
            race: The name of the event
            session_type: The session type code
            
        Returns:
            list: List of drivers with code, name, team, and color
        """
        try:
            logger.info(f"Getting drivers for {year} {race} {session_type}")
            session = self.get_session(year, race, session_type)
            
            # Get driver colors
            driver_colors = get_driver_colors(session)
            
            drivers = []
            for driver_code, driver_data in session.drivers.items():
                try:
                    driver_info = {
                        'code': driver_code,
                        'name': driver_data['FullName'] if 'FullName' in driver_data else driver_code,
                        'number': driver_data['RacingNumber'] if 'RacingNumber' in driver_data else None,
                        'team': driver_data['TeamName'] if 'TeamName' in driver_data else None,
                        'color': driver_colors.get(driver_code, 'white')
                    }
                    drivers.append(driver_info)
                except Exception as e:
                    logger.error(f"Error processing driver {driver_code}: {e}")
            
            return drivers
        except Exception as e:
            logger.error(f"Error getting drivers for {year} {race} {session_type}: {e}")
            return []
    
    def get_driver_laps(self, year, race, session_type, driver):
        """
        Get all laps for a specific driver in a session.
        
        Args:
            year: The year of the session
            race: The name of the event
            session_type: The session type code
            driver: The driver code
            
        Returns:
            list: List of laps with lap number, time, and sector times
        """
        try:
            logger.info(f"Getting laps for {driver} in {year} {race} {session_type}")
            session = self.get_session(year, race, session_type)
            
            # Use pick_drivers (plural) which is the newer API
            driver_laps = session.laps.pick_drivers(driver)
            
            laps = []
            for _, lap in driver_laps.iterrows():
                try:
                    lap_info = {
                        'number': int(lap['LapNumber']),
                        'time': str(lap['LapTime']),
                        'sector1': str(lap['Sector1Time']),
                        'sector2': str(lap['Sector2Time']),
                        'sector3': str(lap['Sector3Time']),
                        'compound': lap['Compound'] if 'Compound' in lap else None,
                        'fresh_tyre': bool(lap['FreshTyre']) if 'FreshTyre' in lap else None,
                        'is_personal_best': bool(lap['IsPersonalBest']) if 'IsPersonalBest' in lap else None
                    }
                    laps.append(lap_info)
                except Exception as e:
                    logger.error(f"Error processing lap {lap['LapNumber']}: {e}")
            
            return laps
        except Exception as e:
            logger.error(f"Error getting laps for {driver} in {year} {race} {session_type}: {e}")
            return []
