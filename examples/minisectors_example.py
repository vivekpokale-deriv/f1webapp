"""
Example script demonstrating how to use mini-sectors with FastF1.

This script shows how to:
1. Load a session
2. Create mini-sectors
3. Find the fastest driver in each mini-sector
4. Visualize the results
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import fastf1
from fastf1 import plotting

# Add the parent directory to the path so we can import from the services package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.telemetry_service import MiniSectorAnalyzer

# Enable FastF1 cache
fastf1.Cache.enable_cache('cache')

# Set up plotting
fastf1.plotting.setup_mpl()

def main():
    """Main function to demonstrate mini-sectors."""
    # Load a session
    year = 2023
    race = 'Monaco'
    session_type = 'Q'
    
    print(f"Loading {year} {race} {session_type} session...")
    session = fastf1.get_session(year, race, session_type)
    session.load()
    
    # Get the fastest laps for the top 3 drivers
    print("Getting fastest laps for top drivers...")
    laps = session.laps.pick_quicklaps()
    fastest_laps = laps.groupby('Driver')['LapTime'].min().sort_values().index[:3]
    drivers = fastest_laps.tolist()
    
    print(f"Analyzing drivers: {', '.join(drivers)}")
    
    # Get telemetry data for each driver
    mini_sectors_list = []
    driver_info = {}
    
    for driver in drivers:
        lap = session.laps.pick_driver(driver).pick_fastest()
        telemetry = lap.get_telemetry()
        telemetry['Driver'] = driver
        mini_sectors_list.append(telemetry)
        
        # Gather driver info
        driver_info[driver] = {
            'DriverNumber': lap['DriverNumber'],
            'DriverName': lap['Driver'],
            'LapTime': lap['LapTime'],
            'TeamColor': fastf1.plotting.get_driver_color_mapping(session=session).get(driver, 'white')
        }
    
    # Create mini-sectors
    print("Creating mini-sectors...")
    num_mini_sectors = 20
    
    # Try different methods for creating mini-sectors
    methods = ['distance', 'time', 'angle']
    
    for method in methods:
        print(f"\nUsing {method}-based mini-sectors:")
        
        # Create a new figure for each method
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.suptitle(f"{year} {race} {session_type} - Track Dominance by Mini-Sectors ({method}-based)", 
                    fontsize=16)
        
        # Set background color
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Create mini-sectors using the specified method
        analyzer = MiniSectorAnalyzer(pd.concat(mini_sectors_list), num_mini_sectors, method)
        mini_sectors = analyzer.create_mini_sectors()
        
        # Find fastest driver per mini-sector
        fastest_per_mini_sector = analyzer.find_fastest_drivers(mini_sectors_list)
        
        # Get track map from the first driver's lap
        lap = session.laps.pick_driver(drivers[0]).pick_fastest()
        x = lap.telemetry['X'].values
        y = lap.telemetry['Y'].values
        
        # Plot the track outline
        ax.plot(x, y, color='white', linestyle='-', linewidth=16, zorder=0, alpha=0.5)
        
        # Create points and segments for coloring
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Color each mini-sector by fastest driver
        for minisector in range(num_mini_sectors):
            sector_data = mini_sectors[mini_sectors['MiniSector'] == minisector]
            if not sector_data.empty:
                fastest_driver = fastest_per_mini_sector[
                    fastest_per_mini_sector['MiniSector'] == minisector
                ]['Driver'].values[0]
                color = fastf1.plotting.get_driver_color_mapping(session=session).get(fastest_driver, 'white')
                
                # Get indices for this mini-sector
                sector_indices = sector_data.index
                if len(sector_indices) > 1:
                    segment_points = segments[sector_indices.min():sector_indices.max() + 1]
                    lc = LineCollection(segment_points, colors=[color], linewidth=5)
                    ax.add_collection(lc)
        
        # Add legend
        for driver in drivers:
            ax.plot([], [], color=fastf1.plotting.get_driver_color_mapping(session=session).get(driver, 'white'), 
                   label=f"{driver} - {driver_info[driver]['LapTime']}")
        
        ax.legend(loc='upper right', facecolor='black', labelcolor='white')
        ax.set_title(f"Mini-Sectors Method: {method}", color='white')
        ax.axis('off')
        ax.set_aspect('equal')
        
        # Save the plot
        filename = f"track_dominance_{method}.png"
        plt.savefig(filename, bbox_inches='tight', facecolor=fig.get_facecolor())
        print(f"Saved visualization to {filename}")
    
    print("\nDone! Check the generated PNG files for visualizations.")

if __name__ == "__main__":
    main()
