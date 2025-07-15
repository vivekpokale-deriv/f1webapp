"""
Driver and team details model for F1 Web App.
"""


class DriverTeamDetails:
    """
    Class to store driver or team details.
    """
    def __init__(self, name, team, points, position=None, driver_number=None, driver_code=None):
        """
        Initialize driver or team details.
        
        Args:
            name: Driver name or team name
            team: Team name (same as name for constructor standings)
            points: Championship points
            position: Championship position (optional)
            driver_number: Driver number (optional, for drivers only)
            driver_code: Driver code (optional, for drivers only)
        """
        self.name = name
        self.team = team
        self.points = points
        self.position = position
        self.driver_number = driver_number
        self.driver_code = driver_code
        
    def to_dict(self):
        """
        Convert to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the driver or team
        """
        result = {
            "name": self.name,
            "team": self.team,
            "points": self.points
        }
        
        if self.position is not None:
            result["position"] = self.position
            
        if self.driver_number is not None:
            result["driver_number"] = self.driver_number
            
        if self.driver_code is not None:
            result["driver_code"] = self.driver_code
            
        return result
