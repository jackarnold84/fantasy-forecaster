import json
from collections import defaultdict

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from db.db import read_s3, write_s3
from fetch.utils import (clean_text, get_data_paths, get_player_id, parse_float,
                         parse_int, player_pos_mapper)


SPORT_API_NAMES = {
    'football': 'nfl',
    'baseball': 'mlb',
    'basketball': 'nba',
}

POSITION_MAPS = {
    'football': {
        0: 'QB', 1: 'TQB', 2: 'RB', 3: 'RB/WR', 4: 'WR', 5: 'WR/TE',
        6: 'TE', 7: 'OP', 8: 'DT', 9: 'DE', 10: 'LB', 11: 'DL',
        12: 'CB', 13: 'S', 14: 'DB', 15: 'DP', 16: 'DST', 17: 'K',
        18: 'P', 19: 'HC',
    },
    'baseball': {
        1: 'SP', 2: 'C', 3: '1B', 4: '2B', 5: '3B', 6: 'SS',
        7: 'OF', 8: 'OF', 9: 'OF', 10: 'DH', 11: 'RP',
    },
    'basketball': {
        1: 'PG', 2: 'SG', 3: 'SF', 4: 'PF', 5: 'C',
    },
}

FOOTBALL_DEFAULT_POSITION_MAP = {
    1: 'QB',
    2: 'RB',
    3: 'WR',
    4: 'TE',
    5: 'K',
    16: 'DST',
}

FOOTBALL_PRIMARY_SLOTS = {
    0, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
}

INJURY_MAP = {
    'ACTIVE': None,
    'NORMAL': None,
    'QUESTIONABLE': 'Q',
    'DOUBTFUL': 'D',
    'OUT': 'O',
    'INJURY_RESERVE': 'IR',
    'INJURED_RESERVE': 'IR',
    'SUSPENSION': 'SUSP',
    'SUSPENDED': 'SUSP',
    'DAY_TO_DAY': 'DTD',
    'TEN_DAY_IL': 'IL10',
    'FIFTEEN_DAY_IL': 'IL15',
    'SIXTY_DAY_IL': 'IL60',
    'IL10': 'IL10',
    'IL15': 'IL15',
    'IL60': 'IL60',
}

ACQUISITION_MAP = {
    'DRAFT': 'Draft',
    'FREEAGENT': 'Free Agency',
    'FREE_AGENT': 'Free Agency',
    'WAIVER': 'Free Agency',
    'WAIVERS': 'Free Agency',
    'TRADE': 'Trade',
}


class ReliableEspnFantasyRequests:
    """Timeout/retry wrapper around espn-api's endpoint configuration."""

    def __init__(self, sport, year, league_id):
        from espn_api.requests.espn_requests import EspnFantasyRequests

        self._client = EspnFantasyRequests(
            sport=sport,
            year=year,
            league_id=league_id,
        )
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({'GET'}),
            respect_retry_after_header=True,
        )
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.timeout = (5, 20)

    def _get(self, endpoint, params=None, headers=None):
        response = self.session.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code == 401:
            raise RuntimeError(
                'ESPN denied access. This collector supports public leagues only.'
            )
        if response.status_code == 404:
            raise RuntimeError('ESPN league or resource was not found')
        response.raise_for_status()
        data = response.json()
        return data[0] if isinstance(data, list) else data

    def league_get(self, params=None, headers=None, extend=''):
        return self._get(
            self._client.LEAGUE_ENDPOINT + extend,
            params=params,
            headers=headers,
        )

    def get(self, params=None, headers=None, extend=''):
        return self._get(
            self._client.ENDPOINT + extend,
            params=params,
            headers=headers,
        )

    def get_league(self):
        return self.league_get(params={
            'view': ['mTeam', 'mRoster', 'mMatchup', 'mSettings', 'mStandings'],
        })

    def get_league_draft(self):
        return self.league_get(params={'view': 'mDraftDetail'})

    def get_pro_schedule(self):
        return self.get(params={'view': 'proTeamSchedules_wl'})

    def get_player_card(self, player_ids, max_scoring_period):
        filters = {
            'players': {
                'filterIds': {'value': player_ids},
                'filterStatsForTopScoringPeriodIds': {
                    'value': max_scoring_period,
                    'additionalValue': [
                        f'00{self._client.year}',
                        f'10{self._client.year}',
                    ],
                },
            },
        }
        return self.league_get(
            params={'view': 'kona_playercard'},
            headers={'x-fantasy-filter': json.dumps(filters)},
        )


class DataFetcher:
    """Collect ESPN fantasy data without rendering fantasy.espn.com pages."""

    def __init__(self, sport_tag, league_tag, week, client=None):
        league_config = Config().leagues[sport_tag][league_tag]
        self.sport, self.year = sport_tag.split('-')
        if self.sport not in SPORT_API_NAMES:
            raise ValueError(f'unsupported ESPN sport: {self.sport}')

        self.year = int(self.year)
        self.week = str(week)
        self.league_id = int(league_config['league_id'])
        self.league_tag = league_tag
        self.n_regular_season_weeks = league_config['regular_season_weeks']
        self.n_weeks_per_playoff_matchup = league_config['weeks_per_playoff_matchup']
        self.path = get_data_paths(self.sport, self.year, self.league_tag)
        self.client = client or ReliableEspnFantasyRequests(
            SPORT_API_NAMES[self.sport], self.year, self.league_id,
        )
        self._league_data_cache = None
        self._draft_data_cache = None
        self._pro_schedule_cache = None

    def read_data(self, path):
        df = read_s3(path)
        if df is None:
            return []
        return df.to_dict('records')

    def write_data(self, data, path, sort, columns=None):
        data = sorted(data, key=sort)
        write_s3(pd.DataFrame(data, columns=columns), path)

    def update_data(self, data, path, sort, filter, columns=None):
        current_data = [x for x in self.read_data(path) if filter(x)]
        self.write_data(current_data + data, path, sort, columns)

    def insert_data(self, data, path, sort, key, columns=None):
        data_map = {key(x): x for x in self.read_data(path)}
        for x in data:
            data_map[key(x)] = x
        self.write_data(list(data_map.values()), path, sort, columns)

    def _league_data(self):
        if self._league_data_cache is None:
            data = self.client.get_league()
            self._require(data, 'teams', 'members', 'schedule', 'settings', 'status')
            scoring_type = data['settings'].get('scoringSettings', {}).get(
                'scoringType', 'H2H_POINTS'
            )
            if scoring_type == 'ROTO':
                raise ValueError(
                    'ESPN roto leagues are unsupported: the forecaster requires '
                    'head-to-head matchups'
                )
            self._league_data_cache = data
        return self._league_data_cache

    def _draft_data(self):
        if self._draft_data_cache is None:
            self._draft_data_cache = self.client.get_league_draft()
        return self._draft_data_cache

    def _pro_schedule(self):
        if self._pro_schedule_cache is None:
            data = self.client.get_pro_schedule()
            teams = data.get('settings', {}).get('proTeams')
            if not isinstance(teams, list):
                raise ValueError('ESPN pro schedule response is missing teams')
            self._pro_schedule_cache = data
        return self._pro_schedule_cache

    @staticmethod
    def _require(data, *keys):
        missing = [key for key in keys if key not in data]
        if missing:
            raise ValueError(f'ESPN response is missing required keys: {missing}')

    @staticmethod
    def _player_payload(entry):
        pool_entry = entry.get('playerPoolEntry', entry)
        return pool_entry.get('player') or entry.get('player') or entry

    def _player_position(self, entry):
        player = self._player_payload(entry)
        position_id = player.get('defaultPositionId')
        if self.sport == 'football':
            primary_slot = next(
                (
                    slot for slot in player.get('eligibleSlots', [])
                    if slot in FOOTBALL_PRIMARY_SLOTS
                ),
                None,
            )
            position = POSITION_MAPS['football'].get(primary_slot)
            if position is None:
                position = FOOTBALL_DEFAULT_POSITION_MAP.get(
                    position_id, str(position_id or '')
                )
        else:
            position = POSITION_MAPS[self.sport].get(
                position_id, str(position_id or '')
            )
        return player_pos_mapper(position.upper())

    def _player_identity(self, entry):
        player = self._player_payload(entry)
        name = clean_text(player.get('fullName', ''))
        position = self._player_position(entry)
        if not name or not position:
            raise ValueError(f'invalid ESPN player record: {player.get("id")}')
        return name, position, get_player_id(name, position)

    @staticmethod
    def _member_name(member):
        full_name = clean_text(
            f'{member.get("firstName", "")} {member.get("lastName", "")}'
        )
        return full_name or clean_text(member.get('displayName', ''))

    @staticmethod
    def _team_name(team):
        return clean_text(team.get('name') or (
            f'{team.get("location", "")} {team.get("nickname", "")}'
        ))

    def _team_managers(self, data=None):
        data = data or self._league_data()
        members = {member.get('id'): member for member in data['members']}
        result = {}
        for team in data['teams']:
            owner_id = team.get('primaryOwner')
            if owner_id not in members:
                owner_id = next(
                    (owner for owner in team.get('owners', []) if owner in members),
                    None,
                )
            manager = self._member_name(members.get(owner_id, {}))
            result[team['id']] = manager or self._team_name(team)
        return result

    def _members_records(self):
        data = self._league_data()
        managers = self._team_managers(data)
        divisions = {
            division.get('id'): clean_text(division.get('name', ''))
            for division in data['settings'].get('scheduleSettings', {}).get(
                'divisions', []
            )
        }
        records = []
        for team in data['teams']:
            records.append({
                'id': team['id'],
                'manager': managers[team['id']],
                'team_name': self._team_name(team),
                'abbrev': team.get('abbrev', ''),
                'division': divisions.get(team.get('divisionId'), 'USA'),
                'img': team.get('logo', ''),
            })
        if not records:
            raise ValueError('ESPN league contains no teams')
        return records

    @staticmethod
    def _category_score(team):
        score = team.get('cumulativeScore', {})
        if not score.get('scoreByStat'):
            return None
        return parse_float(score.get('wins'), 0) + \
            0.5 * parse_float(score.get('ties'), 0)

    def _team_score(self, team):
        category_score = self._category_score(team)
        if category_score is not None:
            return category_score
        if 'totalPointsLive' in team:
            return parse_float(team.get('totalPointsLive'), 0)
        return parse_float(team.get('totalPoints'), 0)

    def _schedule_records(self):
        data = self._league_data()
        managers = self._team_managers(data)
        matchup_periods = data['settings'].get('scheduleSettings', {}).get(
            'matchupPeriods', {}
        )
        records = []
        period_indices = defaultdict(int)

        for matchup in sorted(
            data['schedule'],
            key=lambda x: (x.get('matchupPeriodId', 0), x.get('id', 0)),
        ):
            home = matchup.get('home', {})
            away = matchup.get('away', {})
            home_id, away_id = home.get('teamId'), away.get('teamId')
            if home_id not in managers or away_id not in managers:
                continue

            period = int(matchup.get('matchupPeriodId', 0))
            if period <= 0:
                continue
            period_indices[period] += 1
            playoff_type = matchup.get('playoffTierType')
            playoff = period > self.n_regular_season_weeks or (
                playoff_type not in (None, '', 'NONE')
            )
            scoring_periods = matchup_periods.get(str(period), [period])

            if self.sport == 'football' and playoff:
                scoring_periods = sorted(int(x) for x in scoring_periods)
                previous_week = int(self.week) - 1
                if previous_week in scoring_periods:
                    output_week = previous_week
                elif previous_week > scoring_periods[-1]:
                    output_week = scoring_periods[-1]
                else:
                    continue
                records.append({
                    'week': output_week,
                    'matchup_idx': period_indices[period],
                    'playoff': True,
                    'home': managers[home_id],
                    'home_score': self._team_score(home),
                    'away': managers[away_id],
                    'away_score': self._team_score(away),
                })
            else:
                records.append({
                    'week': period,
                    'matchup_idx': period_indices[period],
                    'playoff': playoff,
                    'home': managers[home_id],
                    'home_score': self._team_score(home),
                    'away': managers[away_id],
                    'away_score': self._team_score(away),
                })

        if not records:
            raise ValueError('ESPN league contains no complete matchups')
        return records

    @staticmethod
    def _acquisition(value):
        if not value:
            return ''
        value = str(value).upper()
        return ACQUISITION_MAP.get(value, value.replace('_', ' ').title())

    def _roster_records(self):
        data = self._league_data()
        records = []
        for team in data['teams']:
            entries = team.get('roster', {}).get('entries', [])
            for slot_idx, entry in enumerate(entries, start=1):
                _, _, player_id = self._player_identity(entry)
                records.append({
                    'week': self.week,
                    'manager_id': team['id'],
                    'slot_idx': slot_idx,
                    'player_id': player_id,
                    'aquired': self._acquisition(entry.get('acquisitionType')),
                })
        if not records:
            raise ValueError('ESPN league contains no rostered players')
        return records

    def _player_card_records(self, player_ids):
        records = {}
        player_ids = sorted(set(player_ids))
        max_period = self._league_data()['status'].get(
            'finalScoringPeriod', int(self.week)
        )
        for start in range(0, len(player_ids), 50):
            batch = player_ids[start:start + 50]
            data = self.client.get_player_card(batch, max_period)
            for entry in data.get('players', []):
                player = self._player_payload(entry)
                if player.get('id') is not None:
                    records[player['id']] = entry
        return records

    def _draft_records(self):
        draft_data = self._draft_data()
        draft_detail = draft_data.get('draftDetail', {})
        if not draft_detail.get('drafted', bool(draft_detail.get('picks'))):
            return []
        picks = draft_detail.get('picks', [])
        players = self._player_card_records(
            pick.get('playerId') for pick in picks if pick.get('playerId') is not None
        )
        records = []
        for pick in picks:
            player = players.get(pick.get('playerId'))
            if player is None:
                raise ValueError(
                    f'ESPN did not return drafted player {pick.get("playerId")}'
                )
            _, _, player_id = self._player_identity(player)
            records.append({
                'pick': pick.get('overallPickNumber') or pick.get('id'),
                'round': pick.get('roundId'),
                'manager_id': pick.get('teamId'),
                'player_id': player_id,
            })
        return records

    def _player_pool_filters(self):
        if self.sport == 'baseball':
            return [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 19],
                [13, 14, 15],
            ]
        return [None]

    def _player_pool_records(self):
        data = self._league_data()
        scoring_period = int(self.week) if self.sport == 'football' else int(
            data.get('scoringPeriodId', 0)
        )
        records = {}
        for slot_ids in self._player_pool_filters():
            player_filter = {
                'filterStatus': {
                    'value': ['ONTEAM', 'FREEAGENT', 'WAIVERS'],
                },
                'limit': 250,
                'sortPercOwned': {'sortPriority': 1, 'sortAsc': False},
                'sortDraftRanks': {
                    'sortPriority': 100,
                    'sortAsc': True,
                    'value': 'STANDARD',
                },
            }
            if slot_ids is not None:
                player_filter['filterSlotIds'] = {'value': slot_ids}
            response = self.client.league_get(
                params={
                    'view': 'kona_player_info',
                    'scoringPeriodId': scoring_period,
                },
                headers={
                    'x-fantasy-filter': json.dumps({'players': player_filter}),
                },
            )
            for entry in response.get('players', []):
                player = self._player_payload(entry)
                if player.get('id') is not None:
                    records[player['id']] = entry

        referenced = set()
        for team in data['teams']:
            referenced.update(
                entry.get('playerId') or self._player_payload(entry).get('id')
                for entry in team.get('roster', {}).get('entries', [])
            )
        draft_detail = self._draft_data().get('draftDetail', {})
        referenced.update(
            pick.get('playerId') for pick in draft_detail.get('picks', [])
        )
        referenced.discard(None)
        records.update(self._player_card_records(referenced - set(records)))
        return list(records.values())

    @staticmethod
    def _stat_entry(player, scoring_period, source):
        candidates = [
            stat for stat in player.get('stats', [])
            if stat.get('scoringPeriodId') == scoring_period
            and stat.get('statSourceId') == source
        ]
        if not candidates:
            return {}
        candidates.sort(key=lambda x: x.get('statSplitTypeId', 99))
        return candidates[0]

    def _pro_team_data(self):
        return {
            team.get('id'): team
            for team in self._pro_schedule()['settings']['proTeams']
        }

    def _opponent(self, player, pro_teams):
        team_id = player.get('proTeamId')
        team = pro_teams.get(team_id, {})
        scoring_period = int(self.week) if self.sport == 'football' else int(
            self._league_data().get('scoringPeriodId', 0)
        )
        games = team.get('proGamesByScoringPeriod', {}).get(
            str(scoring_period), []
        )
        if not games:
            return 'BYE' if team_id else None
        game = games[0]
        opponent_id = game.get('homeProTeamId')
        if opponent_id == team_id:
            opponent_id = game.get('awayProTeamId')
        return pro_teams.get(opponent_id, {}).get('abbrev')

    def _player_image(self, player, team_abbrev):
        if self.sport == 'football' and player.get('defaultPositionId') == 16:
            if not team_abbrev:
                return ''
            return (
                'https://a.espncdn.com/i/teamlogos/nfl/500/'
                f'{team_abbrev.lower()}.png'
            )
        return (
            f'https://a.espncdn.com/i/headshots/{SPORT_API_NAMES[self.sport]}/'
            f'players/full/{player.get("id")}.png'
        )

    def _player_records(self):
        entries = self._player_pool_records()
        if not entries:
            raise ValueError('ESPN returned an empty player pool')
        pro_teams = self._pro_team_data()
        info_records = []
        stat_records = []
        seen = set()

        for entry in entries:
            player = self._player_payload(entry)
            name, position, player_id = self._player_identity(entry)
            if player_id in seen:
                print(f'warning: duplicate player_id ({player_id})')
                continue
            seen.add(player_id)

            pro_team = pro_teams.get(player.get('proTeamId'), {})
            team_abbrev = pro_team.get('abbrev')
            ownership = player.get('ownership', {})
            injury_status = str(player.get('injuryStatus') or '').upper()
            injury = INJURY_MAP.get(injury_status, injury_status or None)

            projection = None
            previous_score = None
            total_points = None
            average_points = None
            if self.sport == 'football':
                if int(self.week) == 0:
                    season = self._stat_entry(player, 0, 1)
                else:
                    projection_stat = self._stat_entry(player, int(self.week), 1)
                    previous_stat = self._stat_entry(
                        player, max(int(self.week) - 1, 0), 0
                    )
                    projection = parse_float(projection_stat.get('appliedTotal'))
                    previous_score = parse_float(previous_stat.get('appliedTotal'))
                    season = self._stat_entry(player, 0, 0)
                total_points = parse_float(season.get('appliedTotal'), 0)
                average_points = parse_float(season.get('appliedAverage'), 0)
            elif self.sport == 'baseball':
                source = 1 if int(self.week) == 0 else 0
                season = self._stat_entry(player, 0, source)
                total_points = parse_float(season.get('appliedTotal'), 0)
                average_points = parse_float(season.get('appliedAverage'), 0)

            info_records.append({
                'id': player_id,
                'name': name,
                'pos': position,
                'team': team_abbrev,
                'img': self._player_image(player, team_abbrev),
            })
            stat_records.append({
                'week': self.week,
                'id': player_id,
                'injury': injury,
                'opp': self._opponent(player, pro_teams),
                'proj': projection,
                'prev_score': previous_score,
                'roster': parse_float(ownership.get('percentOwned'), 0),
                'roster_change': parse_float(ownership.get('percentChange'), 0),
                'total_pts': total_points,
                'avg_pts': average_points,
            })
        return info_records, stat_records

    def _write_schedule(self, records):
        included_weeks = {int(record['week']) for record in records}
        self.update_data(
            records,
            self.path['schedule'],
            sort=lambda x: (
                bool(x['playoff']), parse_int(x['week']), x['matchup_idx'],
            ),
            filter=lambda x: int(x['week']) not in included_weeks,
            columns=[
                'week', 'matchup_idx', 'playoff', 'home', 'home_score',
                'away', 'away_score',
            ],
        )

    def _write_members(self, records):
        self.write_data(
            records,
            self.path['members'],
            sort=lambda x: x['id'],
            columns=['id', 'manager', 'team_name', 'abbrev', 'division', 'img'],
        )

    def _write_rosters(self, records):
        self.update_data(
            records,
            self.path['rosters'],
            sort=lambda x: (
                parse_int(x['week'], 0), x['manager_id'], x['slot_idx'],
            ),
            filter=lambda x: str(x['week']) != self.week,
            columns=['week', 'manager_id', 'slot_idx', 'player_id', 'aquired'],
        )

    def fetch_league(self):
        """Validate all league payloads before replacing any stored dataset."""
        print('--> fetching league from ESPN API')
        members = self._members_records()
        schedule = self._schedule_records()
        rosters = self._roster_records()
        self._write_members(members)
        self._write_schedule(schedule)
        self._write_rosters(rosters)
        if self.week == '0':
            self.fetch_draft()

    def fetch_schedule(self):
        print('--> fetching schedule from ESPN API')
        self._write_schedule(self._schedule_records())

    def fetch_members(self):
        print('--> fetching members from ESPN API')
        self._write_members(self._members_records())

    def fetch_rosters(self):
        print('--> fetching rosters from ESPN API')
        self._write_rosters(self._roster_records())

    def fetch_draft(self):
        print('--> fetching draft from ESPN API')
        self.write_data(
            self._draft_records(),
            self.path['draft'],
            sort=lambda x: parse_int(x['pick'], 0),
            columns=['pick', 'round', 'manager_id', 'player_id'],
        )

    def fetch_players(self):
        print('--> fetching players from ESPN API')
        player_info, player_stats = self._player_records()
        self.insert_data(
            player_info,
            self.path['player_info'],
            sort=lambda x: x['id'],
            key=lambda x: x['id'],
            columns=['id', 'name', 'pos', 'team', 'img'],
        )
        self.update_data(
            player_stats,
            self.path['player_stats'],
            sort=lambda x: (parse_int(x['week'], 0), x['id']),
            filter=lambda x: str(x['week']) != self.week,
            columns=[
                'week', 'id', 'injury', 'opp', 'proj', 'prev_score',
                'roster', 'roster_change', 'total_pts', 'avg_pts',
            ],
        )
