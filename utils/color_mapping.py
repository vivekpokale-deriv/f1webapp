"""
Utility module for handling F1 driver and team color mappings.

This module provides consistent color mappings for F1 drivers and teams,
with fallbacks to FastF1's color mapping when available.
"""

import logging
import fastf1
from fastf1 import plotting
from typing import Dict, Optional, Union

logger = logging.getLogger('f1webapp')

# Default team colors (2023-2024 season)
DEFAULT_TEAM_COLORS = {
    'Red Bull': '#0600EF',       # Red Bull Racing
    'Ferrari': '#DC0000',        # Ferrari
    'Mercedes': '#00D2BE',       # Mercedes
    'McLaren': '#FF8700',        # McLaren
    'Aston Martin': '#006F62',   # Aston Martin
    'Alpine': '#0090FF',         # Alpine
    'Williams': '#005AFF',       # Williams
    'RB': '#1E41FF',             # Racing Bulls (formerly AlphaTauri)
    'Sauber': '#900000',         # Sauber (formerly Alfa Romeo)
    'Haas': '#FFFFFF',           # Haas
    
    # Historical teams
    'AlphaTauri': '#2B4562',     # AlphaTauri (now Racing Bulls)
    'Alfa Romeo': '#900000',     # Alfa Romeo (now Sauber)
    'Racing Point': '#F596C8',   # Racing Point (now Aston Martin)
    'Renault': '#FFF500',        # Renault (now Alpine)
    'Toro Rosso': '#469BFF',     # Toro Rosso (now Racing Bulls)
    'Force India': '#F596C8',    # Force India (now Aston Martin)
    'Manor': '#323232',          # Manor (defunct)
    'Lotus': '#FFB800',          # Lotus (defunct)
    'Caterham': '#005030',       # Caterham (defunct)
    'Marussia': '#6E0000',       # Marussia (defunct)
    'HRT': '#B2945B',            # HRT (defunct)
    'Virgin': '#c10d23',         # Virgin (defunct)
    'Brawn': '#BFD447',          # Brawn GP (now Mercedes)
    'Toyota': '#EB0000',         # Toyota (defunct)
    'BMW Sauber': '#006EFF',     # BMW Sauber (now Sauber)
    'Honda': '#CC0000',          # Honda (defunct)
    'Super Aguri': '#E60012',    # Super Aguri (defunct)
    'Spyker': '#F07E12',         # Spyker (defunct)
    'Midland': '#D4271E',        # Midland (defunct)
    'Jordan': '#EFC829',         # Jordan (defunct)
    'BAR': '#F8C300',            # BAR (defunct)
    'Jaguar': '#358C75',         # Jaguar (now Red Bull)
    'Arrows': '#FC8F1F',         # Arrows (defunct)
    'Minardi': '#000000',        # Minardi (now Racing Bulls)
    'Prost': '#3277D4',          # Prost (defunct)
    'Benetton': '#72DFDB',       # Benetton (now Alpine)
    'Stewart': '#FFFFFF',        # Stewart (now Red Bull)
    'Tyrrell': '#3277D4',        # Tyrrell (defunct)
    'Forti': '#F7EF07',          # Forti (defunct)
    'Footwork': '#FC8F1F',       # Footwork (defunct)
    'Simtek': '#000000',         # Simtek (defunct)
    'Pacific': '#46698A',        # Pacific (defunct)
    'Larrousse': '#318CE7',      # Larrousse (defunct)
    'Ligier': '#318CE7',         # Ligier (defunct)
}

# Default driver colors (fallback when FastF1 doesn't provide them)
DEFAULT_DRIVER_COLORS = {
    # 2024 Drivers
    'VER': '#0600EF',  # Verstappen (Red Bull)
    'PER': '#0600EF',  # Perez (Red Bull)
    'LEC': '#DC0000',  # Leclerc (Ferrari)
    'SAI': '#DC0000',  # Sainz (Ferrari)
    'HAM': '#00D2BE',  # Hamilton (Mercedes)
    'RUS': '#00D2BE',  # Russell (Mercedes)
    'NOR': '#FF8700',  # Norris (McLaren)
    'PIA': '#FF8700',  # Piastri (McLaren)
    'ALO': '#006F62',  # Alonso (Aston Martin)
    'STR': '#006F62',  # Stroll (Aston Martin)
    'OCO': '#0090FF',  # Ocon (Alpine)
    'GAS': '#0090FF',  # Gasly (Alpine)
    'ALB': '#005AFF',  # Albon (Williams)
    'SAR': '#005AFF',  # Sargeant (Williams)
    'TSU': '#1E41FF',  # Tsunoda (RB)
    'RIC': '#1E41FF',  # Ricciardo (RB)
    'BOT': '#900000',  # Bottas (Sauber)
    'ZHO': '#900000',  # Zhou (Sauber)
    'MAG': '#FFFFFF',  # Magnussen (Haas)
    'HUL': '#FFFFFF',  # Hulkenberg (Haas)
    
    # Recent past drivers
    'VET': '#006F62',  # Vettel (Aston Martin)
    'RAI': '#900000',  # Raikkonen (Alfa Romeo)
    'GIO': '#900000',  # Giovinazzi (Alfa Romeo)
    'MSC': '#FFFFFF',  # Schumacher (Haas)
    'MAZ': '#FFFFFF',  # Mazepin (Haas)
    'KVY': '#2B4562',  # Kvyat (AlphaTauri)
    'GRO': '#FFFFFF',  # Grosjean (Haas)
    'KUB': '#900000',  # Kubica (Alfa Romeo)
}

def get_driver_color(driver_code: str, session: Optional[fastf1.core.Session] = None) -> str:
    """
    Get the color for a driver.
    
    Args:
        driver_code: The three-letter driver code
        session: Optional FastF1 session to get colors from
        
    Returns:
        str: Hex color code for the driver
    """
    try:
        # Try to get color from FastF1 if session is provided
        if session:
            try:
                # Try using get_driver_color_mapping first (newer FastF1 versions)
                driver_mapping = plotting.get_driver_color_mapping(session=session)
                if driver_code in driver_mapping:
                    return driver_mapping[driver_code]
            except (AttributeError, TypeError) as e:
                logger.debug(f"Could not use get_driver_color_mapping: {e}")
                
                # Try using driver_color directly (older FastF1 versions)
                try:
                    if hasattr(plotting, 'driver_color') and driver_code in plotting.driver_color:
                        return plotting.driver_color[driver_code]
                except Exception as e:
                    logger.debug(f"Could not use plotting.driver_color: {e}")
        
        # Fall back to our default mapping
        if driver_code in DEFAULT_DRIVER_COLORS:
            return DEFAULT_DRIVER_COLORS[driver_code]
        
        # If all else fails, return a default color
        logger.warning(f"No color found for driver {driver_code}, using default")
        return "#333333"
        
    except Exception as e:
        logger.error(f"Error getting driver color for {driver_code}: {e}")
        return "#333333"

def get_team_color(team_name: str, session: Optional[fastf1.core.Session] = None) -> str:
    """
    Get the color for a team.
    
    Args:
        team_name: The team name
        session: Optional FastF1 session to get colors from
        
    Returns:
        str: Hex color code for the team
    """
    try:
        # Try to get color from FastF1 if session is provided
        if session:
            try:
                # Try using get_team_color_mapping first (newer FastF1 versions)
                team_mapping = plotting.get_team_color_mapping(session=session)
                if team_name in team_mapping:
                    return team_mapping[team_name]
            except (AttributeError, TypeError) as e:
                logger.debug(f"Could not use get_team_color_mapping: {e}")
                
                # Try using team_color directly (older FastF1 versions)
                try:
                    if hasattr(plotting, 'team_color') and team_name in plotting.team_color:
                        return plotting.team_color[team_name]
                except Exception as e:
                    logger.debug(f"Could not use plotting.team_color: {e}")
        
        # Fall back to our default mapping
        if team_name in DEFAULT_TEAM_COLORS:
            return DEFAULT_TEAM_COLORS[team_name]
        
        # If all else fails, return a default color
        logger.warning(f"No color found for team {team_name}, using default")
        return "#333333"
        
    except Exception as e:
        logger.error(f"Error getting team color for {team_name}: {e}")
        return "#333333"

def get_color_mapping(session: Optional[fastf1.core.Session] = None) -> Dict[str, Dict[str, str]]:
    """
    Get a complete mapping of driver and team colors.
    
    Args:
        session: Optional FastF1 session to get colors from
        
    Returns:
        dict: Dictionary with 'drivers' and 'teams' color mappings
    """
    driver_colors = {}
    team_colors = {}
    
    # If session is provided, try to get colors from FastF1
    if session:
        try:
            # Get driver colors
            try:
                driver_mapping = plotting.get_driver_color_mapping(session=session)
                driver_colors.update(driver_mapping)
            except (AttributeError, TypeError):
                if hasattr(plotting, 'driver_color'):
                    driver_colors.update(plotting.driver_color)
            
            # Get team colors
            try:
                team_mapping = plotting.get_team_color_mapping(session=session)
                team_colors.update(team_mapping)
            except (AttributeError, TypeError):
                if hasattr(plotting, 'team_color'):
                    team_colors.update(plotting.team_color)
        except Exception as e:
            logger.error(f"Error getting color mappings from FastF1: {e}")
    
    # Add our default mappings for any missing entries
    for driver, color in DEFAULT_DRIVER_COLORS.items():
        if driver not in driver_colors:
            driver_colors[driver] = color
    
    for team, color in DEFAULT_TEAM_COLORS.items():
        if team not in team_colors:
            team_colors[team] = color
    
    return {
        'drivers': driver_colors,
        'teams': team_colors
    }
