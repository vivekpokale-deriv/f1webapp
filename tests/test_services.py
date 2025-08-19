import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from services.schedule_service import get_schedule
from services.standings_service import get_driver_standings, get_constructor_standings

class TestServices(unittest.TestCase):

    @patch('services.schedule_service.fastf1.get_event_schedule')
    def test_get_schedule(self, mock_get_event_schedule):
        # Mock the fastf1.get_event_schedule function
        mock_schedule = pd.DataFrame({
            'EventName': ['Bahrain Grand Prix', 'Saudi Arabian Grand Prix'],
            'EventDate': pd.to_datetime(['2023-03-05', '2023-03-19']),
            'Country': ['Bahrain', 'Saudi Arabia'],
            'Location': ['Sakhir', 'Jeddah']
        })
        mock_get_event_schedule.return_value = mock_schedule

        # Call the function to be tested
        schedule = get_schedule(2023)

        # Assert that the mock function was called with the correct arguments
        mock_get_event_schedule.assert_called_once_with(2023)

        # Assert that the returned schedule is the one we mocked
        self.assertEqual(len(schedule), 2)
        self.assertEqual(schedule['EventName'].iloc[0], 'Bahrain Grand Prix')

    @patch('services.standings_service.fastf1.get_event_schedule')
    def test_get_driver_standings(self, mock_get_event_schedule):
        # Mock the event schedule and the result
        mock_event = MagicMock()
        mock_event.results = pd.DataFrame({
            'DriverNumber': ['1', '11'],
            'BroadcastName': ['M VERSTAPPEN', 'S PEREZ'],
            'TeamName': ['Red Bull Racing', 'Red Bull Racing'],
            'Position': [1, 2],
            'Points': [25, 18]
        })
        mock_event.get_driver_standings.return_value = mock_event.results

        mock_schedule = MagicMock()
        mock_schedule.get_event_by_round.return_value = mock_event
        mock_get_event_schedule.return_value = mock_schedule

        # Call the function to be tested
        standings = get_driver_standings(2023, 1)

        # Assert that the mock functions were called correctly
        mock_get_event_schedule.assert_called_once_with(2023)
        mock_schedule.get_event_by_round.assert_called_once_with(1)
        mock_event.load.assert_called_once()
        mock_event.get_driver_standings.assert_called_once()

        # Assert that the returned standings are correct
        self.assertEqual(len(standings), 2)
        self.assertEqual(standings['BroadcastName'].iloc[0], 'M VERSTAPPEN')

    @patch('services.standings_service.fastf1.get_event_schedule')
    def test_get_constructor_standings(self, mock_get_event_schedule):
        # Mock the event schedule and the result
        mock_event = MagicMock()
        mock_event.results = pd.DataFrame({
            'TeamName': ['Red Bull Racing', 'Aston Martin'],
            'Position': [1, 2],
            'Points': [43, 23]
        })
        mock_event.get_constructor_standings.return_value = mock_event.results

        mock_schedule = MagicMock()
        mock_schedule.get_event_by_round.return_value = mock_event
        mock_get_event_schedule.return_value = mock_schedule

        # Call the function to be tested
        standings = get_constructor_standings(2023, 1)

        # Assert that the mock functions were called correctly
        mock_get_event_schedule.assert_called_once_with(2023)
        mock_schedule.get_event_by_round.assert_called_once_with(1)
        mock_event.load.assert_called_once()
        mock_event.get_constructor_standings.assert_called_once()

        # Assert that the returned standings are correct
        self.assertEqual(len(standings), 2)
        self.assertEqual(standings['TeamName'].iloc[0], 'Red Bull Racing')

if __name__ == '__main__':
    unittest.main()
