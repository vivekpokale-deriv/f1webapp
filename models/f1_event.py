"""
F1 event model for F1 Web App.
"""

from datetime import datetime


class F1Event:
    """
    Class to store F1 event details.
    """
    def __init__(self, race_name, event_type, start_time, location, country):
        """
        Initialize F1 event details.
        
        Args:
            race_name: Name of the race
            event_type: Type of event (e.g., 'Race', 'Practice 1', 'Qualifying')
            start_time: Start time of the event
            location: Location of the event
            country: Country of the event
        """
        self.race_name = race_name
        self.event_type = event_type
        self.start_time = start_time
        self.location = location
        self.country = country
        
    def to_dict(self):
        """
        Convert to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the event
        """
        return {
            "race_name": self.race_name,
            "event_type": self.event_type,
            "start_time": self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            "location": self.location,
            "country": self.country
        }
