#!/usr/bin/env python3
"""
F1 Data Caching Script

This script pre-caches all Formula 1 data from 2018 to the most recent race
using the FastF1 library and our custom SessionService. It loads each session 
and saves the data to the cache directory, which significantly improves 
performance for the web application.

The script includes performance optimizations such as:
- Session prioritization (races and qualifying first)
- Memory management for large operations
- Usage statistics tracking

Usage:
    python cache_f1_data.py [--cache-dir CACHE_DIR] [--start-year YEAR] [--threads NUM]
"""

import os
import sys
import argparse
import logging
import time
import gc
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import fastf1

# Try to import tqdm, but make it optional
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Define a simple progress bar alternative
    class SimplePBar:
        def __init__(self, total, desc=""):
            self.total = total
            self.desc = desc
            self.n = 0
            self.start_time = time.time()
            self._print_status()
            
        def update(self, n=1):
            self.n += n
            self._print_status()
            
        def set_postfix(self, d):
            self.postfix = d
            self._print_status()
            
        def _print_status(self):
            elapsed = time.time() - self.start_time
            percent = 100 * (self.n / self.total) if self.total > 0 else 0
            postfix_str = ""
            if hasattr(self, 'postfix'):
                postfix_str = " " + str(self.postfix)
            sys.stdout.write(f"\r{self.desc}: {self.n}/{self.total} ({percent:.1f}%) [{elapsed:.1f}s]{postfix_str}")
            sys.stdout.flush()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.write("\n")
            sys.stdout.flush()
    
    # Use our simple progress bar as a replacement for tqdm
    tqdm = SimplePBar

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.session_service import SessionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("f1_cache.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('f1_caching')

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
    'years_processed': [],
    'events_processed': 0,
    'memory_usage': 0,
    'session_types': {}
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Cache F1 data from 2018 to present')
    parser.add_argument('--cache-dir', type=str, default='cache',
                        help='Directory to store cached data (default: cache)')
    parser.add_argument('--start-year', type=int, default=2018,
                        help='First year to cache (default: 2018)')
    parser.add_argument('--threads', type=int, default=4,
                        help='Number of threads to use for parallel downloading (default: 4)')
    parser.add_argument('--retry', type=int, default=3,
                        help='Number of retry attempts for failed downloads (default: 3)')
    parser.add_argument('--timeout', type=int, default=300,
                        help='Timeout in seconds for each session download (default: 300)')
    parser.add_argument('--max-cache-size', type=int, default=50,
                        help='Maximum number of sessions to keep in memory cache (default: 50)')
    parser.add_argument('--stats-file', type=str, default='cache_stats.json',
                        help='File to save usage statistics (default: cache_stats.json)')
    parser.add_argument('--prioritize', action='store_true',
                        help='Prioritize important sessions (races and qualifying) first')
    return parser.parse_args()

def get_years_to_cache(start_year):
    """Get list of years to cache from start_year to current year."""
    current_year = datetime.now().year
    return list(range(start_year, current_year + 1))

def get_events_for_year(year, session_service):
    """Get all events for a specific year using SessionService."""
    try:
        # Use SessionService to get events
        events = session_service.get_events_for_year(year)
        
        # Convert to DataFrame-like structure for compatibility
        event_list = []
        for event in events:
            # For current year, filter to only include past races
            if year == datetime.now().year:
                if event.get('date'):
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
                    current_date = datetime.now().date()
                    if event_date > current_date:
                        continue
            
            event_list.append({
                'EventName': event['name'],
                'RoundNumber': event['round'],
                'Country': event.get('country', ''),
                'Location': event.get('location', '')
            })
            
        return event_list
    except Exception as e:
        logger.error(f"Error fetching events for {year}: {e}")
        return None

def get_available_sessions_for_event(year, event_name, session_service):
    """
    Get all available sessions for a specific event.
    This properly handles sprint weekends which have a different format.
    """
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

def update_memory_stats():
    """Update memory usage statistics."""
    try:
        # Get memory usage
        memory_usage = 0
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # Convert to MB
        except ImportError:
            logger.warning("psutil not installed, memory tracking disabled")
        
        # Update memory usage in stats
        usage_stats['memory_usage'] = memory_usage
        
        # If memory usage is high, trigger garbage collection
        if memory_usage > 1000:  # More than 1GB
            gc.collect()
            
        return memory_usage
    except Exception as e:
        logger.error(f"Error updating memory stats: {e}")
        return 0

def cache_session(year, event_name, session_type, session_service, retry_count=3, timeout=300):
    """Cache a specific session using SessionService."""
    # Update session type stats
    if session_type not in usage_stats['session_types']:
        usage_stats['session_types'][session_type] = {
            'total': 0,
            'successful': 0,
            'failed': 0
        }
    
    usage_stats['session_types'][session_type]['total'] += 1
    usage_stats['total_sessions'] += 1
    
    for attempt in range(retry_count):
        try:
            # Set a timeout for the session load
            start_time = time.time()
            
            # Try to load the session using SessionService
            session_service.get_session(year, event_name, session_type)
            
            # If we get here, the session was loaded successfully
            logger.info(f"Successfully cached {year} {event_name} {session_type}")
            
            # Update stats
            usage_stats['session_types'][session_type]['successful'] += 1
            usage_stats['successful_sessions'] += 1
            
            # Update memory stats
            update_memory_stats()
            
            return True
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                logger.warning(f"Timeout ({timeout}s) reached for {year} {event_name} {session_type}")
            
            if attempt < retry_count - 1:
                logger.warning(f"Attempt {attempt+1}/{retry_count} failed for {year} {event_name} {session_type}: {e}")
                time.sleep(2)  # Wait before retrying
            else:
                logger.error(f"Failed to cache {year} {event_name} {session_type} after {retry_count} attempts: {e}")
                
                # Update stats
                usage_stats['session_types'][session_type]['failed'] += 1
                usage_stats['failed_sessions'] += 1
                
                return False

def cache_event(year, event, session_service, prioritize=False, retry_count=3, timeout=300):
    """Cache all available sessions for a specific event."""
    event_name = event['EventName']
    logger.info(f"Caching event: {year} {event_name}")
    
    # Get available sessions for this event
    available_sessions = get_available_sessions_for_event(year, event_name, session_service)
    logger.info(f"Available sessions for {year} {event_name}: {available_sessions}")
    
    # Prioritize sessions if requested
    if prioritize and available_sessions:
        available_sessions = prioritize_sessions(available_sessions)
        logger.info(f"Prioritized sessions for {year} {event_name}: {available_sessions}")
    
    results = {}
    for session_type in available_sessions:
        result = cache_session(year, event_name, session_type, session_service, retry_count, timeout)
        results[session_type] = result
        
        # Periodically trigger garbage collection to free memory
        gc.collect()
    
    return results, len(available_sessions)

def save_stats(stats_file):
    """Save usage statistics to a JSON file."""
    try:
        with open(stats_file, 'w') as f:
            json.dump(usage_stats, f, indent=2)
        logger.info(f"Statistics saved to {stats_file}")
    except Exception as e:
        logger.error(f"Error saving statistics: {e}")

def main():
    """Main function to cache all F1 data."""
    args = parse_args()
    
    # Initialize usage statistics
    usage_stats['start_time'] = datetime.now().isoformat()
    
    # Create cache directory if it doesn't exist
    os.makedirs(args.cache_dir, exist_ok=True)
    
    # Enable FastF1 cache
    fastf1.Cache.enable_cache(args.cache_dir)
    
    # Create SessionService with increased cache size
    session_service = SessionService(max_cache_size=args.max_cache_size)
    
    # Get years to cache
    years = get_years_to_cache(args.start_year)
    logger.info(f"Caching data for years: {years}")
    
    # Cache data for each year
    for year in years:
        logger.info(f"Processing year: {year}")
        usage_stats['years_processed'].append(year)
        
        # Get events for the year
        events = get_events_for_year(year, session_service)
        if events is None or len(events) == 0:
            logger.warning(f"No events found for {year}")
            continue
        
        logger.info(f"Found {len(events)} events for {year}")
        usage_stats['events_processed'] += len(events)
        
        # Create a progress bar for this year
        with tqdm(total=len(events), desc=f"Year {year}") as pbar:
            # Use ThreadPoolExecutor for parallel downloading
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                # Submit tasks for each event
                future_to_event = {}
                for event in events:
                    future = executor.submit(
                        cache_event, year, event, session_service, 
                        args.prioritize, args.retry, args.timeout
                    )
                    future_to_event[future] = event['EventName']
                
                # Process completed tasks
                for future in as_completed(future_to_event):
                    event_name = future_to_event[future]
                    try:
                        future.result()
                        
                        # Update progress bar
                        pbar.update(1)
                        pbar.set_postfix({
                            "Sessions": f"{usage_stats['successful_sessions']}/{usage_stats['total_sessions']}"
                        })
                            
                    except Exception as e:
                        logger.error(f"Error processing {year} {event_name}: {e}")
                        # Update progress bar
                        pbar.update(1)
    
    # Update end time
    usage_stats['end_time'] = datetime.now().isoformat()
    
    # Save statistics
    save_stats(args.stats_file)
    
    # Log summary
    logger.info(f"Caching complete. Successfully cached {usage_stats['successful_sessions']}/{usage_stats['total_sessions']} sessions.")
    if usage_stats['total_sessions'] > 0:
        success_rate = (usage_stats['successful_sessions'] / usage_stats['total_sessions']) * 100
        logger.info(f"Success rate: {success_rate:.2f}%")

if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed = time.time() - start_time
    logger.info(f"Total execution time: {elapsed:.2f} seconds")
