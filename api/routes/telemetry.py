"""
Telemetry routes for F1 Web App API.
"""

from flask import Blueprint, request
import logging
from api.utils.response import success_response, error_response
from api.utils.error_handler import APIError, configure_error_handling
from services.session_service import SessionService
from services.telemetry_service import TelemetryService

# Create blueprint
telemetry_bp = Blueprint('telemetry', __name__)
logger = logging.getLogger('f1webapp')

# Configure error handling
configure_error_handling(telemetry_bp)

# Create shared service instances for better caching
telemetry_service = TelemetryService()


@telemetry_bp.route('/speed-trace/<int:year>/<race>/<session>/<driver1>/<driver2>', methods=['GET'])
def get_speed_trace(year, race, session, driver1, driver2):
    """
    Get speed trace comparison data for two drivers.
    
    Args:
        year: Year of the session
        race: Race name or round number
        session: Session type (e.g., 'R', 'Q', 'FP1')
        driver1: First driver code
        driver2: Second driver code
        
    Returns:
        JSON: Speed trace data
    """
    try:
        logger.info(f"Getting speed trace data for {year} {race} {session} {driver1} vs {driver2}")
        
        # Use the shared telemetry service instance
        session_obj = telemetry_service.get_session(year, race, session)
        data = telemetry_service.get_speed_trace_data(session_obj, driver1, driver2)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting speed trace data: {e}")
        return error_response(f"Error getting speed trace data: {str(e)}", 500)


@telemetry_bp.route('/gear-shifts/<int:year>/<race>/<session>/<driver>', methods=['GET'])
def get_gear_shifts(year, race, session, driver):
    """
    Get gear shift data for a driver.
    
    Args:
        year: Year of the session
        race: Race name or round number
        session: Session type (e.g., 'R', 'Q', 'FP1')
        driver: Driver code
        
    Returns:
        JSON: Gear shift data
    """
    try:
        logger.info(f"Getting gear shift data for {year} {race} {session} {driver}")
        
        # Use the shared telemetry service instance
        session_obj = telemetry_service.get_session(year, race, session)
        data = telemetry_service.get_gear_shifts_data(session_obj, driver)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting gear shift data: {e}")
        return error_response(f"Error getting gear shift data: {str(e)}", 500)


@telemetry_bp.route('/track-dominance/<int:year>/<race>/<session>', methods=['GET'])
def get_track_dominance(year, race, session):
    """
    Get track dominance data for drivers.
    
    Args:
        year: Year of the session
        race: Race name or round number
        session: Session type (e.g., 'R', 'Q', 'FP1')
        
    Returns:
        JSON: Track dominance data
    """
    try:
        # Get drivers from query parameters
        drivers = request.args.get('drivers', '')
        driver_list = drivers.split(',') if drivers else []
        
        logger.info(f"Getting track dominance data for {year} {race} {session} {driver_list}")
        
        # Use the shared telemetry service instance
        session_obj = telemetry_service.get_session(year, race, session)
        data = telemetry_service.get_track_dominance_data(session_obj, driver_list)
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting track dominance data: {e}")
        return error_response(f"Error getting track dominance data: {str(e)}", 500)


# Session picker routes


@telemetry_bp.route('/session-laps/<int:year>/<race>/<session>', methods=['GET'])
def get_session_laps(year, race, session):
    """
    Get all laps for a given session.
    
    Args:
        year: The year of the session
        race: The name of the event
        session: The session type code
        
    Returns:
        JSON: List of laps
    """
    try:
        logger.info(f"Getting all laps for {year} {race} {session}")
        
        # Use the shared telemetry service instance
        session_obj = telemetry_service.get_session(year, race, session)
        laps = telemetry_service.get_all_laps(session_obj)
        
        return success_response(laps)
        
    except Exception as e:
        logger.error(f"Error getting all laps for {year} {race} {session}: {e}")
        return error_response(f"Error getting all laps for {year} {race} {session}: {str(e)}", 500)
