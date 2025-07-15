"""
Test script for the color_mapping module.
"""

import logging
import fastf1
from utils.color_mapping import (
    get_driver_colors,
    get_driver_color,
    get_team_color,
    get_driver_team_color,
    get_driver_color_safely
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_color_mapping')

# Enable FastF1 cache
fastf1.Cache.enable_cache('cache')

def test_color_functions():
    """Test all color mapping functions."""
    print("FastF1 version:", fastf1.__version__)
    
    # Test with a session
    print("\n=== Testing with session ===")
    try:
        session = fastf1.get_session(2023, 'Bahrain', 'R')
        session.load()
        print(f"Loaded session: {session.event['EventName']} {session.event.year}")
        
        # Test get_driver_colors with session
        driver_colors = get_driver_colors(session)
        print(f"Driver colors: {len(driver_colors)} drivers found")
        if driver_colors:
            print(f"Sample driver colors: {list(driver_colors.items())[:3]}")
        
        # Test get_driver_color for a specific driver
        driver = 'VER'
        color = get_driver_color(driver, session)
        print(f"Color for {driver}: {color}")
        
        # Test get_team_color
        team = 'Red Bull'
        team_color = get_team_color(team, session)
        print(f"Color for team {team}: {team_color}")
        
        # Test get_driver_team_color
        driver_team_color = get_driver_team_color(driver, team, session)
        print(f"Driver-team color for {driver}/{team}: {driver_team_color}")
        
        # Test get_driver_color_safely with valid driver
        safe_color = get_driver_color_safely(driver, session)
        print(f"Safe color for {driver}: {safe_color}")
        
        # Test get_driver_color_safely with invalid driver
        invalid_driver = 'XYZ'
        safe_color_invalid = get_driver_color_safely(invalid_driver, session, 'purple')
        print(f"Safe color for invalid driver {invalid_driver}: {safe_color_invalid}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")

if __name__ == "__main__":
    test_color_functions()
