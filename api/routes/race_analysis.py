"""
Race analysis routes for F1 Web App API.
"""

from flask import Blueprint, request, send_file
import logging
import os
from api.utils.response import success_response, error_response
from api.utils.error_handler import APIError, configure_error_handling
from services.session_service import SessionService
from services.race_analysis_service import RaceAnalysisService

# Create blueprint
race_analysis_bp = Blueprint('race_analysis', __name__)
logger = logging.getLogger('f1webapp')

# Configure error handling
configure_error_handling(race_analysis_bp)

# Create shared service instances for better caching
session_service = SessionService(max_cache_size=20)  # Increased cache size for API server
race_analysis_service = RaceAnalysisService(session_service=session_service)


@race_analysis_bp.route('/race-pace/<int:year>/<race>', methods=['GET'])
def get_race_pace(year, race):
    """
    Get race pace comparison data.
    
    Args:
        year: Year of the session
        race: Race name or round number
        
    Returns:
        JSON: Race pace data
    """
    try:
        # Get optional parameters
        num_drivers = request.args.get('drivers', default=10, type=int)
        
        logger.info(f"Getting race pace data for {year} {race} (top {num_drivers} drivers)")
        
        # Use the shared race_analysis_service instance
        session = race_analysis_service.get_session(year, race, 'R')
        data = race_analysis_service.get_race_pace_data(session, num_drivers)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting race pace data: {e}")
        return error_response(f"Error getting race pace data: {str(e)}", 500)


@race_analysis_bp.route('/team-pace/<int:year>/<race>', methods=['GET'])
def get_team_pace(year, race):
    """
    Get team pace comparison data.
    
    Args:
        year: Year of the session
        race: Race name or round number
        
    Returns:
        JSON: Team pace data
    """
    try:
        logger.info(f"Getting team pace data for {year} {race}")
        
        # Use the shared race_analysis_service instance
        session = race_analysis_service.get_session(year, race, 'R')
        data = race_analysis_service.get_team_pace_data(session)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting team pace data: {e}")
        return error_response(f"Error getting team pace data: {str(e)}", 500)


@race_analysis_bp.route('/lap-sections/<int:year>/<race>/<session>', methods=['GET'])
def get_lap_sections(year, race, session):
    """
    Get lap sections analysis data.
    
    Args:
        year: Year of the session
        race: Race name or round number
        session: Session type (e.g., 'R', 'Q', 'FP1')
        
    Returns:
        JSON: Lap sections data
    """
    try:
        # Get drivers from query parameters
        drivers = request.args.get('drivers', '')
        driver_list = drivers.split(',') if drivers else []
        
        logger.info(f"Getting lap sections data for {year} {race} {session} {driver_list}")
        
        # Use the shared race_analysis_service instance
        session_obj = race_analysis_service.get_session(year, race, session)
        data = race_analysis_service.get_lap_sections_data(session_obj, driver_list)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting lap sections data: {e}")
        return error_response(f"Error getting lap sections data: {str(e)}", 500)
