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
        
    def create_race_pace_plot(self, session, num_drivers=10):
        """
        Create a race pace comparison plot for the top drivers.
        
        Args:
            session: The FastF1 session
            num_drivers: Number of drivers to include (default: 10)
            
        Returns:
            tuple: (figure, filename) - The matplotlib figure and the saved filename
        """
        # Get the top drivers
        point_finishers = session.drivers[:num_drivers]
        driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
        driver_laps = driver_laps.reset_index()
        
        # Get the finishing order for the plot
        finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]
        
        # Get driver colors
        driver_colors = fastf1.plotting.get_driver_color_mapping(session=session)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=config.DEFAULT_FIG_SIZE)
        
        # Convert lap times to seconds for plotting
        driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
        
        # Create violin plot
        sns.violinplot(data=driver_laps,
                      x="Driver",
                      y="LapTime(s)",
                      inner=None,
                      scale='area',
                      order=finishing_order,
                      palette=driver_colors
                      )
        
        # Add swarm plot for tire compounds
        sns.swarmplot(data=driver_laps,
                     x="Driver",
                     y="LapTime(s)",
                     order=finishing_order,
                     hue="Compound",
                     palette=fastf1.plotting.get_compound_mapping(session=session),
                     hue_order=["SOFT", "MEDIUM", "HARD"],
                     linewidth=0,
                     size=5
                     )
        
        # Set labels and title
        ax.set_xlabel("Driver")
        ax.set_ylabel("Lap Time (s)")
        plt.suptitle(f"Race Pace Comparison\n"
                    f"{session.event['EventName']} {session.event.year}")
        
        # Style adjustments
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        
        # Save and return
        filename = "race_pace_plot.png"
        filepath = os.path.join(os.getcwd(), filename)
        plt.savefig(filepath)
        
        return fig, filepath
        
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
        
    def create_team_pace_plot(self, session):
        """
        Create a team pace comparison plot.
        
        Args:
            session: The FastF1 session
            
        Returns:
            tuple: (figure, filename) - The matplotlib figure and the saved filename
        """
        # Get quick laps
        laps = session.laps.pick_quicklaps()
        
        # Convert lap times to seconds for plotting
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
        team_palette = {}
        for team in team_order:
            team_palette[team] = fastf1.plotting.team_color(team)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Create box plot
        sns.boxplot(
            data=transformed_laps,
            x="Team",
            y="LapTime (s)",
            order=team_order,
            palette=team_palette,
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )
        
        # Set title and style
        plt.title(f"Team Pace Visualization\n"
                 f"{session.event['EventName']} {session.event.year}")
        plt.grid(visible=False)
        
        # Remove redundant x-label
        ax.set(xlabel=None)
        plt.tight_layout()
        
        # Save and return
        filename = "team_pace_plot.png"
        filepath = os.path.join(os.getcwd(), filename)
        plt.savefig(filepath)
        
        return fig, filepath
        
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
        
    def create_lap_sections_plot(self, session, drivers=None):
        """
        Create a lap sections analysis plot.
        
        Args:
            session: The FastF1 session
            drivers: List of driver codes (default: None, will use top 5)
            
        Returns:
            tuple: (figure, filename) - The matplotlib figure and the saved filename
        """
        # If no drivers specified, use the top 5 fastest
        if not drivers:
            laps = session.laps.pick_quicklaps()
            drivers = laps['Driver'].unique()[:5]
        else:
            drivers = drivers[:5]  # Limit to 5 drivers
        
        # Create the plot with 4 subplots
        fig, axs = plt.subplots(2, 2, figsize=config.DEFAULT_FIG_SIZE)
        fig.suptitle(f"Lap Sections for {session.event['EventName']} {session.event.year}")
        
        # Define the section types
        section_types = ['braking', 'cornering', 'acceleration', 'full_throttle']
        
        # Process each driver
        for driver in drivers:
            try:
                lap = session.laps.pick_drivers(driver).pick_fastest()
                telemetry = lap.get_telemetry()
                
                time = telemetry['Time'].dt.total_seconds().tolist()
                time = [t - time[0] for t in time]  # Normalize to start at 0
                
                # Define the sections
                braking_mask = telemetry['Brake'] > 0
                full_throttle_mask = telemetry['Throttle'] == 100
                cornering_mask = (telemetry['nGear'] < 5) & (telemetry['Speed'] > 100)  # Simplified cornering detection
                acceleration_mask = (telemetry['Throttle'] > 80) & (telemetry['Throttle'] < 100)
                
                masks = {
                    'braking': braking_mask,
                    'cornering': cornering_mask,
                    'acceleration': acceleration_mask,
                    'full_throttle': full_throttle_mask
                }
                
                # Plot each section
                for idx, section in enumerate(section_types):
                    mask = masks[section]
                    section_time = [time[i] for i in range(len(time)) if mask.iloc[i]]
                    section_speed = [telemetry['Speed'].iloc[i] for i in range(len(time)) if mask.iloc[i]]
                    
                    if section_time and section_speed:
                        axs[idx // 2, idx % 2].plot(section_time, section_speed, label=driver)
            except Exception as e:
                logger.error(f"Error processing lap sections for driver {driver}: {e}")
        
        # Add labels and legends
        for idx, section in enumerate(section_types):
            axs[idx // 2, idx % 2].set_title(section.replace('_', ' ').capitalize())
            axs[idx // 2, idx % 2].legend()
            axs[idx // 2, idx % 2].set_xlabel("Time (s)")
            axs[idx // 2, idx % 2].set_ylabel("Speed (km/h)")
        
        # Save and return
        filename = "lap_sections_plot.png"
        filepath = os.path.join(os.getcwd(), filename)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(filepath)
        
        return fig, filepath
