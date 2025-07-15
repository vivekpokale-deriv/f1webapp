"""
Information routes for F1 Web App API.
"""

from flask import Blueprint, request
import logging
from api.utils.response import success_response, error_response
from api.utils.error_handler import APIError, configure_error_handling

# Create blueprint
info_bp = Blueprint('info', __name__)
logger = logging.getLogger('f1webapp')

# Configure error handling
configure_error_handling(info_bp)


@info_bp.route('/drivers', methods=['GET'])
def get_driver_standings():
    """
    Get driver standings.
    
    Query Parameters:
        year: Optional year to get standings for
        
    Returns:
        JSON: Driver standings data
    """
    try:
        # Get optional year parameter
        year = request.args.get('year', default=None, type=int)
        
        logger.info(f"Getting driver standings for year: {year if year else 'current'}")
        
        # TODO: Import and use StandingsService to get data
        # from services.standings_service import StandingsService
        # standings_service = StandingsService()
        # standings = standings_service.get_driver_standings(year)
        
        # For now, return dummy data
        data = {
            "year": year if year else 2025,
            "standings": [
                {
                    "position": 1,
                    "driver": {
                        "code": "VER",
                        "name": "Max Verstappen",
                        "number": 1
                    },
                    "team": "Red Bull Racing",
                    "points": 250
                },
                {
                    "position": 2,
                    "driver": {
                        "code": "HAM",
                        "name": "Lewis Hamilton",
                        "number": 44
                    },
                    "team": "Mercedes",
                    "points": 220
                }
            ]
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting driver standings: {e}")
        return error_response(f"Error getting driver standings: {str(e)}", 500)


@info_bp.route('/constructors', methods=['GET'])
def get_constructor_standings():
    """
    Get constructor standings.
    
    Query Parameters:
        year: Optional year to get standings for
        
    Returns:
        JSON: Constructor standings data
    """
    try:
        # Get optional year parameter
        year = request.args.get('year', default=None, type=int)
        
        logger.info(f"Getting constructor standings for year: {year if year else 'current'}")
        
        # TODO: Import and use StandingsService to get data
        # For now, return dummy data
        data = {
            "year": year if year else 2025,
            "standings": [
                {
                    "position": 1,
                    "team": "Red Bull Racing",
                    "points": 400
                },
                {
                    "position": 2,
                    "team": "Mercedes",
                    "points": 350
                }
            ]
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting constructor standings: {e}")
        return error_response(f"Error getting constructor standings: {str(e)}", 500)


@info_bp.route('/next-event', methods=['GET'])
def get_next_event():
    """
    Get the next upcoming F1 event.
    
    Returns:
        JSON: Next event data
    """
    try:
        logger.info("Getting next event")
        
        # TODO: Import and use ScheduleService to get data
        # from services.schedule_service import ScheduleService
        # schedule_service = ScheduleService()
        # schedule_service.load_schedule()
        # next_event = schedule_service.get_next_event()
        
        # For now, return dummy data
        data = {
            "race": {
                "name": "British Grand Prix",
                "location": "Silverstone",
                "country": "United Kingdom",
                "flagUrl": "https://example.com/flags/gb.png"
            },
            "events": [
                {
                    "type": "Practice 1",
                    "startTime": "2025-07-18T11:30:00Z"
                },
                {
                    "type": "Practice 2",
                    "startTime": "2025-07-18T15:00:00Z"
                },
                {
                    "type": "Practice 3",
                    "startTime": "2025-07-19T10:30:00Z"
                },
                {
                    "type": "Qualifying",
                    "startTime": "2025-07-19T14:00:00Z"
                },
                {
                    "type": "Race",
                    "startTime": "2025-07-20T14:00:00Z"
                }
            ]
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting next event: {e}")
        return error_response(f"Error getting next event: {str(e)}", 500)


@info_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """
    Get the F1 schedule.
    
    Query Parameters:
        year: Optional year to get schedule for
        
    Returns:
        JSON: Schedule data
    """
    try:
        # Get optional year parameter
        year = request.args.get('year', default=None, type=int)
        
        logger.info(f"Getting schedule for year: {year if year else 'current'}")
        
        # TODO: Import and use ScheduleService to get data
        # For now, return dummy data
        data = {
            "year": year if year else 2025,
            "races": [
                {
                    "round": 1,
                    "name": "Bahrain Grand Prix",
                    "location": "Sakhir",
                    "country": "Bahrain",
                    "flagUrl": "https://example.com/flags/bh.png",
                    "events": [
                        {
                            "type": "Practice 1",
                            "startTime": "2025-03-01T11:30:00Z"
                        },
                        {
                            "type": "Practice 2",
                            "startTime": "2025-03-01T15:00:00Z"
                        },
                        {
                            "type": "Practice 3",
                            "startTime": "2025-03-02T12:30:00Z"
                        },
                        {
                            "type": "Qualifying",
                            "startTime": "2025-03-02T16:00:00Z"
                        },
                        {
                            "type": "Race",
                            "startTime": "2025-03-03T15:00:00Z"
                        }
                    ]
                },
                {
                    "round": 2,
                    "name": "Saudi Arabian Grand Prix",
                    "location": "Jeddah",
                    "country": "Saudi Arabia",
                    "flagUrl": "https://example.com/flags/sa.png",
                    "events": [
                        {
                            "type": "Practice 1",
                            "startTime": "2025-03-08T13:30:00Z"
                        },
                        {
                            "type": "Practice 2",
                            "startTime": "2025-03-08T17:00:00Z"
                        },
                        {
                            "type": "Practice 3",
                            "startTime": "2025-03-09T13:30:00Z"
                        },
                        {
                            "type": "Qualifying",
                            "startTime": "2025-03-09T17:00:00Z"
                        },
                        {
                            "type": "Race",
                            "startTime": "2025-03-10T17:00:00Z"
                        }
                    ]
                }
            ]
        }
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        return error_response(f"Error getting schedule: {str(e)}", 500)
