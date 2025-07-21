"""
Utility API routes for the F1 Web App.
"""

from flask import Blueprint, request, jsonify
from api.utils.response import create_response
from utils.color_mapping import get_driver_color, get_team_color, get_color_mapping

# Create a Blueprint for utility routes
utils_bp = Blueprint('utils', __name__)

@utils_bp.route('/driver-color/<driver_code>', methods=['GET'])
def driver_color(driver_code):
    """
    Get the color for a specific driver.
    
    Args:
        driver_code: The three-letter code for the driver (e.g., 'VER', 'HAM')
        
    Query Parameters:
        year: Optional year to get historical colors
        
    Returns:
        JSON response with the driver's color
    """
    try:
        year = request.args.get('year', None)
        year = int(year) if year else None
        
        color = get_driver_color(driver_code, year)
        
        return create_response({
            'color': color,
            'driver': driver_code,
            'year': year
        })
    except Exception as e:
        return create_response(None, success=False, error=str(e))

@utils_bp.route('/team-color', methods=['GET'])
def team_color():
    """
    Get the color for a specific team.
    
    Query Parameters:
        team: The name of the team
        year: Optional year to get historical colors
        
    Returns:
        JSON response with the team's color
    """
    try:
        team = request.args.get('team', None)
        if not team:
            return create_response(None, success=False, error="Team parameter is required")
            
        year = request.args.get('year', None)
        year = int(year) if year else None
        
        color = get_team_color(team, year)
        
        return create_response({
            'color': color,
            'team': team,
            'year': year
        })
    except Exception as e:
        return create_response(None, success=False, error=str(e))

@utils_bp.route('/all-driver-colors', methods=['GET'])
def all_driver_colors():
    """
    Get colors for all drivers.
    
    Query Parameters:
        year: Optional year to get historical colors
        
    Returns:
        JSON response with all driver colors
    """
    try:
        year = request.args.get('year', None)
        year = int(year) if year else None
        
        # Get the color mapping
        color_mapping = get_color_mapping(year)
        
        # Extract driver colors
        driver_colors = {}
        for driver_code, color in color_mapping.get('drivers', {}).items():
            driver_colors[driver_code] = color
        
        return create_response({
            'colors': driver_colors,
            'year': year
        })
    except Exception as e:
        return create_response(None, success=False, error=str(e))

@utils_bp.route('/all-team-colors', methods=['GET'])
def all_team_colors():
    """
    Get colors for all teams.
    
    Query Parameters:
        year: Optional year to get historical colors
        
    Returns:
        JSON response with all team colors
    """
    try:
        year = request.args.get('year', None)
        year = int(year) if year else None
        
        # Get the color mapping
        color_mapping = get_color_mapping(year)
        
        # Extract team colors
        team_colors = {}
        for team_name, color in color_mapping.get('teams', {}).items():
            team_colors[team_name] = color
        
        return create_response({
            'colors': team_colors,
            'year': year
        })
    except Exception as e:
        return create_response(None, success=False, error=str(e))
