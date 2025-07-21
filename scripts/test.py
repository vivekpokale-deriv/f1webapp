#!/usr/bin/env python3
"""
Test script for exploring the fastf1.events.EventSchedule class.

This script demonstrates how to use fastf1.get_event_schedule() to get event schedules
for different F1 seasons and how to work with the EventSchedule object.
"""

import os
import sys
import pandas as pd
import fastf1
from fastf1.events import EventSchedule
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('f1_test')

# Enable FastF1 cache
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
fastf1.Cache.enable_cache(cache_dir)

def explore_event_schedule(year):
    """
    Explore the EventSchedule for a specific year.
    
    Args:
        year: The year to get the schedule for
    """
    logger.info(f"Getting event schedule for {year}")
    
    # Get the event schedule using fastf1.get_event_schedule()
    schedule = fastf1.get_event_schedule(year)
    
    # Print basic information about the schedule
    logger.info(f"Schedule type: {type(schedule)}")
    logger.info(f"Number of events: {len(schedule)}")
    
    # Print the column names
    logger.info(f"Available columns: {schedule.columns.tolist()}")
    
    # Print the first event details
    if len(schedule) > 0:
        first_event = schedule.iloc[0]
        logger.info(f"First event: {first_event['EventName']} in {first_event['Country']}")
        logger.info(f"First event date: {first_event['EventDate']}")
        
        # Check if session times are available
        if 'FP1Date' in first_event and pd.notna(first_event['FP1Date']):
            logger.info(f"FP1 date: {first_event['FP1Date']}")
        if 'FP1Time' in first_event and pd.notna(first_event['FP1Time']):
            logger.info(f"FP1 time: {first_event['FP1Time']}")
    
    return schedule

def filter_events(schedule, country=None, circuit=None):
    """
    Filter events by country or circuit.
    
    Args:
        schedule: The EventSchedule to filter
        country: Optional country name to filter by
        circuit: Optional circuit name to filter by
        
    Returns:
        DataFrame: Filtered schedule
    """
    filtered = schedule
    
    if country:
        filtered = filtered[filtered['Country'] == country]
        
    if circuit:
        filtered = filtered[filtered['Location'] == circuit]
        
    return filtered

def get_next_event(schedule):
    """
    Get the next upcoming event from a schedule.
    
    Args:
        schedule: The EventSchedule to search
        
    Returns:
        Series: The next event or None if no future events
    """
    # Filter future events
    now = pd.Timestamp.now()
    future_events = schedule[schedule['EventDate'] > now]
    
    if future_events.empty:
        return None
        
    # Get the next event
    return future_events.iloc[0]

def main():
    """Main function to run the script."""
    try:
        # Get schedules for multiple years
        current_year = pd.Timestamp.now().year
        years = [current_year - 1, current_year, current_year + 1]
        
        for year in years:
            try:
                schedule = explore_event_schedule(year)
                
                # Example: Filter events by country
                monaco_events = filter_events(schedule, country='Monaco')
                logger.info(f"Monaco events in {year}: {len(monaco_events)}")
                
                # Example: Get the next event
                next_event = get_next_event(schedule)
                if next_event is not None:
                    logger.info(f"Next event in {year}: {next_event['EventName']} on {next_event['EventDate']}")
                else:
                    logger.info(f"No future events in {year}")
                
                # Example: Access specific round
                if len(schedule) >= 5:
                    round5 = schedule[schedule['RoundNumber'] == 5]
                    if not round5.empty:
                        logger.info(f"Round 5 in {year}: {round5.iloc[0]['EventName']}")
                
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Error processing {year} schedule: {e}")
        
        # Example: Direct instantiation (not recommended)
        logger.info("Direct instantiation example (not recommended):")
        try:
            # This is just for demonstration - fastf1.get_event_schedule() is the recommended way
            direct_schedule = EventSchedule(year=current_year)
            logger.info(f"Direct instantiation result type: {type(direct_schedule)}")
        except Exception as e:
            logger.error(f"Error with direct instantiation: {e}")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
