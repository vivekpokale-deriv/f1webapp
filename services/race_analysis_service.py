"""
Service for handling F1 race analysis.
"""

import logging
import numpy as np
import pandas as pd
import fastf1
import fastf1.plotting
from matplotlib import pyplot as plt
import seaborn as sns
import os
from api.config import get_config

logger = logging.getLogger('f1webapp')
config = get_config()

# Setup FastF1 plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')


class RaceAnalysisService:
    """
    Service for analyzing F1 race data.
    """
    
    def __init__(self, session_service=None):
        """
        Initialize the race analysis service.
        
        Args:
            session_service: Optional SessionService instance for session caching
        """
        from services.session_service import SessionService
        self.session_service = session_service or SessionService()
        
    def get_session(self, year, race, session_type='R'):
        """
        Get a FastF1 session using the SessionService cache.
        
        Args:
            year: The year of the session
            race: The race name or round number
            session_type: The session type (default: 'R' for race)
            
        Returns:
            fastf1.core.Session: The loaded session
        """
        logger.info(f"Getting session data for {year} {race} {session_type}")
        return self.session_service.get_session(int(year), race, session_type)
        
    def get_race_pace_data(self, session, num_drivers=10):
        """
        Get race pace comparison data for the top drivers.
        
        Args:
            session: The FastF1 session
            num_drivers: Number of drivers to include (default: 10)
            
        Returns:
            dict: Race pace data for interactive visualization
        """
        # Get the top drivers
        point_finishers = session.drivers[:num_drivers]
        driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
        driver_laps = driver_laps.reset_index()
        
        # Get the finishing order
        finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]
        
        # Get driver colors
        driver_colors = fastf1.plotting.get_driver_color_mapping(session=session)
        
        # Process data for each driver
        drivers_data = []
        for driver in finishing_order:
            driver_data = driver_laps[driver_laps['Driver'] == driver]
            if not driver_data.empty:
                # Get lap times in seconds
                lap_times = driver_data["LapTime"].dt.total_seconds().tolist()
                
                # Get compounds
                compounds = driver_data["Compound"].tolist()
                
                # Get driver info
                driver_info = session.get_driver(driver)
                
                drivers_data.append({
                    "code": driver,
                    "name": driver_info["FullName"] if "FullName" in driver_info else driver,
                    "color": driver_colors.get(driver, "#FFFFFF"),
                    "team": driver_info["TeamName"] if "TeamName" in driver_info else "",
                    "lapTimes": lap_times,
                    "compounds": compounds
                })
        
        # Return structured data
        return {
            "drivers": drivers_data,
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
        
    def get_team_pace_data(self, session):
        """
        Get team pace comparison data.
        
        Args:
            session: The FastF1 session
            
        Returns:
            dict: Team pace data for interactive visualization
        """
        # Get quick laps
        laps = session.laps.pick_quicklaps()
        
        # Convert lap times to seconds for analysis
        transformed_laps = laps.copy()
        transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()
        
        # Order teams from fastest to slowest
        team_order = (
            transformed_laps[["Team", "LapTime (s)"]]
            .groupby("Team")
            .median()["LapTime (s)"]
            .sort_values()
            .index
        )
        
        # Get team colors
        team_colors = fastf1.plotting.get_team_color_mapping(session=session)
        
        # Process data for each team
        teams_data = []
        for team in team_order:
            team_data = transformed_laps[transformed_laps['Team'] == team]
            if not team_data.empty:
                # Calculate statistics
                lap_times = team_data["LapTime (s)"]
                
                teams_data.append({
                    "name": team,
                    "color": team_colors.get(team, "#FFFFFF"),
                    "lapTimes": {
                        "min": lap_times.min(),
                        "q1": lap_times.quantile(0.25),
                        "median": lap_times.median(),
                        "q3": lap_times.quantile(0.75),
                        "max": lap_times.max()
                    }
                })
        
        # Return structured data
        return {
            "teams": teams_data,
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
        
    def get_lap_sections_data(self, session, drivers=None):
        """
        Get lap sections analysis data.
        
        Args:
            session: The FastF1 session
            drivers: List of driver codes (default: None, will use top 5)
            
        Returns:
            dict: Lap sections data for interactive visualization
        """
        # If no drivers specified, use the top 5 fastest
        if not drivers:
            laps = session.laps.pick_quicklaps()
            drivers = laps['Driver'].unique()[:5]
        else:
            drivers = drivers[:5]  # Limit to 5 drivers
        
        # Define the section types
        section_types = ['braking', 'cornering', 'acceleration', 'full_throttle']
        
        # Get driver colors
        driver_colors = fastf1.plotting.get_driver_color_mapping(session=session)
        
        # Process data for each section type
        sections_data = []
        for section_type in section_types:
            drivers_data = []
            
            for driver in drivers:
                try:
                    lap = session.laps.pick_drivers(driver).pick_fastest()
                    telemetry = lap.get_telemetry()
                    
                    time = telemetry['Time'].dt.total_seconds().tolist()
                    time = [t - time[0] for t in time]  # Normalize to start at 0
                    
                    # Define the sections based on telemetry
                    if section_type == 'braking':
                        mask = telemetry['Brake'] > 0
                    elif section_type == 'full_throttle':
                        mask = telemetry['Throttle'] == 100
                    elif section_type == 'cornering':
                        mask = (telemetry['nGear'] < 5) & (telemetry['Speed'] > 100)  # Simplified cornering detection
                    elif section_type == 'acceleration':
                        mask = (telemetry['Throttle'] > 80) & (telemetry['Throttle'] < 100)
                    else:
                        continue
                    
                    # Extract data for this section
                    section_time = [time[i] for i in range(len(time)) if mask.iloc[i]]
                    section_speed = [telemetry['Speed'].iloc[i] for i in range(len(time)) if mask.iloc[i]]
                    
                    # Only add if we have data
                    if section_time and section_speed:
                        drivers_data.append({
                            "code": driver,
                            "color": driver_colors.get(driver, "#FFFFFF"),
                            "time": section_time,
                            "speed": section_speed
                        })
                except Exception as e:
                    logger.error(f"Error processing lap sections for driver {driver}: {e}")
            
            # Add section data if we have any drivers
            if drivers_data:
                sections_data.append({
                    "name": section_type,
                    "drivers": drivers_data
                })
        
        # Return structured data
        return {
            "sections": sections_data,
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
