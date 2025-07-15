"""
Utility functions for handling driver and team colors in the F1 Web App.

This module provides a thin wrapper around FastF1's color functions with
error handling to ensure consistent behavior.
"""

import logging
import fastf1
from fastf1 import plotting

logger = logging.getLogger('f1webapp')

def get_driver_colors(session):
    """
    Get a mapping of driver codes to colors.
    
    Args:
        session: FastF1 session object (required)
        
    Returns:
        dict: Mapping of driver codes to color hex strings
    """
    try:
        return plotting.get_driver_color_mapping(session)
    except Exception as e:
        logger.error(f"Error getting driver colors: {e}")
        return {}

def get_driver_color(driver_code, session):
    """
    Get the color for a specific driver.
    
    Args:
        driver_code: Three-letter driver code (e.g., 'VER', 'HAM')
        session: FastF1 session object (required)
        
    Returns:
        str: Color hex string or 'white' if not found
    """
    try:
        return plotting.get_driver_color(driver_code, session)
    except Exception as e:
        logger.error(f"Error getting color for driver {driver_code}: {e}")
        return 'white'

def get_team_color(team_name, session):
    """
    Get the color for a specific team.
    
    Args:
        team_name: Team name (e.g., 'Red Bull', 'Ferrari')
        session: FastF1 session object (required)
        
    Returns:
        str: Color hex string or 'white' if not found
    """
    try:
        return plotting.get_team_color(team_name, session)
    except Exception as e:
        logger.error(f"Error getting color for team {team_name}: {e}")
        return 'white'

def get_driver_team_color(driver_code, team_name, session):
    """
    Get the color for a driver, falling back to team color if driver color is not found.
    
    Args:
        driver_code: Three-letter driver code (e.g., 'VER', 'HAM')
        team_name: Team name (e.g., 'Red Bull', 'Ferrari')
        session: FastF1 session object (required)
        
    Returns:
        str: Color hex string
    """
    try:
        return plotting.get_driver_color(driver_code, session)
    except Exception:
        try:
            return plotting.get_team_color(team_name, session)
        except Exception:
            return 'white'

def get_driver_color_safely(driver_code, session, default_color='white'):
    """
    Get the color for a specific driver with a safe fallback.
    
    Args:
        driver_code: Three-letter driver code (e.g., 'VER', 'HAM')
        session: FastF1 session object (required)
        default_color: Color to use if driver color is not found
        
    Returns:
        str: Color hex string
    """
    try:
        return plotting.get_driver_color(driver_code, session)
    except Exception:
        return default_color
