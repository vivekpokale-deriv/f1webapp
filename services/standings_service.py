"""
Service for handling F1 standings data.
"""

import logging
import fastf1
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger('f1webapp')

class StandingsService:
    """
    Service for handling F1 standings data.
    """
    
    def __init__(self, cache_dir='cache'):
        """
        Initialize the standings service.
        
        Args:
            cache_dir: Directory for FastF1 cache
        """
        # Adjust paths to be relative to the app root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cache_dir = os.path.join(base_dir, cache_dir)
        
        # Enable FastF1 cache
        fastf1.Cache.enable_cache(self.cache_dir)
        
    def get_driver_standings(self, year=None):
        """
        Get driver standings for a specific year.
        
        Args:
            year: The year to get the standings for (defaults to current year)
            
        Returns:
            dict: Driver standings data
        """
        try:
            # If year is not provided, use current year
            if not year:
                year = datetime.now().year
                
            # Get the latest event for the specified year
            events = fastf1.get_event_schedule(year)
            
            # Filter completed events
            completed_events = events[events['EventDate'] < pd.Timestamp.now()]
            
            if completed_events.empty:
                logger.warning(f"No completed events found for {year}")
                return {"year": year, "standings": []}
                
            # Get the latest completed event
            latest_event = completed_events.iloc[-1]
            
            # Load the session
            session = fastf1.get_session(year, latest_event['EventName'], 'R')
            session.load()
            
            # Get driver standings
            driver_standings = session.get_driver_standings()
            
            # Format the response
            standings = []
            for _, row in driver_standings.iterrows():
                driver_data = {
                    "position": int(row['Position']),
                    "driverCode": row['Abbreviation'],
                    "driverName": f"{row['FirstName']} {row['LastName']}",
                    "teamName": row['TeamName'],
                    "points": float(row['Points'])
                }
                standings.append(driver_data)
                
            return {
                "year": year,
                "lastUpdated": latest_event['EventDate'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                "standings": standings
            }
            
        except Exception as e:
            logger.error(f"Error getting driver standings: {e}")
            return {"year": year if year else datetime.now().year, "standings": []}
    
    def get_constructor_standings(self, year=None):
        """
        Get constructor standings for a specific year.
        
        Args:
            year: The year to get the standings for (defaults to current year)
            
        Returns:
            dict: Constructor standings data
        """
        try:
            # If year is not provided, use current year
            if not year:
                year = datetime.now().year
                
            # Get the latest event for the specified year
            events = fastf1.get_event_schedule(year)
            
            # Filter completed events
            completed_events = events[events['EventDate'] < pd.Timestamp.now()]
            
            if completed_events.empty:
                logger.warning(f"No completed events found for {year}")
                return {"year": year, "standings": []}
                
            # Get the latest completed event
            latest_event = completed_events.iloc[-1]
            
            # Load the session
            session = fastf1.get_session(year, latest_event['EventName'], 'R')
            session.load()
            
            # Get constructor standings
            constructor_standings = session.get_constructor_standings()
            
            # Format the response
            standings = []
            for _, row in constructor_standings.iterrows():
                constructor_data = {
                    "position": int(row['Position']),
                    "teamName": row['TeamName'],
                    "points": float(row['Points'])
                }
                standings.append(constructor_data)
                
            return {
                "year": year,
                "lastUpdated": latest_event['EventDate'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                "standings": standings
            }
            
        except Exception as e:
            logger.error(f"Error getting constructor standings: {e}")
            return {"year": year if year else datetime.now().year, "standings": []}

    def get_all_drivers(self, year=None):
        """
        Get all drivers for a specific year.
        
        Args:
            year: The year to get the drivers for (defaults to current year)
            
        Returns:
            dict: List of drivers
        """
        try:
            # If year is not provided, use current year
            if not year:
                year = datetime.now().year
                
            # Get the first event of the year to load drivers
            events = fastf1.get_event_schedule(year)
            first_event = events.iloc[0]
            
            # Load the session
            session = fastf1.get_session(year, first_event['EventName'], 'R')
            session.load()
            
            # Get all drivers
            drivers = session.drivers
            
            # Format the response
            driver_list = []
            for driver_id in drivers:
                driver_info = session.get_driver(driver_id)
                driver_list.append({
                    "driverId": driver_id,
                    "code": driver_info['Abbreviation'],
                    "name": f"{driver_info['FirstName']} {driver_info['LastName']}",
                    "number": driver_info['DriverNumber']
                })
                
            return {
                "year": year,
                "drivers": driver_list
            }
            
        except Exception as e:
            logger.error(f"Error getting all drivers: {e}")
            return {"year": year if year else datetime.now().year, "drivers": []}
