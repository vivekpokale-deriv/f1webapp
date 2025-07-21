"""
Service for handling F1 schedule data.
"""

import logging
import fastf1
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger('f1webapp')

class ScheduleService:
    """
    Service for handling F1 schedule data.
    """
    
    # Cache expiration time in seconds (24 hours)
    CACHE_EXPIRATION = 24 * 60 * 60
    
    def __init__(self, cache_dir='cache'):
        """
        Initialize the schedule service.
        
        Args:
            cache_dir: Directory for FastF1 cache
        """
        # Adjust paths to be relative to the app root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = os.path.join(base_dir, cache_dir)
        self.data_dir = os.path.join(base_dir, 'data')
        
        # In-memory cache for schedules
        self.schedule_cache = {}
        
        # Load country flags data
        self.country_flags = self._load_country_flags()
        
        # Enable FastF1 cache
        fastf1.Cache.enable_cache(self.cache_dir)
    
    def _load_country_flags(self) -> Dict[str, str]:
        """
        Load country flags data from JSON file.
        
        Returns:
            dict: Country flags data
        """
        try:
            flags_file = os.path.join(self.data_dir, 'country_flags.json')
            if os.path.exists(flags_file):
                with open(flags_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Country flags file not found: {flags_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading country flags: {e}")
            return {}
    
    def _get_cached_schedule(self, year: int) -> Tuple[Optional[fastf1.events.EventSchedule], bool]:
        """
        Get a cached schedule if available and not expired.
        
        Args:
            year: The year to get the schedule for
            
        Returns:
            tuple: (schedule, is_from_cache) - The schedule and whether it was from cache
        """
        cache_key = f"schedule_{year}"
        
        if cache_key in self.schedule_cache:
            cache_entry = self.schedule_cache[cache_key]
            cache_time = cache_entry.get('time', 0)
            
            # Check if cache is still valid
            if time.time() - cache_time < self.CACHE_EXPIRATION:
                logger.info(f"Using cached schedule for {year}")
                return cache_entry.get('data'), True
        
        return None, False
    
    def _cache_schedule(self, year: int, schedule: fastf1.events.EventSchedule) -> None:
        """
        Cache a schedule for future use.
        
        Args:
            year: The year of the schedule
            schedule: The schedule to cache
        """
        cache_key = f"schedule_{year}"
        self.schedule_cache[cache_key] = {
            'data': schedule,
            'time': time.time()
        }
        logger.info(f"Cached schedule for {year}")
    
    def _filter_testing_events(self, schedule: fastf1.events.EventSchedule) -> fastf1.events.EventSchedule:
        """
        Filter out testing events from a schedule.
        
        Args:
            schedule: The schedule to filter
            
        Returns:
            EventSchedule: Filtered schedule without testing events
        """
        # Use the is_testing method to filter out testing events
        non_testing_events = schedule[~schedule.apply(lambda x: x.is_testing(), axis=1)]
        return non_testing_events
    
    def _get_event_status(self, event_date: pd.Timestamp) -> str:
        """
        Determine the status of an event based on its date.
        
        Args:
            event_date: The date of the event
            
        Returns:
            str: 'past', 'current', or 'future'
        """
        now = pd.Timestamp.now()
        
        # Event is in the past
        if event_date < now - pd.Timedelta(days=1):
            return 'past'
        
        # Event is current (within a day before and 2 days after)
        if now - pd.Timedelta(days=1) <= event_date <= now + pd.Timedelta(days=2):
            return 'current'
        
        # Event is in the future
        return 'future'
    
    def get_schedule(self, year=None, include_testing=False) -> Dict[str, Any]:
        """
        Get the F1 schedule for a specific year.
        
        Args:
            year: The year to get the schedule for (defaults to current year)
            include_testing: Whether to include testing events
            
        Returns:
            dict: Schedule data
        """
        try:
            # If year is not provided, use current year
            if not year:
                year = datetime.now().year
            else:
                year = int(year)
            
            # Try to get from cache first
            schedule, from_cache = self._get_cached_schedule(year)
            
            # If not in cache or expired, fetch from FastF1
            if not from_cache:
                logger.info(f"Fetching schedule for {year} from FastF1")
                schedule = fastf1.get_event_schedule(year)
                self._cache_schedule(year, schedule)
            
            # Filter out testing events if requested
            if not include_testing:
                schedule = self._filter_testing_events(schedule)
            
            # Format the response
            races = []
            for _, row in schedule.iterrows():
                # Get country flag URL
                country = row['Country']
                flag_url = self.country_flags.get(country, None)
                
                # Get event sessions
                event_sessions = []
                for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R']:
                    session_date_col = f"{session_type}Date"
                    session_time_col = f"{session_type}Time"
                    
                    if session_date_col in row and pd.notna(row[session_date_col]) and \
                       session_time_col in row and pd.notna(row[session_time_col]):
                        session_date = row[session_date_col]
                        session_time = row[session_time_col]
                        
                        # Convert to datetime
                        if isinstance(session_date, str):
                            session_date = pd.to_datetime(session_date)
                        if isinstance(session_time, str):
                            session_time = pd.to_datetime(session_time).time()
                            
                        # Combine date and time
                        session_datetime = pd.Timestamp.combine(session_date.date(), session_time)
                        
                        # Map session type to full name
                        session_name = {
                            'FP1': 'Practice 1',
                            'FP2': 'Practice 2',
                            'FP3': 'Practice 3',
                            'Q': 'Qualifying',
                            'S': 'Sprint',
                            'R': 'Race'
                        }.get(session_type, session_type)
                        
                        event_sessions.append({
                            'type': session_name,
                            'startTime': session_datetime.isoformat()
                        })
                
                race_data = {
                    'round': int(row['RoundNumber']),
                    'name': row['EventName'],
                    'location': row['Location'],
                    'country': country,
                    'flagUrl': flag_url,
                    'events': event_sessions
                }
                races.append(race_data)
                
            return {
                'year': year,
                'races': races
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return {'year': year, 'races': []}
    
    def get_next_event(self) -> Dict[str, Any]:
        """
        Get the next upcoming F1 event.
        
        Returns:
            dict: Next event data
        """
        try:
            # Get the current year's schedule
            year = datetime.now().year
            schedule = fastf1.get_event_schedule(year)
            
            # Filter future events
            now = pd.Timestamp.now()
            future_events = schedule[schedule['EventDate'] > now]
            
            if future_events.empty:
                # Check next year if no future events in current year
                next_year = year + 1
                next_year_schedule = fastf1.get_event_schedule(next_year)
                if next_year_schedule.empty:
                    logger.warning(f"No events found for {next_year}")
                    return {}
                    
                # Get the first event of next year
                next_event = next_year_schedule.iloc[0]
            else:
                # Get the next event
                next_event = future_events.iloc[0]
            
            # Get country flag URL
            country = next_event['Country']
            flag_url = self.country_flags.get(country, None)
            
            # Get event sessions
            event_sessions = []
            
            # Check if we have session data
            has_session_data = False
            for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R']:
                session_date_col = f"{session_type}Date"
                if session_date_col in next_event and pd.notna(next_event[session_date_col]):
                    has_session_data = True
                    break
            
            if has_session_data:
                # Process actual session data
                for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R']:
                    session_date_col = f"{session_type}Date"
                    session_time_col = f"{session_type}Time"
                    
                    if session_date_col in next_event and pd.notna(next_event[session_date_col]) and \
                       session_time_col in next_event and pd.notna(next_event[session_time_col]):
                        session_date = next_event[session_date_col]
                        session_time = next_event[session_time_col]
                        
                        # Convert to datetime
                        if isinstance(session_date, str):
                            session_date = pd.to_datetime(session_date)
                        if isinstance(session_time, str):
                            session_time = pd.to_datetime(session_time).time()
                            
                        # Combine date and time
                        session_datetime = pd.Timestamp.combine(session_date.date(), session_time)
                        
                        # Map session type to full name
                        session_name = {
                            'FP1': 'Practice 1',
                            'FP2': 'Practice 2',
                            'FP3': 'Practice 3',
                            'Q': 'Qualifying',
                            'S': 'Sprint',
                            'R': 'Race'
                        }.get(session_type, session_type)
                        
                        event_sessions.append({
                            'type': session_name,
                            'startTime': session_datetime.isoformat()
                        })
            else:
                # Create placeholder session data based on typical F1 weekend
                # Get the event date
                event_date = next_event['EventDate']
                if isinstance(event_date, str):
                    event_date = pd.to_datetime(event_date)
                
                # Calculate session dates (typically Friday, Saturday, Sunday)
                race_day = event_date.date()  # Sunday
                saturday = race_day - pd.Timedelta(days=1)
                friday = race_day - pd.Timedelta(days=2)
                
                # Add placeholder sessions
                event_sessions = [
                    {
                        'type': 'Practice 1',
                        'startTime': pd.Timestamp.combine(friday, pd.Timestamp('13:30:00').time()).isoformat(),
                        'placeholder': True
                    },
                    {
                        'type': 'Practice 2',
                        'startTime': pd.Timestamp.combine(friday, pd.Timestamp('17:00:00').time()).isoformat(),
                        'placeholder': True
                    },
                    {
                        'type': 'Practice 3',
                        'startTime': pd.Timestamp.combine(saturday, pd.Timestamp('12:30:00').time()).isoformat(),
                        'placeholder': True
                    },
                    {
                        'type': 'Qualifying',
                        'startTime': pd.Timestamp.combine(saturday, pd.Timestamp('16:00:00').time()).isoformat(),
                        'placeholder': True
                    },
                    {
                        'type': 'Race',
                        'startTime': pd.Timestamp.combine(race_day, pd.Timestamp('15:00:00').time()).isoformat(),
                        'placeholder': True
                    }
                ]
            
            # Sort sessions by start time
            event_sessions.sort(key=lambda x: x['startTime'])
            
            race_data = {
                'round': int(next_event['RoundNumber']),
                'name': next_event['EventName'],
                'location': next_event['Location'],
                'country': country,
                'flagUrl': flag_url
            }
            
            return {
                'race': race_data,
                'events': event_sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting next event: {e}")
            return {}
