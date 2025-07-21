"""
API routes for F1 information data.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from services.schedule_service import ScheduleService
from services.standings_service import StandingsService
from api.utils.response import create_response

logger = logging.getLogger('f1webapp')

# Create Blueprint
info_bp = Blueprint('info', __name__)

# Initialize services
schedule_service = ScheduleService()
standings_service = StandingsService()

@info_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """
    Get the F1 schedule.
    
    Query Parameters:
        year (int, optional): The year to get the schedule for
        include_testing (bool, optional): Whether to include testing events
        
    Returns:
        JSON: Schedule data
    """
    try:
        year = request.args.get('year')
        include_testing = request.args.get('include_testing', 'false').lower() == 'true'
        
        if year:
            year = int(year)
            
        schedule_data = schedule_service.get_schedule(year, include_testing)
        return create_response(schedule_data)
    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/next-event', methods=['GET'])
def get_next_event():
    """
    Get the next upcoming F1 event.
    
    Returns:
        JSON: Next event data
    """
    try:
        next_event = schedule_service.get_next_event()
        return create_response(next_event)
    except Exception as e:
        logger.error(f"Error getting next event: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/drivers', methods=['GET'])
def get_drivers():
    """
    Get driver standings.
    
    Query Parameters:
        year (int, optional): The year to get the standings for
        
    Returns:
        JSON: Driver standings data
    """
    try:
        year = request.args.get('year')
        if year:
            year = int(year)
            
        driver_standings = standings_service.get_driver_standings(year)
        return create_response(driver_standings)
    except Exception as e:
        logger.error(f"Error getting driver standings: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/all-drivers', methods=['GET'])
def get_all_drivers():
    """
    Get all drivers for a given year.
    
    Query Parameters:
        year (int, optional): The year to get the drivers for
        
    Returns:
        JSON: List of drivers
    """
    try:
        year = request.args.get('year')
        if year:
            year = int(year)
            
        drivers = standings_service.get_all_drivers(year)
        return create_response(drivers)
    except Exception as e:
        logger.error(f"Error getting all drivers: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/races', methods=['GET'])
def get_races():
    """
    Get all races for a given year.
    
    Query Parameters:
        year (int, optional): The year to get the races for
        
    Returns:
        JSON: List of races
    """
    try:
        year = request.args.get('year')
        if year:
            year = int(year)
        
        schedule = schedule_service.get_schedule(year)
        return create_response(schedule)
    except Exception as e:
        logger.error(f"Error getting all races: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/constructors', methods=['GET'])
def get_constructors():
    """
    Get constructor standings.
    
    Query Parameters:
        year (int, optional): The year to get the standings for
        
    Returns:
        JSON: Constructor standings data
    """
    try:
        year = request.args.get('year')
        if year:
            year = int(year)
            
        constructor_standings = standings_service.get_constructor_standings(year)
        return create_response(constructor_standings)
    except Exception as e:
        logger.error(f"Error getting constructor standings: {e}")
        return create_response({"error": str(e)}, 500)

@info_bp.route('/events-by-status', methods=['GET'])
def get_events_by_status():
    """
    Get F1 events grouped by status (past, current, future).
    
    Query Parameters:
        year (int, optional): The year to get the events for
        
    Returns:
        JSON: Events grouped by status
    """
    try:
        year = request.args.get('year')
        if year:
            year = int(year)
        else:
            year = datetime.now().year
            
        # Get the schedule
        schedule_data = schedule_service.get_schedule(year)
        
        # Group events by status
        past_events = []
        current_events = []
        future_events = []
        
        now = datetime.now()
        
        for race in schedule_data.get('races', []):
            # Get the race date from the first event (usually FP1)
            events = race.get('events', [])
            if not events:
                continue
                
            # Sort events by start time
            events.sort(key=lambda x: x['startTime'])
            
            # Get the first and last event times
            first_event_time = datetime.fromisoformat(events[0]['startTime'])
            last_event_time = datetime.fromisoformat(events[-1]['startTime'])
            
            # Determine status based on event times
            if last_event_time < now - timedelta(days=1):
                race['status'] = 'past'
                past_events.append(race)
            elif first_event_time <= now + timedelta(days=2):
                race['status'] = 'current'
                current_events.append(race)
            else:
                race['status'] = 'future'
                future_events.append(race)
        
        return create_response({
            'year': year,
            'past': past_events,
            'current': current_events,
            'future': future_events
        })
    except Exception as e:
        logger.error(f"Error getting events by status: {e}")
        return create_response({"error": str(e)}, 500)
