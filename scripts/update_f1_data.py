#!/usr/bin/env python3
"""
F1 Data Update Script

This script polls FastF1 for new session data and updates the cache.
It can be run periodically (e.g., weekly) to keep the data up-to-date.
It uses our custom SessionService for efficient caching and includes
performance optimizations.

Usage:
    python update_f1_data.py [--cache-dir CACHE_DIR]
"""

import os
import sys
import argparse
import logging
import time
import json
import gc
from datetime import datetime, timedelta
import fastf1

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.session_service import SessionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("f1_update.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('f1_update')

# Session priority mapping (higher number = higher priority)
SESSION_PRIORITY = {
    'R': 10,   # Race (highest priority)
    'Q': 9,    # Qualifying
    'S': 8,    # Sprint Race
    'SQ': 7,   # Sprint Qualifying
    'FP3': 6,  # Free Practice 3
    'FP2': 5,  # Free Practice 2
    'FP1': 4   # Free Practice 1 (lowest priority)
}

# Usage statistics
usage_stats = {
    'start_time': None,
    'end_time': None,
    'total_sessions': 0,
    'successful_sessions': 0,
    'failed_sessions': 0,
    'events_processed': 0,
    'memory_usage': 0,
    'session_types': {}
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Update F1 data cache')
    parser.add_argument('--cache-dir', type=str, default='cache',
                        help='Directory to store cached data (default: cache)')
    parser.add_argument('--lookback-days', type=int, default=14,
                        help='Number of days to look back for recent events (default: 14)')
    parser.add_argument('--lookahead-days', type=int, default=30,
                        help='Number of days to look ahead for upcoming events (default: 30)')
    parser.add_argument('--max-cache-size', type=int, default=30,
                        help='Maximum number of sessions to keep in memory cache (default: 30)')
    parser.add_argument('--stats-file', type=str, default='update_stats.json',
                        help='File to save usage statistics (default: update_stats.json)')
    parser.add_argument('--prioritize', action='store_true',
                        help='Prioritize important sessions (races and qualifying) first')
    parser.add_argument('--retry', type=int, default=3,
                        help='Number of retry attempts for failed downloads (default: 3)')
    return parser.parse_args()

def get_recent_and_upcoming_events(session_service, lookback_days=14, lookahead_days=30):
    """
    Get recent and upcoming F1 events using SessionService.
    
    Args:
        session_service: SessionService instance
        lookback_days: Number of days to look back
        lookahead_days: Number of days to look ahead
        
    Returns:
        list: List of events to update
    """
    current_year = datetime.now().year
    events_to_update = []
    
    try:
        # Get current year schedule
        events = session_service.get_events_for_year(current_year)
        
        # Calculate date range
        now = datetime.now().date()
        start_date = now - timedelta(days=lookback_days)
        end_date = now + timedelta(days=lookahead_days)
        
        # Filter events within the date range
        for event in events:
            if event.get('date'):
                event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
                if start_date <= event_date <= end_date:
                    events_to_update.append({
                        'year': current_year,
                        'name': event['name'],
                        'date': event_date
                    })
        
        # Check if we need to look at next year's schedule
        if (now.month >= 11):  # If it's November or December
            try:
                next_year = current_year + 1
                next_year_events = session_service.get_events_for_year(next_year)
                
                # Add early events from next year
                for event in next_year_events:
                    if event.get('date'):
                        event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
                        if event_date <= end_date:
                            events_to_update.append({
                                'year': next_year,
                                'name': event['name'],
                                'date': event_date
                            })
            except Exception as e:
                logger.warning(f"Could not get next year's schedule: {e}")
        
        return events_to_update
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return []

def get_available_sessions_for_event(year, event_name, session_service):
    """Get all available sessions for a specific event using SessionService."""
    try:
        # Get session types from SessionService
        sessions = session_service.get_session_types(year, event_name)
        available_sessions = [session['code'] for session in sessions]
        return available_sessions
    except Exception as e:
        logger.error(f"Error getting available sessions for {year} {event_name}: {e}")
        return []

def prioritize_sessions(sessions):
    """
    Prioritize sessions based on importance.
    
    Args:
        sessions: List of session types
        
    Returns:
        list: Prioritized list of session types
    """
    return sorted(sessions, key=lambda x: SESSION_PRIORITY.get(x, 0), reverse=True)

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed, memory tracking will be limited")

def update_memory_stats():
    """Update memory usage statistics."""
    try:
        # Get memory usage
        memory_usage = 0
        if PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # Convert to MB
            
            # Update memory usage in stats
            usage_stats['memory_usage'] = memory_usage
            
            # If memory usage is high, trigger garbage collection
            if memory_usage > 500:  # More than 500MB
                gc.collect()
        else:
            # Without psutil, we can still trigger periodic garbage collection
            gc.collect()
            
        return memory_usage
    except Exception as e:
        logger.error(f"Error updating memory stats: {e}")
        return 0

def update_session(year, event_name, session_type, session_service, retry_count=3):
    """Update a specific session in the cache using SessionService."""
    # Update session type stats
    if session_type not in usage_stats['session_types']:
        usage_stats['session_types'][session_type] = {
            'total': 0,
            'successful': 0,
            'failed': 0
        }
    
    usage_stats['session_types'][session_type]['total'] += 1
    usage_stats['total_sessions'] += 1
    
    try:
        # Get session info to check if it has started
        sessions = session_service.get_session_types(year, event_name)
        session_info = next((s for s in sessions if s['code'] == session_type), None)
        
        if session_info and session_info.get('date'):
            session_date = datetime.strptime(session_info['date'], '%Y-%m-%d').date()
            if session_date > datetime.now().date():
                logger.info(f"Session {year} {event_name} {session_type} has not started yet, skipping")
                return False
        
        # Try to load the session with retries
        for attempt in range(retry_count):
            try:
                # Use SessionService to get the session (which will cache it)
                session_service.get_session(year, event_name, session_type)
                
                # If we get here, the session was loaded successfully
                logger.info(f"Successfully updated {year} {event_name} {session_type}")
                
                # Update stats
                usage_stats['session_types'][session_type]['successful'] += 1
                usage_stats['successful_sessions'] += 1
                
                # Update memory stats
                update_memory_stats()
                
                return True
            except Exception as e:
                if attempt < retry_count - 1:
                    logger.warning(f"Attempt {attempt+1}/{retry_count} failed for {year} {event_name} {session_type}: {e}")
                    time.sleep(2)  # Wait before retrying
                else:
                    logger.error(f"Failed to update {year} {event_name} {session_type} after {retry_count} attempts: {e}")
                    
                    # Update stats
                    usage_stats['session_types'][session_type]['failed'] += 1
                    usage_stats['failed_sessions'] += 1
                    
                    return False
    except Exception as e:
        logger.error(f"Error updating {year} {event_name} {session_type}: {e}")
        
        # Update stats
        usage_stats['session_types'][session_type]['failed'] += 1
        usage_stats['failed_sessions'] += 1
        
        return False

def update_event(event, session_service, prioritize=False, retry_count=3):
    """Update all available sessions for an event."""
    year = event['year']
    event_name = event['name']
    logger.info(f"Updating event: {year} {event_name}")
    
    # Get available sessions for this event
    available_sessions = get_available_sessions_for_event(year, event_name, session_service)
    logger.info(f"Available sessions for {year} {event_name}: {available_sessions}")
    
    # Prioritize sessions if requested
    if prioritize and available_sessions:
        available_sessions = prioritize_sessions(available_sessions)
        logger.info(f"Prioritized sessions for {year} {event_name}: {available_sessions}")
    
    results = {}
    for session_type in available_sessions:
        result = update_session(year, event_name, session_type, session_service, retry_count)
        results[session_type] = result
        
        # Periodically trigger garbage collection to free memory
        gc.collect()
    
    # Log results
    successful = sum(1 for result in results.values() if result)
    total = len(results)
    logger.info(f"Updated {successful}/{total} sessions for {year} {event_name}")
    
    return results

def save_stats(stats_file):
    """Save usage statistics to a JSON file."""
    try:
        with open(stats_file, 'w') as f:
            json.dump(usage_stats, f, indent=2)
        logger.info(f"Statistics saved to {stats_file}")
    except Exception as e:
        logger.error(f"Error saving statistics: {e}")

def main():
    """Main function to update F1 data."""
    args = parse_args()
    
    # Initialize usage statistics
    usage_stats['start_time'] = datetime.now().isoformat()
    
    # Create cache directory if it doesn't exist
    os.makedirs(args.cache_dir, exist_ok=True)
    
    # Enable FastF1 cache
    fastf1.Cache.enable_cache(args.cache_dir)
    
    # Create SessionService with increased cache size
    session_service = SessionService(max_cache_size=args.max_cache_size)
    
    # Get events to update
    events = get_recent_and_upcoming_events(
        session_service, args.lookback_days, args.lookahead_days
    )
    logger.info(f"Found {len(events)} events to update")
    usage_stats['events_processed'] = len(events)
    
    # Update each event
    for event in events:
        update_event(event, session_service, args.prioritize, args.retry)
        
        # Periodically trigger garbage collection to free memory
        gc.collect()
    
    # Update end time
    usage_stats['end_time'] = datetime.now().isoformat()
    
    # Save statistics
    save_stats(args.stats_file)
    
    # Log summary
    logger.info(f"Update complete. Successfully updated {usage_stats['successful_sessions']}/{usage_stats['total_sessions']} sessions.")
    if usage_stats['total_sessions'] > 0:
        success_rate = (usage_stats['successful_sessions'] / usage_stats['total_sessions']) * 100
        logger.info(f"Success rate: {success_rate:.2f}%")

if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed = time.time() - start_time
    logger.info(f"Total execution time: {elapsed:.2f} seconds")
