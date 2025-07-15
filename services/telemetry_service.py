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
from utils.color_mapping import get_driver_colors

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
        self.session_service = session_service or SessionService()
        
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
        driver_colors = get_driver_colors(session)
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
        
    def create_speed_trace_plot(self, session, driver1, driver2):
        """
        Create a speed trace comparison plot for two drivers.
        
        Args:
            session: The FastF1 session
            driver1: The first driver code
            driver2: The second driver code
            
        Returns:
            tuple: (figure, filename) - The matplotlib figure and the saved filename
        """
        driver1_lap = self.get_driver_fastest_lap(session, driver1)
        driver2_lap = self.get_driver_fastest_lap(session, driver2)
        
        # Get telemetry data
        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver2_tel = driver2_lap.get_car_data().add_distance()
        
        # Get driver colors using our custom color mapping
        driver_colors = get_driver_colors(session)
        driver1_color = driver_colors.get(driver1, 'white')
        driver2_color = driver_colors.get(driver2, 'white')
        
        # Get lap times for display
        driver1_time = str(driver1_lap["LapTime"])[11:19]  # Format as MM:SS.sss
        driver2_time = str(driver2_lap["LapTime"])[11:19]
        
        # Get circuit info for corner markers
        circuit_info = session.get_circuit_info()
        v_min = min(driver1_tel['Speed'].min(), driver2_tel['Speed'].min())
        v_max = max(driver1_tel['Speed'].max(), driver2_tel['Speed'].max())
        
        # Create plot with two subplots (speed and throttle)
        fig, ax = plt.subplots(2, figsize=config.DEFAULT_FIG_SIZE, 
                              gridspec_kw={'height_ratios': [10, 3]})
        
        # Speed plot
        ax[0].plot(driver1_tel['Distance'], driver1_tel['Speed'], 
                  color=driver1_color, label=f"{driver1} - {driver1_time}")
        ax[0].plot(driver2_tel['Distance'], driver2_tel['Speed'], 
                  color=driver2_color, label=f"{driver2} - {driver2_time}")
        
        # Add corner markers
        ax[0].vlines(x=circuit_info.corners['Distance'], 
                    ymin=v_min - 20, ymax=v_max + 10,
                    linestyles='dotted', colors='grey')
        
        # Add corner numbers with alternating positions to avoid overlap
        for i, (_, corner) in enumerate(circuit_info.corners.iterrows()):
            txt = f"{corner['Number']}{corner['Letter']}"
            # Alternate between top and bottom positions
            if i % 2 == 0:
                # Even index: place at bottom
                y_pos = v_min - 30
                va = 'center_baseline'
            else:
                # Odd index: place at top
                y_pos = v_max + 20
                va = 'center'
            
            ax[0].text(corner['Distance'], y_pos, txt,
                      va=va, ha='center', size='small', rotation=-90)
        
        ax[0].set_xlabel('Distance (m)')
        ax[0].set_ylabel('Speed (km/h)')
        ax[0].set_ylim([v_min - 40, v_max + 30])  # Increased upper limit for corner numbers
        ax[0].legend()
        
        # Throttle plot
        ax[1].plot(driver1_tel['Distance'], driver1_tel['Throttle'], 
                  color=driver1_color, label=f"{driver1}")
        ax[1].plot(driver2_tel['Distance'], driver2_tel['Throttle'], 
                  color=driver2_color, label=f"{driver2}")
        ax[1].set_ylabel('Throttle %')
        ax[1].legend()
        
        # Title
        plt.suptitle(f"Fastest Lap Comparison\n"
                    f"{session.event['EventName']} {session.event.year}")
        
        # Save and return
        filename = "plot.png"
        plt.savefig(filename)
        
        return fig, filename
        
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
        driver_colors = get_driver_colors(session)
        
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
        
    def create_gear_shifts_plot(self, session, driver, ax=None, show_title=True):
        """
        Create a gear shift visualization plot.
        
        Args:
            session: The FastF1 session
            driver: The driver code
            ax: Optional matplotlib axis to plot on
            show_title: Whether to show the title
            
        Returns:
            tuple: (figure, ax) - The matplotlib figure and axis
        """
        lap = self.get_driver_fastest_lap(session, driver)
        tel = lap.get_telemetry()
        
        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)
        
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        gear = tel['nGear'].to_numpy().astype(float)
        
        if ax is None:
            fig, ax = plt.subplots(figsize=config.DEFAULT_FIG_SIZE)
        else:
            fig = ax.figure
        
        cmap = plt.get_cmap('Paired')
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N + 1), cmap=cmap)
        lc_comp.set_array(gear)
        lc_comp.set_linewidth(4)
        
        ax.add_collection(lc_comp)
        ax.axis('equal')
        ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)
        
        if show_title:
            ax.set_title(
                f"Gear Shifts: {lap['Driver']}\n"
                f"{session.event['EventName']} {session.event.year}"
            )
        
        cbar = plt.colorbar(mappable=lc_comp, ax=ax, label="Gear", boundaries=np.arange(1, 10))
        cbar.set_ticks(np.arange(1.5, 9.5))
        cbar.set_ticklabels(np.arange(1, 9))
        
        return fig, ax
        
    def create_combined_visualization(self, session, driver1, driver2):
        """
        Create a combined visualization with speed trace, track dominance, and gear shifts.
        
        Args:
            session: The FastF1 session
            driver1: The first driver code
            driver2: The second driver code
            
        Returns:
            tuple: (figure, filename) - The matplotlib figure and the saved filename
        """
        # Create a figure with a grid layout
        fig = plt.figure(figsize=(20, 28))
        
        # Define grid layout with track dominance chart larger
        gs = fig.add_gridspec(3, 2, height_ratios=[8, 15, 5])
        
        # Speed trace plot (full width, top)
        speed_ax1 = fig.add_subplot(gs[0, 0:])
        
        # Get telemetry data
        driver1_lap = self.get_driver_fastest_lap(session, driver1)
        driver2_lap = self.get_driver_fastest_lap(session, driver2)
        
        driver1_tel = driver1_lap.get_car_data().add_distance()
        driver2_tel = driver2_lap.get_car_data().add_distance()
        
        # Get driver colors using our custom color mapping
        driver_colors = get_driver_colors(session)
        driver1_color = driver_colors.get(driver1, 'white')
        driver2_color = driver_colors.get(driver2, 'white')
        
        # Get lap times for display
        driver1_time = str(driver1_lap["LapTime"])[11:19]  # Format as MM:SS.sss
        driver2_time = str(driver2_lap["LapTime"])[11:19]
        
        # Get circuit info for corner markers
        circuit_info = session.get_circuit_info()
        v_min = min(driver1_tel['Speed'].min(), driver2_tel['Speed'].min())
        v_max = max(driver1_tel['Speed'].max(), driver2_tel['Speed'].max())
        
        # Speed plot
        speed_ax1.plot(driver1_tel['Distance'], driver1_tel['Speed'], 
                      color=driver1_color, label=f"{driver1} - {driver1_time}")
        speed_ax1.plot(driver2_tel['Distance'], driver2_tel['Speed'], 
                      color=driver2_color, label=f"{driver2} - {driver2_time}")
        
        # Add corner markers
        speed_ax1.vlines(x=circuit_info.corners['Distance'], 
                        ymin=v_min - 20, ymax=v_max + 10,
                        linestyles='dotted', colors='grey')
        
        # Add corner numbers with alternating positions to avoid overlap
        for i, (_, corner) in enumerate(circuit_info.corners.iterrows()):
            txt = f"{corner['Number']}{corner['Letter']}"
            # Alternate between top and bottom positions
            if i % 2 == 0:
                # Even index: place at bottom
                y_pos = v_min - 30
                va = 'center_baseline'
            else:
                # Odd index: place at top
                y_pos = v_max + 20
                va = 'center'
            
            speed_ax1.text(corner['Distance'], y_pos, txt,
                          va=va, ha='center', size='small', rotation=-90)
        
        speed_ax1.set_xlabel('Distance (m)')
        speed_ax1.set_ylabel('Speed (km/h)')
        speed_ax1.set_ylim([v_min - 40, v_max + 30])  # Increased upper limit for corner numbers
        speed_ax1.legend()
        speed_ax1.set_title(f"Speed Trace Comparison\n{session.event['EventName']} {session.event.year}")
        
        # Track dominance plot (full width, middle)
        track_ax = fig.add_subplot(gs[1, 0:])
        _, track_ax, _ = self.create_track_dominance_plot(
            session, [driver1, driver2], config.DEFAULT_MINI_SECTORS, track_ax
        )
        
        # Gear shifts plots (half width each, bottom)
        gear1_ax = fig.add_subplot(gs[2, 0])
        gear2_ax = fig.add_subplot(gs[2, 1])
        
        # Create gear shift plots
        _, gear1_ax = self.create_gear_shifts_plot(session, driver1, gear1_ax)
        _, gear2_ax = self.create_gear_shifts_plot(session, driver2, gear2_ax)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the combined visualization
        filename = "combined_visualization.png"
        plt.savefig(filename, bbox_inches='tight')
        
        return fig, filename
        
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
                    'TeamColour': get_driver_colors(session).get(driver, 'white')
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
        
    def create_track_dominance_plot(self, session, drivers, num_mini_sectors=config.DEFAULT_MINI_SECTORS, ax=None, show_title=True):
        """
        Create a track dominance visualization showing which driver is fastest in each mini-sector.
        
        Args:
            session: The FastF1 session
            drivers: List of driver codes
            num_mini_sectors: Number of mini-sectors to create
            ax: Optional matplotlib axis to plot on
            show_title: Whether to show the title
            
        Returns:
            tuple: (figure, ax, driver_info) - The matplotlib figure, axis, and driver info
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
        
        # Get driver colors using our custom color mapping
        driver_colors = get_driver_colors(session)
        
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
                    'TeamColour': driver_colors.get(driver, 'white')
                }
            except Exception as e:
                logger.error(f"Error getting telemetry for driver {driver}: {e}")
        
        if not mini_sectors_list:
            logger.error("No valid telemetry data found for any driver")
            if ax is None:
                fig, ax = plt.subplots(figsize=config.DEFAULT_FIG_SIZE)
                return fig, "track_dominance_minisectors.png", {}
            else:
                return ax.figure, ax, {}
        
        # Create mini-sectors
        analyzer = MiniSectorAnalyzer(pd.concat(mini_sectors_list), num_mini_sectors)
        mini_sectors = analyzer.create_mini_sectors()
        
        # Find fastest driver per mini-sector and get all processed telemetry
        fastest_per_mini_sector, all_mini_sectors = analyzer.find_fastest_drivers(mini_sectors_list)
        
        # Create the plot if axis not provided
        if ax is None:
            fig, ax = plt.subplots(figsize=config.DEFAULT_FIG_SIZE)
        else:
            fig = ax.figure
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Get track map from the first driver's lap
        lap = session.laps.pick_drivers(drivers[0]).pick_fastest()
        x = lap.telemetry['X'].values
        y = lap.telemetry['Y'].values
        
        # Plot the track outline
        ax.plot(x, y, color='black', linestyle='-', linewidth=16, zorder=0)
        
        # Create points and segments for coloring
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Color each mini-sector by fastest driver
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
                        
                        if not driver_sector_data.empty:
                            # Get valid segment indices
                            segment_indices = driver_sector_data.index
                            
                            if len(segment_indices) > 1:  # Need at least 2 points to form a segment
                                # Get the min and max indices, ensuring they're within bounds
                                min_idx = max(0, segment_indices.min())
                                max_idx = min(len(segments) - 1, segment_indices.max())
                                
                                if min_idx < max_idx:
                                    # Get the segment points for this mini-sector
                                    segment_points = segments[min_idx:max_idx]
                                    
                                    # Get the color for this driver
                                    color = driver_colors.get(fastest_driver, 'white')
                                    
                                    # Create a line collection for this mini-sector
                                    lc = LineCollection(segment_points, colors=[color], linewidth=5)
                                    ax.add_collection(lc)
            except Exception as e:
                logger.error(f"Error visualizing mini-sector {minisector}: {e}")
        
        # Add legend
        for driver in drivers:
            ax.plot([], [], color=driver_colors.get(driver, 'white'), label=driver)
        
        ax.legend()
        if show_title:
            ax.set_title(f"{session.event.year} {session.event['EventName']} - Track Dominance by Mini-Sectors", 
                        color='white')
        ax.axis('off')
        ax.set_aspect('equal')
        
        # Only save if this is a standalone plot
        if ax is None:
            filename = "track_dominance_minisectors.png"
            plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor())
            return fig, filename, driver_info
        else:
            return fig, ax, driver_info
