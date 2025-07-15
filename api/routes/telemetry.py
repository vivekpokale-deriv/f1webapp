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
session_service = SessionService(max_cache_size=20)  # Increased cache size for API server
telemetry_service = TelemetryService(session_service=session_service)


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


@telemetry_bp.route('/combined/<int:year>/<race>/<session>/<driver1>/<driver2>', methods=['GET'])
def get_combined_visualization(year, race, session, driver1, driver2):
    """
    Get combined visualization with speed trace, track dominance, and gear shifts.
    
    Args:
        year: Year of the session
        race: Race name or round number
        session: Session type (e.g., 'R', 'Q', 'FP1')
        driver1: First driver code
        driver2: Second driver code
        
    Returns:
        JSON: Path to the combined visualization image
    """
    try:
        logger.info(f"Creating combined visualization for {year} {race} {session} {driver1} vs {driver2}")
        
        # Use the shared telemetry service instance
        session_obj = telemetry_service.get_session(year, race, session)
        
        # Create the combined visualization
        _, filename = telemetry_service.create_combined_visualization(session_obj, driver1, driver2)
        
        # Return the path to the image
        return success_response({
            "image_path": filename,
            "session": {
                "name": session_obj.event['EventName'],
                "year": session_obj.event.year
            },
            "drivers": [driver1, driver2]
        })
        
    except Exception as e:
        logger.error(f"Error creating combined visualization: {e}")
        return error_response(f"Error creating combined visualization: {str(e)}", 500)


# Session picker routes

@telemetry_bp.route('/years', methods=['GET'])
def get_available_years():
    """
    Get all available years from 2018 to present.
    
    Returns:
        JSON: List of available years
    """
    try:
        logger.info("Getting available years")
        
        # Use the shared session service instance
        years = session_service.get_available_years()
        
        return success_response({"years": years})
        
    except Exception as e:
        logger.error(f"Error getting available years: {e}")
        return error_response(f"Error getting available years: {str(e)}", 500)


@telemetry_bp.route('/events/<int:year>', methods=['GET'])
def get_events_for_year(year):
    """
    Get all events (races) for a specific year.
    
    Args:
        year: The year to get events for
        
    Returns:
        JSON: List of events
    """
    try:
        logger.info(f"Getting events for year {year}")
        
        # Use the shared session service instance
        events = session_service.get_events_for_year(year)
        
        return success_response({"events": events})
        
    except Exception as e:
        logger.error(f"Error getting events for year {year}: {e}")
        return error_response(f"Error getting events for year {year}: {str(e)}", 500)


@telemetry_bp.route('/sessions/<int:year>/<race>', methods=['GET'])
def get_session_types(year, race):
    """
    Get available session types for a specific event.
    
    Args:
        year: The year of the event
        race: The name of the event
        
    Returns:
        JSON: List of session types
    """
    try:
        logger.info(f"Getting session types for {year} {race}")
        
        # Use the shared session service instance
        sessions = session_service.get_session_types(year, race)
        
        return success_response({"sessions": sessions})
        
    except Exception as e:
        logger.error(f"Error getting session types for {year} {race}: {e}")
        return error_response(f"Error getting session types for {year} {race}: {str(e)}", 500)


@telemetry_bp.route('/drivers/<int:year>/<race>/<session>', methods=['GET'])
def get_drivers_in_session(year, race, session):
    """
    Get all drivers who participated in a specific session.
    
    Args:
        year: The year of the session
        race: The name of the event
        session: The session type code
        
    Returns:
        JSON: List of drivers
    """
    try:
        logger.info(f"Getting drivers for {year} {race} {session}")
        
        # Use the shared session service instance
        drivers = session_service.get_drivers_in_session(year, race, session)
        
        return success_response({"drivers": drivers})
        
    except Exception as e:
        logger.error(f"Error getting drivers for {year} {race} {session}: {e}")
        return error_response(f"Error getting drivers for {year} {race} {session}: {str(e)}", 500)


@telemetry_bp.route('/laps/<int:year>/<race>/<session>/<driver>', methods=['GET'])
def get_driver_laps(year, race, session, driver):
    """
    Get all laps for a specific driver in a session.
    
    Args:
        year: The year of the session
        race: The name of the event
        session: The session type code
        driver: The driver code
        
    Returns:
        JSON: List of laps
    """
    try:
        logger.info(f"Getting laps for {driver} in {year} {race} {session}")
        
        # Use the shared session service instance
        laps = session_service.get_driver_laps(year, race, session, driver)
        
        return success_response({"laps": laps})
        
    except Exception as e:
        logger.error(f"Error getting laps for {driver} in {year} {race} {session}: {e}")
        return error_response(f"Error getting laps for {driver} in {year} {race} {session}: {str(e)}", 500)
