import unittest
from unittest.mock import Mock, patch

from handler import handler


class TestHandler(unittest.TestCase):

    def test_default_run_fetches_then_simulates(self):
        event = {
            'detail-type': 'Scheduled Event',
            'detail': {
                'sport': 'football-2026',
                'league': 'purdue',
                'week': 5,
                'iter': 100
            }
        }
        config = Mock()
        config.leagues = {
            'football-2026': {
                'purdue': {'app': 'espn'},
            },
        }

        with patch('handler.Config', return_value=config), \
                patch('handler.DataFetcher') as fetcher_class, \
                patch('handler.League') as league_class, \
                patch('handler.Processor') as processor_class:
            result = handler(event, None)

        fetcher_class.assert_called_once_with('football-2026', 'purdue', 5)
        fetcher_class.return_value.fetch_league.assert_called_once_with()
        fetcher_class.return_value.fetch_players.assert_called_once_with()
        league_class.assert_called_once_with(
            'football-2026', 'purdue', 5, 100,
        )
        processor_class.assert_called_once_with(league_class.return_value)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['action'], 'run')
        self.assertEqual(result['sport'], event['detail']['sport'])
        self.assertEqual(result['league'], event['detail']['league'])

    def test_sleeper_run_only_simulates(self):
        event = {'sport': 'football-2026', 'league': 'purdue', 'week': 5}
        config = Mock()
        config.leagues = {
            'football-2026': {'purdue': {'app': 'sleeper'}},
        }

        with patch('handler.Config', return_value=config), \
                patch('handler.DataFetcher') as fetcher_class, \
                patch('handler.League') as league_class, \
                patch('handler.Processor') as processor_class:
            handler(event, None)

        fetcher_class.assert_not_called()
        processor_class.assert_called_once_with(league_class.return_value)


if __name__ == '__main__':
    unittest.main()
