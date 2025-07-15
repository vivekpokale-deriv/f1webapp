"""
Standalone F1 Telemetry Visualization Script

This script creates a standalone HTML file with telemetry visualizations for
Hamilton vs Verstappen at Bahrain 2023 Qualifying.

Usage:
    python standalone_telemetry.py

The script will generate an HTML file that can be opened in a browser to view
the visualizations and adjust their sizes.
"""

import os
import logging
import numpy as np
import pandas as pd
import fastf1
from fastf1 import plotting
from utils.color_mapping import get_driver_colors
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import base64
from io import BytesIO
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('f1_standalone')

# Setup FastF1
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')
fastf1.Cache.enable_cache('cache')  # Use the cache directory

# Constants
YEAR = 2023
RACE = "Bahrain"
SESSION_TYPE = "Q"  # Qualifying
DRIVER1 = "HAM"  # Hamilton
DRIVER2 = "VER"  # Verstappen
OUTPUT_FILE = "standalone_telemetry.html"
DEFAULT_MINI_SECTORS = 20

class MiniSectorAnalyzer:
    """
    Analyzer for creating and analyzing mini-sectors on a track.
    """
    
    def __init__(self, telemetry_data, num_sectors=DEFAULT_MINI_SECTORS, sector_type='distance'):
        """
        Initialize the mini-sector analyzer.
        
        Args:
            telemetry_data: The telemetry data to analyze
            num_sectors: Number of mini-sectors to create
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


class TelemetryVisualizer:
    """
    Class for generating telemetry visualizations.
    """
    
    def __init__(self):
        """Initialize the telemetry visualizer."""
        self.session = None
        self.driver1_lap = None
        self.driver2_lap = None
        self.driver1_tel = None
        self.driver2_tel = None
        self.driver1_color = None
        self.driver2_color = None
        
        # Create a session service for caching
        from services.session_service import SessionService
        self.session_service = SessionService(max_cache_size=5)  # Smaller cache for standalone script
        
    def load_session(self, year, race, session_type):
        """
        Load a FastF1 session.
        
        Args:
            year: The year of the session
            race: The race name or round number
            session_type: The session type (e.g., 'R', 'Q', 'FP1')
        """
        logger.info(f"Loading session data for {year} {race} {session_type}")
        self.session = self.session_service.get_session(int(year), race, session_type)
        
    def load_driver_data(self, driver1, driver2):
        """
        Load data for two drivers.
        
        Args:
            driver1: The first driver code
            driver2: The second driver code
        """
        logger.info(f"Loading driver data for {driver1} and {driver2}")
        # Use pick_drivers (plural) which is the newer API
        self.driver1_lap = self.session.laps.pick_drivers(driver1).pick_fastest()
        self.driver2_lap = self.session.laps.pick_drivers(driver2).pick_fastest()
        
        # Get telemetry data
        self.driver1_tel = self.driver1_lap.get_car_data().add_distance()
        self.driver2_tel = self.driver2_lap.get_car_data().add_distance()
        
        # Get driver colors using our custom color mapping
        driver_colors = get_driver_colors(self.session)
        self.driver1_color = driver_colors.get(driver1, 'blue')
        self.driver2_color = driver_colors.get(driver2, 'red')
        
    def create_speed_trace_plot(self):
        """
        Create a speed trace comparison plot for two drivers.
        
        Returns:
            str: Base64-encoded PNG image
        """
        logger.info("Creating speed trace plot")
        
        # Get lap times for display
        driver1_time = str(self.driver1_lap["LapTime"])[11:19]  # Format as MM:SS.sss
        driver2_time = str(self.driver2_lap["LapTime"])[11:19]
        
        # Get circuit info for corner markers
        circuit_info = self.session.get_circuit_info()
        v_min = min(self.driver1_tel['Speed'].min(), self.driver2_tel['Speed'].min())
        v_max = max(self.driver1_tel['Speed'].max(), self.driver2_tel['Speed'].max())
        
        # Create plot with two subplots (speed and throttle)
        fig, ax = plt.subplots(2, figsize=(12, 8), gridspec_kw={'height_ratios': [10, 3]})
        
        # Speed plot
        ax[0].plot(self.driver1_tel['Distance'], self.driver1_tel['Speed'], 
                  color=self.driver1_color, label=f"{DRIVER1} - {driver1_time}")
        ax[0].plot(self.driver2_tel['Distance'], self.driver2_tel['Speed'], 
                  color=self.driver2_color, label=f"{DRIVER2} - {driver2_time}")
        
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
        ax[1].plot(self.driver1_tel['Distance'], self.driver1_tel['Throttle'], 
                  color=self.driver1_color, label=f"{DRIVER1}")
        ax[1].plot(self.driver2_tel['Distance'], self.driver2_tel['Throttle'], 
                  color=self.driver2_color, label=f"{DRIVER2}")
        ax[1].set_ylabel('Throttle %')
        ax[1].legend()
        
        # Title
        plt.suptitle(f"Fastest Lap Comparison\n"
                    f"{self.session.event['EventName']} {self.session.event.year}")
        
        # Save to BytesIO and convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
        
    def create_gear_shifts_plot(self, driver, driver_color):
        """
        Create a gear shift visualization plot.
        
        Args:
            driver: The driver code
            driver_color: The color to use for the driver
            
        Returns:
            str: Base64-encoded PNG image
        """
        logger.info(f"Creating gear shifts plot for {driver}")
        
        lap = self.session.laps.pick_drivers(driver).pick_fastest()
        tel = lap.get_telemetry()
        
        x = np.array(tel['X'].values)
        y = np.array(tel['Y'].values)
        
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        gear = tel['nGear'].to_numpy().astype(float)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        cmap = plt.get_cmap('Paired')
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N + 1), cmap=cmap)
        lc_comp.set_array(gear)
        lc_comp.set_linewidth(4)
        
        ax.add_collection(lc_comp)
        ax.axis('equal')
        ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)
        
        ax.set_title(
            f"Gear Shifts: {driver}\n"
            f"{self.session.event['EventName']} {self.session.event.year}"
        )
        
        cbar = plt.colorbar(mappable=lc_comp, ax=ax, label="Gear", boundaries=np.arange(1, 10))
        cbar.set_ticks(np.arange(1.5, 9.5))
        cbar.set_ticklabels(np.arange(1, 9))
        
        # Save to BytesIO and convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
        
    def create_track_dominance_plot(self, drivers, num_mini_sectors=DEFAULT_MINI_SECTORS):
        """
        Create a track dominance visualization showing which driver is fastest in each mini-sector.
        
        Args:
            drivers: List of driver codes
            num_mini_sectors: Number of mini-sectors to create
            
        Returns:
            str: Base64-encoded PNG image
        """
        logger.info(f"Creating track dominance plot for {drivers}")
        
        mini_sectors_list = []
        driver_info = {}
        
        # Get telemetry data for each driver
        for driver in drivers:
            try:
                lap = self.session.laps.pick_drivers(driver).pick_fastest()
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
                    'TeamColour': get_driver_colors(self.session).get(driver, 'white')
                }
            except Exception as e:
                logger.error(f"Error getting telemetry for driver {driver}: {e}")
        
        if not mini_sectors_list:
            logger.error("No valid telemetry data found for any driver")
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, "No valid telemetry data found", ha='center', va='center')
            
            # Save to BytesIO and convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100)
            plt.close(fig)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode('utf-8')
        
        # Create mini-sectors
        analyzer = MiniSectorAnalyzer(pd.concat(mini_sectors_list), num_mini_sectors)
        mini_sectors = analyzer.create_mini_sectors()
        
        # Find fastest driver per mini-sector and get all processed telemetry
        fastest_per_mini_sector, all_mini_sectors = analyzer.find_fastest_drivers(mini_sectors_list)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Get track map from the first driver's lap
        lap = self.session.laps.pick_drivers(drivers[0]).pick_fastest()
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
                                    color = get_driver_colors(self.session).get(fastest_driver, 'white')
                                    
                                    # Create a line collection for this mini-sector
                                    lc = LineCollection(segment_points, colors=[color], linewidth=5)
                                    ax.add_collection(lc)
            except Exception as e:
                logger.error(f"Error visualizing mini-sector {minisector}: {e}")
        
        # Add legend
        for driver in drivers:
            ax.plot([], [], color=get_driver_colors(self.session).get(driver, 'white'), label=driver)
        
        ax.legend()
        ax.set_title(f"{self.session.event.year} {self.session.event['EventName']} - Track Dominance by Mini-Sectors", 
                    color='white')
        ax.axis('off')
        ax.set_aspect('equal')
        
        # Save to BytesIO and convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, facecolor=fig.get_facecolor())
        plt.close(fig)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')


def generate_html_file(speed_trace_img, gear_shifts_img1, gear_shifts_img2, track_dominance_img):
    """
    Generate an HTML file with the visualizations.
    
    Args:
        speed_trace_img: Base64-encoded speed trace image
        gear_shifts_img1: Base64-encoded gear shifts image for driver 1
        gear_shifts_img2: Base64-encoded gear shifts image for driver 2
        track_dominance_img: Base64-encoded track dominance image
        
    Returns:
        str: Path to the generated HTML file
    """
    logger.info("Generating HTML file")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>F1 Telemetry Visualization - {RACE} {YEAR} {SESSION_TYPE}</title>
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .header {{
            background-color: #e10600;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            overflow: hidden;
        }}
        .card-header {{
            background-color: #15151e;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-body {{
            padding: 20px;
        }}
        .visualization-container {{
            position: relative;
            margin-bottom: 20px;
            text-align: center;
        }}
        .visualization-img {{
            max-width: 100%;
            height: auto;
        }}
        .controls {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .control-group {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        input[type="number"] {{
            width: 60px;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        button {{
            background-color: #e10600;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #c10500;
        }}
        .footer {{
            background-color: #15151e;
            color: white;
            padding: 20px 0;
            margin-top: 30px;
            text-align: center;
        }}
        .row {{
            display: flex;
            flex-wrap: wrap;
            margin: 0 -15px;
        }}
        .col-6 {{
            flex: 0 0 50%;
            max-width: 50%;
            padding: 0 15px;
            box-sizing: border-box;
        }}
        @media (max-width: 768px) {{
            .col-6 {{
                flex: 0 0 100%;
                max-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>F1 Telemetry Visualization</h1>
            <p>{RACE} {YEAR} {SESSION_TYPE} - {DRIVER1} vs {DRIVER2}</p>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <div class="card-header">
                <span>Speed Trace</span>
                <div class="controls">
                    <div class="control-group">
                        <label for="speed-trace-height">Height:</label>
                        <input type="number" id="speed-trace-height" value="450" min="200" max="800">
                    </div>
                    <button onclick="updateVisualizationSize('speed-trace')">Apply</button>
                </div>
            </div>
            <div class="card-body">
                <div class="visualization-container" id="speed-trace-container" style="height: 450px;">
                    <img src="data:image/png;base64,{speed_trace_img}" alt="Speed Trace" class="visualization-img" id="speed-trace-img">
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-6">
                <div class="card">
                    <div class="card-header">
                        <span>Gear Shifts - {DRIVER1}</span>
                        <div class="controls">
                            <div class="control-group">
                                <label for="gear-shifts1-height">Height:</label>
                                <input type="number" id="gear-shifts1-height" value="350" min="200" max="600">
                            </div>
                            <button onclick="updateVisualizationSize('gear-shifts1')">Apply</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="visualization-container" id="gear-shifts1-container" style="height: 350px;">
                            <img src="data:image/png;base64,{gear_shifts_img1}" alt="Gear Shifts - {DRIVER1}" class="visualization-img" id="gear-shifts1-img">
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <div class="card">
                    <div class="card-header">
                        <span>Gear Shifts - {DRIVER2}</span>
                        <div class="controls">
                            <div class="control-group">
                                <label for="gear-shifts2-height">Height:</label>
                                <input type="number" id="gear-shifts2-height" value="350" min="200" max="600">
                            </div>
                            <button onclick="updateVisualizationSize('gear-shifts2')">Apply</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="visualization-container" id="gear-shifts2-container" style="height: 350px;">
                            <img src="data:image/png;base64,{gear_shifts_img2}" alt="Gear Shifts - {DRIVER2}" class="visualization-img" id="gear-shifts2-img">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span>Track Dominance</span>
                <div class="controls">
                    <div class="control-group">
                        <label for="track-dominance-height">Height:</label>
                        <input type="number" id="track-dominance-height" value="500" min="300" max="800">
                    </div>
                    <button onclick="updateVisualizationSize('track-dominance')">Apply</button>
                </div>
            </div>
            <div class="card-body">
                <div class="visualization-container" id="track-dominance-container" style="height: 500px;">
                    <img src="data:image/png;base64,{track_dominance_img}" alt="Track Dominance" class="visualization-img" id="track-dominance-img">
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} F1 Telemetry Visualization</p>
        </div>
    </div>

    <script>
        function updateVisualizationSize(id) {{
            const container = document.getElementById(`${{id}}-container`);
            const height = document.getElementById(`${{id}}-height`).value;
            
            if (container && height) {{
                container.style.height = `${{height}}px`;
            }}
        }}
    </script>
</body>
</html>
"""
    
    # Write the HTML file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html_content)
    
    return OUTPUT_FILE


def main():
    """Main function to run the script."""
    try:
        logger.info(f"Starting telemetry visualization for {RACE} {YEAR} {SESSION_TYPE} - {DRIVER1} vs {DRIVER2}")
        
        # Create visualizer
        visualizer = TelemetryVisualizer()
        
        # Load session and driver data
        visualizer.load_session(YEAR, RACE, SESSION_TYPE)
        visualizer.load_driver_data(DRIVER1, DRIVER2)
        
        # Create visualizations
        speed_trace_img = visualizer.create_speed_trace_plot()
        gear_shifts_img1 = visualizer.create_gear_shifts_plot(DRIVER1, visualizer.driver1_color)
        gear_shifts_img2 = visualizer.create_gear_shifts_plot(DRIVER2, visualizer.driver2_color)
        track_dominance_img = visualizer.create_track_dominance_plot([DRIVER1, DRIVER2])
        
        # Generate HTML file
        output_file = generate_html_file(
            speed_trace_img, 
            gear_shifts_img1, 
            gear_shifts_img2, 
            track_dominance_img
        )
        
        logger.info(f"Telemetry visualization completed. Output file: {output_file}")
        print(f"Telemetry visualization completed. Open {output_file} in a web browser to view.")
        
    except Exception as e:
        logger.error(f"Error generating telemetry visualization: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
