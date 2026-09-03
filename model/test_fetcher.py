import json
import unittest
from unittest.mock import patch

from fetch.fetcher import DataFetcher
from fetch.utils import get_data_paths, get_profile_image_url


def player_entry(
    player_id=101,
    name='Test Runner',
    position=2,
    pro_team=1,
    injury='QUESTIONABLE',
):
    return {
        'playerId': player_id,
        'acquisitionType': 'WAIVER',
        'playerPoolEntry': {
            'player': {
                'id': player_id,
                'fullName': name,
                'defaultPositionId': position,
                'eligibleSlots': [position],
                'proTeamId': pro_team,
                'injuryStatus': injury,
                'ownership': {
                    'percentOwned': 75.25,
                    'percentChange': 2.5,
                },
                'stats': [
                    {
                        'scoringPeriodId': 0,
                        'statSourceId': 0,
                        'statSplitTypeId': 0,
                        'appliedTotal': 25.0,
                        'appliedAverage': 12.5,
                    },
                    {
                        'scoringPeriodId': 0,
                        'statSourceId': 1,
                        'statSplitTypeId': 0,
                        'appliedTotal': 200.0,
                        'appliedAverage': 11.75,
                    },
                    {
                        'scoringPeriodId': 1,
                        'statSourceId': 0,
                        'statSplitTypeId': 1,
                        'appliedTotal': 15.0,
                    },
                    {
                        'scoringPeriodId': 2,
                        'statSourceId': 1,
                        'statSplitTypeId': 1,
                        'appliedTotal': 13.5,
                    },
                ],
            },
        },
    }


def league_fixture(scoring_type='H2H_POINTS'):
    roster_player = player_entry()
    return {
        'scoringPeriodId': 2,
        'members': [
            {
                'id': 'owner-1',
                'firstName': 'Alice',
                'lastName': "O'Neil",
                'displayName': 'alice',
            },
            {
                'id': 'owner-2',
                'firstName': '',
                'lastName': '',
                'displayName': 'BobDisplay',
            },
        ],
        'teams': [
            {
                'id': 1,
                'primaryOwner': 'owner-1',
                'owners': ['owner-1'],
                'name': 'Alpha Team',
                'abbrev': 'ALP',
                'divisionId': 10,
                'logo': 'alpha.png',
                'roster': {'entries': [roster_player]},
            },
            {
                'id': 2,
                'owners': ['owner-2'],
                'location': 'Beta',
                'nickname': 'Club',
                'abbrev': 'BET',
                'divisionId': 20,
                'logo': 'beta.png',
                'roster': {
                    'entries': [
                        player_entry(202, 'Test Catcher', 6, 2, 'ACTIVE')
                    ],
                },
            },
        ],
        'schedule': [
            {
                'id': 1,
                'matchupPeriodId': 1,
                'winner': 'HOME',
                'home': {'teamId': 1, 'totalPoints': 110.5},
                'away': {'teamId': 2, 'totalPoints': 99.25},
            },
        ],
        'settings': {
            'scoringSettings': {'scoringType': scoring_type},
            'scheduleSettings': {
                'divisions': [
                    {'id': 10, 'name': 'East'},
                    {'id': 20, 'name': 'West'},
                ],
                'matchupPeriods': {'1': [1]},
            },
        },
        'status': {'finalScoringPeriod': 18},
    }


def pro_schedule_fixture():
    game = {
        'homeProTeamId': 1,
        'awayProTeamId': 2,
        'scoringPeriodId': 2,
    }
    return {
        'settings': {
            'proTeams': [
                {
                    'id': 1,
                    'abbrev': 'AAA',
                    'proGamesByScoringPeriod': {'2': [game]},
                },
                {
                    'id': 2,
                    'abbrev': 'BBB',
                    'proGamesByScoringPeriod': {'2': [game]},
                },
            ],
        },
    }


class FakeClient:
    def __init__(self, league=None, players=None, draft=None):
        self.league = league or league_fixture()
        self.players = players or [
            self.league['teams'][0]['roster']['entries'][0],
            self.league['teams'][1]['roster']['entries'][0],
        ]
        self.draft = draft or {
            'draftDetail': {
                'drafted': True,
                'picks': [
                    {
                        'overallPickNumber': 1,
                        'roundId': 1,
                        'teamId': 2,
                        'playerId': 101,
                    },
                ],
            },
        }

    def get_league(self):
        return self.league

    def get_league_draft(self):
        return self.draft

    def get_pro_schedule(self):
        return pro_schedule_fixture()

    def league_get(self, params=None, headers=None, extend=''):
        player_filter = json.loads(headers['x-fantasy-filter'])['players']
        self.last_player_filter = player_filter
        return {'players': self.players}

    def get_player_card(self, player_ids, max_scoring_period):
        ids = set(player_ids)
        return {
            'players': [
                player for player in self.players
                if DataFetcher._player_payload(player).get('id') in ids
            ],
        }


def make_fetcher(sport='football', week=2, league=None, players=None):
    fetcher = DataFetcher.__new__(DataFetcher)
    fetcher.sport = sport
    fetcher.year = 2026
    fetcher.week = str(week)
    fetcher.league_id = 123
    fetcher.league_tag = 'test'
    fetcher.n_regular_season_weeks = 14
    fetcher.n_weeks_per_playoff_matchup = 2
    fetcher.path = get_data_paths(sport, 2026, 'test')
    fetcher.client = FakeClient(league=league, players=players)
    fetcher._league_data_cache = None
    fetcher._draft_data_cache = None
    fetcher._pro_schedule_cache = None
    fetcher.profile_images = {}
    return fetcher


class DataFetcherContractTest(unittest.TestCase):
    def test_profile_image_alias_overrides_team_logo(self):
        fetcher = make_fetcher()
        fetcher.profile_images = {'Alice ONeil': 'jack.jpeg'}

        members = fetcher._members_records()

        self.assertEqual(
            members[0]['img'],
            'https://fantasy-forecaster-data.s3.us-east-2.amazonaws.com/'
            'profile/jack.jpeg',
        )
        self.assertEqual(members[1]['img'], 'beta.png')

    def test_profile_image_alias_falls_back_to_source_image(self):
        self.assertEqual(
            get_profile_image_url('Unmapped Manager', {}, 'source-logo.png'),
            'source-logo.png',
        )

    def test_week_zero_league_update_includes_draft(self):
        fetcher = make_fetcher(week=0)
        with patch.object(fetcher, '_members_records', return_value=[]), \
                patch.object(fetcher, '_schedule_records', return_value=[]), \
                patch.object(fetcher, '_roster_records', return_value=[]), \
                patch.object(fetcher, '_write_members'), \
                patch.object(fetcher, '_write_schedule'), \
                patch.object(fetcher, '_write_rosters'), \
                patch.object(fetcher, 'fetch_draft') as fetch_draft:
            fetcher.fetch_league()

        fetch_draft.assert_called_once_with()

    def test_league_contract_uses_owner_team_and_acquisition_data(self):
        fetcher = make_fetcher()

        members = fetcher._members_records()
        self.assertEqual(members[0], {
            'id': 1,
            'manager': 'Alice ONeil',
            'team_name': 'Alpha Team',
            'abbrev': 'ALP',
            'division': 'East',
            'img': 'alpha.png',
        })
        self.assertEqual(members[1]['manager'], 'BobDisplay')

        schedule = fetcher._schedule_records()
        self.assertEqual(schedule[0]['home'], 'Alice ONeil')
        self.assertEqual(schedule[0]['away'], 'BobDisplay')
        self.assertEqual(schedule[0]['home_score'], 110.5)

        rosters = fetcher._roster_records()
        self.assertEqual(rosters[0]['player_id'], 'testrunner-RB')
        self.assertEqual(rosters[0]['aquired'], 'Free Agency')

        draft = fetcher._draft_records()
        self.assertEqual(draft[0]['manager_id'], 2)
        self.assertEqual(draft[0]['player_id'], 'testrunner-RB')

    def test_football_player_contract(self):
        fetcher = make_fetcher()
        self.assertEqual(fetcher._player_position({
            'fullName': "Ja'Marr Chase",
            'defaultPositionId': 3,
            'eligibleSlots': [3, 4, 5, 23, 7, 20, 21],
        }), 'WR')
        self.assertEqual(fetcher._player_position({
            'fullName': 'Josh Allen',
            'defaultPositionId': 1,
            'eligibleSlots': [0, 7, 20, 21],
        }), 'QB')
        info, stats = fetcher._player_records()
        player_info = next(x for x in info if x['name'] == 'Test Runner')
        player_stats = next(x for x in stats if x['id'] == 'testrunner-RB')

        self.assertEqual(player_info['team'], 'AAA')
        self.assertIn('/nfl/players/full/101.png', player_info['img'])
        self.assertEqual(player_stats['injury'], 'Q')
        self.assertEqual(player_stats['opp'], 'BBB')
        self.assertEqual(player_stats['proj'], 13.5)
        self.assertEqual(player_stats['prev_score'], 15.0)
        self.assertEqual(player_stats['total_pts'], 25.0)
        self.assertEqual(player_stats['avg_pts'], 12.5)
        self.assertEqual(player_stats['roster'], 75.25)
        self.assertEqual(player_stats['roster_change'], 2.5)

    def test_category_scores_use_wins_and_half_ties(self):
        league = league_fixture('H2H_CATEGORY')
        for side, wins, ties in [('home', 6, 1), ('away', 3, 1)]:
            league['schedule'][0][side]['cumulativeScore'] = {
                'wins': wins,
                'ties': ties,
                'scoreByStat': {'0': {'score': 1}},
            }
        schedule = make_fetcher(league=league)._schedule_records()
        self.assertEqual(schedule[0]['home_score'], 6.5)
        self.assertEqual(schedule[0]['away_score'], 3.5)

    def test_multiweek_football_playoffs_are_split(self):
        league = league_fixture()
        league['settings']['scheduleSettings']['matchupPeriods'] = {
            '15': [15, 16],
        }
        league['schedule'][0] = {
            'id': 1,
            'matchupPeriodId': 15,
            'playoffTierType': 'WINNERS_BRACKET',
            'home': {
                'teamId': 1,
                'totalPointsLive': 220,
                'pointsByScoringPeriod': {'15': 100, '16': 120},
            },
            'away': {
                'teamId': 2,
                'totalPointsLive': 220,
                'pointsByScoringPeriod': {'15': 90, '16': 130},
            },
        }
        schedule = make_fetcher(week=16, league=league)._schedule_records()
        self.assertEqual([x['week'] for x in schedule], [15])
        self.assertEqual([x['home_score'] for x in schedule], [220.0])
        self.assertEqual([x['away_score'] for x in schedule], [220.0])

    def test_baseball_and_basketball_preserve_legacy_stat_blanks(self):
        baseball_player = player_entry(position=1)
        baseball = make_fetcher('baseball', players=[baseball_player])
        _, baseball_stats = baseball._player_records()
        self.assertIsNone(baseball_stats[0]['proj'])
        self.assertIsNone(baseball_stats[0]['prev_score'])
        self.assertEqual(baseball_stats[0]['total_pts'], 25.0)

        basketball_player = player_entry(position=1)
        basketball = make_fetcher('basketball', players=[basketball_player])
        _, basketball_stats = basketball._player_records()
        self.assertIsNone(basketball_stats[0]['proj'])
        self.assertIsNone(basketball_stats[0]['prev_score'])
        self.assertIsNone(basketball_stats[0]['total_pts'])
        self.assertIsNone(basketball_stats[0]['avg_pts'])

    def test_roto_is_rejected_before_translation(self):
        fetcher = make_fetcher(league=league_fixture('ROTO'))
        with self.assertRaisesRegex(ValueError, 'roto leagues are unsupported'):
            fetcher._league_data()


if __name__ == '__main__':
    unittest.main()
