import unittest

import db.db as db
from handler import handler


class TestHandler(unittest.TestCase):

    def test_handler_with_event(self):
        db.READ_MOCK = True
        db.WRITE_MOCK = True

        event = {
            'detail-type': 'Scheduled Event',
            'detail': {
                'action': 'sim',
                'sport': 'football-2024',
                'league': 'purdue',
                'week': 5,
                'iter': 100
            }
        }
        result = handler(event, None)
        print(result)

        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['action'], event['detail']['action'])
        self.assertEqual(result['sport'], event['detail']['sport'])
        self.assertEqual(result['league'], event['detail']['league'])
