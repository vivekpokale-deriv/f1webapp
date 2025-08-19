"""
Service for handling F1 telemetry data processing.
"""

import logging
import numpy as np
import pandas as pd
import fastf1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import seaborn as sns
from api.config import get_config
from utils.color_mapping import get_color_mapping

logger = logging.getLogger('f1webapp')
config = get_config()

# Setup FastF1 plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')


class MiniSectorAnalyzer:
    """
    Analyzer for creating and analyzing mini-sectors on a track.
    """
    
    def __init__(self, telemetry_data, num_sectors=config.DEFAULT_MINI_SECTORS, sector_type='distance'):
        """
        Initialize the mini-sector analyzer.
        
        Args:
            telemetry_data: The telemetry data to analyze
            num_sectors: Number of mini-sectors to create (default: from Config)
            sector_type: Type of mini-sectors ('distance', 'time', or 'angle')
        """
        self.telemetry = telemetry_data
        self.num_sectors = num_sectors
        self.sector_type = sector_type
        
    def create_mini_sectors(self):
        """
        Create mini-sectors based on the specified type.
        
        Returns:
            pandas.DataFrame: Telemetry data with mini-sector information
        """
        if self.sector_type == 'distance':
            self.telemetry['MiniSector'] = pd.cut(
                self.telemetry['Distance'], 
                self.num_sectors, 
                labels=False
            )
        elif self.sector_type == 'time':
            self.telemetry['MiniSector'] = pd.cut(
                self.telemetry['Time'].dt.total_seconds(), 
                self.num_sectors, 
                labels=False
            )
        elif self.sector_type == 'angle':
            # Calculate track angle for more natural mini-sectors around corners
            x_diff = self.telemetry['X'].diff()
            y_diff = self.telemetry['Y'].diff()
            angles = np.arctan2(y_diff, x_diff)
            # Normalize angles to 0-2π range
            angles = (angles + 2 * np.pi) % (2 * np.pi)
            self.telemetry['Angle'] = angles
            self.telemetry['MiniSector'] = pd.cut(
                angles, 
                self.num_sectors, 
                labels=False
            )
        else:
            raise ValueError(f"Invalid sector_type: {self.sector_type}. Must be 'distance', 'time', or 'angle'.")
            
        return self.telemetry
        
    def find_fastest_drivers(self, drivers_telemetry_list):
        """
        Find the fastest driver in each mini-sector.
        
        Args:
            drivers_telemetry_list: List of telemetry data for different drivers
            
        Returns:
            tuple: (DataFrame with the fastest driver for each mini-sector, 
                   DataFrame with all processed telemetry data)
        """
        # Process each driver's telemetry to add mini-sectors
        processed_telemetry_list = []
        for telemetry in drivers_telemetry_list:
            # Create a copy to avoid modifying the original
            tel_copy = telemetry.copy()
            # Add mini-sectors based on distance
            tel_copy['MiniSector'] = pd.cut(
                tel_copy['Distance'], 
                self.num_sectors, 
                labels=False
            )
            processed_telemetry_list.append(tel_copy)
        
        # Combine all drivers' processed telemetry
        mini_sectors = pd.concat(processed_telemetry_list)
        
        # Calculate the time spent in each mini-sector for each driver
        time_spent = mini_sectors.groupby(['Driver', 'MiniSector']).apply(
            lambda df: df['Time'].diff().sum()
        ).reset_index().rename(columns={0: 'TimeSpent'})
        
        # Find the fastest driver in each mini-sector
        fastest_per_mini_sector = time_spent.loc[
            time_spent.groupby('MiniSector')['TimeSpent'].idxmin()
        ]
        
        return fastest_per_mini_sector, mini_sectors


class TelemetryService:
    """
    Service for processing and analyzing F1 telemetry data.
    """
    
    def __init__(self, session_service=None):
        """
        Initialize the telemetry service.
        
        Args:
            session_service: Optional SessionService instance for session caching
        """
        from services.session_service import SessionService
        self.session_service = session_service or SessionService
        
    def get_session(self, year, race, session_type):
        """
        Get a FastF1 session using the SessionService cache.
        
        Args:
            year: The year of the session
            race: The race name or round number
            session_type: The session type (e.g., 'R', 'Q', 'FP1')
            
        Returns:
            fastf1.core.Session: The loaded session
        """
        logger.info(f"Getting session data for {year} {race} {session_type}")
        return self.session_service.get_session(int(year), race, session_type)
        
    def get_driver_fastest_lap(self, session, driver):
        """
        Get the fastest lap for a driver.
        
        Args:
            session: The FastF1 session
            driver: The driver code
            
        Returns:
            fastf1.core.Lap: The fastest lap
        """
        return session.laps.pick_drivers(driver).pick_fastest()
        
    def get_speed_trace_data(self, session, driver1, driver2):
        """
        Get speed trace comparison data for two drivers.
        
        Args:
            session: The FastF1 session
            driver1: The first driver code
            driver2: The second driver code
            
        Returns:
            dict: Speed trace data for interactive visualization
        """
        driver1_lap = self.get_driver_fastest_lap(session, driver1)
        driver2_lap = self.get_driver_fastest_lap(session, driver2)
        
        # Get telemetry data
        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver2_tel = driver2_lap.get_car_data().add_distance()
        
        # Get driver colors using our custom color mapping
        driver_colors = get_color_mapping(session)['drivers']
        driver1_color = driver_colors.get(driver1, 'white')
        driver2_color = driver_colors.get(driver2, 'white')
        
        # Get lap times for display
        driver1_time = str(driver1_lap["LapTime"])[11:19]  # Format as MM:SS.sss
        driver2_time = str(driver2_lap["LapTime"])[11:19]
        
        # Get circuit info for corner markers
        circuit_info = session.get_circuit_info()
        
        # Return structured data
        return {
            "driver1": {
                "name": driver1,
                "color": driver1_color,
                "lapTime": driver1_time,
                "distance": driver1_tel['Distance'].tolist(),
                "speed": driver1_tel['Speed'].tolist(),
                "throttle": driver1_tel['Throttle'].tolist(),
                "brake": driver1_tel['Brake'].tolist() if 'Brake' in driver1_tel else None,
                "drs": driver1_tel['DRS'].tolist() if 'DRS' in driver1_tel else None
            },
            "driver2": {
                "name": driver2,
                "color": driver2_color,
                "lapTime": driver2_time,
                "distance": driver2_tel['Distance'].tolist(),
                "speed": driver2_tel['Speed'].tolist(),
                "throttle": driver2_tel['Throttle'].tolist(),
                "brake": driver2_tel['Brake'].tolist() if 'Brake' in driver2_tel else None,
                "drs": driver2_tel['DRS'].tolist() if 'DRS' in driver2_tel else None
            },
            "circuit": {
                "corners": [
                    {
                        "distance": float(corner['Distance']),
                        "number": int(corner['Number']),
                        "letter": str(corner['Letter'])
                    }
                    for _, corner in circuit_info.corners.iterrows()
                ]
            },
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
        
    def get_gear_shifts_data(self, session, driver):
        """
        Get gear shift data for a driver.
        
        Args:
            session: The FastF1 session
            driver: The driver code
            
        Returns:
            dict: Gear shift data for interactive visualization
        """
        lap = self.get_driver_fastest_lap(session, driver)
        tel = lap.get_telemetry()
        
        # Get driver colors using our custom color mapping
        driver_colors = get_color_mapping(session)['drivers']
        
        # Return structured data
        return {
            "driver": {
                "name": driver,
                "color": driver_colors.get(driver, 'white'),
                "lapTime": str(lap["LapTime"])[11:19]
            },
            "track": {
                "x": tel['X'].tolist(),
                "y": tel['Y'].tolist()
            },
            "gears": tel['nGear'].tolist(),
            "speed": tel['Speed'].tolist(),
            "distance": tel['Distance'].tolist() if 'Distance' in tel else None,
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
        
    def get_track_dominance_data(self, session, drivers, num_mini_sectors=config.DEFAULT_MINI_SECTORS):
        """
        Get track dominance data for drivers.
        
        Args:
            session: The FastF1 session
            drivers: List of driver codes
            num_mini_sectors: Number of mini-sectors to create
            
        Returns:
            dict: Track dominance data for interactive visualization
        """
        mini_sectors_list = []
        driver_info = {}
        
        # If no drivers specified, use the top 3 fastest
        if not drivers:
            laps = session.laps.pick_quicklaps()
            fastest_laps = laps.groupby('Driver')['LapTime'].min().sort_values().index[:3]
            drivers = fastest_laps.tolist()
        
        # Limit to 3 drivers for clarity
        drivers = drivers[:3]
        
        # Get telemetry data for each driver
        for driver in drivers:
            try:
                lap = self.get_driver_fastest_lap(session, driver)
                telemetry = lap.get_telemetry()
                telemetry['Driver'] = driver
                mini_sectors_list.append(telemetry)
                
                # Gather driver info
                driver_info[driver] = {
                    'DriverNumber': lap['DriverNumber'],
                    'DriverName': lap['Driver'],
                    'Sector1': lap['Sector1Time'],
                    'Sector2': lap['Sector2Time'],
                    'Sector3': lap['Sector3Time'],
                    'TeamColour': get_color_mapping(session)['drivers'].get(driver, 'white')
                }
            except Exception as e:
                logger.error(f"Error getting telemetry for driver {driver}: {e}")
        
        if not mini_sectors_list:
            logger.error("No valid telemetry data found for any driver")
            return {
                'track': {'x': [], 'y': []},
                'miniSectors': [],
                'drivers': [],
                'session': {
                    'name': session.event['EventName'],
                    'year': session.event.year
                }
            }
        
        # Create mini-sectors
        analyzer = MiniSectorAnalyzer(pd.concat(mini_sectors_list), num_mini_sectors)
        mini_sectors = analyzer.create_mini_sectors()
        
        # Find fastest driver per mini-sector and get all processed telemetry
        fastest_per_mini_sector, all_mini_sectors = analyzer.find_fastest_drivers(mini_sectors_list)
        
        # Get track coordinates from the first driver's lap
        lap = session.laps.pick_drivers(drivers[0]).pick_fastest()
        x = lap.telemetry['X'].values
        y = lap.telemetry['Y'].values
        
        # Create mini-sector data
        mini_sector_data = []
        for minisector in range(num_mini_sectors):
            try:
                # Get data for this mini-sector
                sector_data = all_mini_sectors[all_mini_sectors['MiniSector'] == minisector]
                
                if not sector_data.empty:
                    # Find the fastest driver for this mini-sector
                    fastest_driver_rows = fastest_per_mini_sector[
                        fastest_per_mini_sector['MiniSector'] == minisector
                    ]
                    
                    if not fastest_driver_rows.empty:
                        fastest_driver = fastest_driver_rows['Driver'].values[0]
                        
                        # Get only this driver's data for this mini-sector
                        driver_sector_data = sector_data[sector_data['Driver'] == fastest_driver]
                        
                        # Get coordinates for this mini-sector
                        if not driver_sector_data.empty and 'X' in driver_sector_data and 'Y' in driver_sector_data:
                            # Filter out any NaN values
                            valid_data = driver_sector_data.dropna(subset=['X', 'Y'])
                            
                            if not valid_data.empty:
                                sector_x = valid_data['X'].tolist()
                                sector_y = valid_data['Y'].tolist()
                                
                                # Get time spent in this mini-sector
                                time_spent = fastest_driver_rows['TimeSpent'].values[0]
                                
                                # Only add if we have valid coordinates
                                if sector_x and sector_y and len(sector_x) == len(sector_y) and not np.isnan(sector_x).any() and not np.isnan(sector_y).any():
                                    mini_sector_data.append({
                                        'id': int(minisector),
                                        'driver': str(fastest_driver),
                                        'color': get_driver_colors(session).get(fastest_driver, 'white'),
                                        'time': str(time_spent),
                                        'coordinates': {
                                            'x': sector_x,
                                            'y': sector_y
                                        }
                                    })
            except Exception as e:
                logger.error(f"Error processing mini-sector {minisector}: {e}")
        
        # Return structured data
        return {
            'track': {
                'x': x.tolist(),
                'y': y.tolist()
            },
            'miniSectors': mini_sector_data,
            'drivers': [
                {
                    'code': driver,
                    'name': info['DriverName'],
                    'number': info['DriverNumber'],
                    'color': info['TeamColour'],
                    'sector1': str(info['Sector1']),
                    'sector2': str(info['Sector2']),
                    'sector3': str(info['Sector3'])
                }
                for driver, info in driver_info.items()
            ],
            'session': {
                'name': session.event['EventName'],
                'year': session.event.year
            }
        }

    def get_all_laps(self, session):
        """
        Get all laps for a session.
        
        Args:
            session: The FastF1 session
            
        Returns:
            dict: All laps data for the session
        """
        if session.name in ['Qualifying', 'Sprint Qualifying']:
            laps = session.laps.pick_quicklaps()
        else:
            laps = session.laps
        
        # Format the response
        lap_data = []
        for _, row in laps.iterrows():
            lap_data.append({
                "lapNumber": int(row['LapNumber']),
                "driverCode": row['Driver'],
                "lapTime": row['LapTime'].total_seconds() if pd.notna(row['LapTime']) else None,
                "compound": row['Compound'],
                "tyreLife": row['TyreLife'],
                "freshTyre": row['FreshTyre'],
                "stint": row['Stint'],
                "sector1Time": row['Sector1Time'].total_seconds() if pd.notna(row['Sector1Time']) else None,
                "sector2Time": row['Sector2Time'].total_seconds() if pd.notna(row['Sector2Time']) else None,
                "sector3Time": row['Sector3Time'].total_seconds() if pd.notna(row['Sector3Time']) else None,
            })
            
        return {
            "laps": lap_data,
            "session": {
                "name": session.event['EventName'],
                "year": session.event.year
            }
        }
