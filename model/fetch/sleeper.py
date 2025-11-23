import pandas as pd
import requests
from config import Config
from db.db import read_s3, write_s3
from fetch.utils import get_data_paths, parse_float


class SleeperFetcher:
    BASE_URL = "https://api.sleeper.app/v1"

    def read_data(self, path):
        df = read_s3(path)
        if df is None:
            return []
        return df.to_dict('records')

    def write_data(self, data, path, sort):
        data = sorted(data, key=sort)
        df = pd.DataFrame(data)
        write_s3(df, path)

    def __init__(self, sport_tag, league_tag, week):
        league_config = Config().leagues[sport_tag][league_tag]
        self.sport, self.year = sport_tag.split('-')
        self.week = str(week)
        self.league_id = league_config['league_id']
        self.league_tag = league_tag
        self.n_regular_season_weeks = league_config['regular_season_weeks']
        self.n_weeks_per_playoff_matchup = league_config['weeks_per_playoff_matchup']
        self.playoff_start_week = self.n_regular_season_weeks + 1
        self.is_playoffs = int(self.week) > self.n_regular_season_weeks
        self.path = get_data_paths(self.sport, self.year, self.league_tag)

    def fetch_members(self):
        url = f"{self.BASE_URL}/league/{self.league_id}/users"
        print('--> fetching members')
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Fetch rosters to get roster_id mapping
        rosters_url = f"{self.BASE_URL}/league/{self.league_id}/rosters"
        rosters_response = requests.get(rosters_url)
        rosters_response.raise_for_status()
        rosters = rosters_response.json()

        # Create mapping from user_id to roster_id (which serves as team id)
        user_to_roster = {roster['owner_id']: roster['roster_id'] for roster in rosters}

        members_data = []
        for user in data:
            user_id = user.get('user_id')
            roster_id = user_to_roster.get(user_id, 0)
            display_name = user.get('display_name', '')
            metadata = user.get('metadata') or {}
            team_name = metadata.get('team_name') or display_name
            avatar = user.get('avatar')

            # Sleeper avatar format: https://sleepercdn.com/avatars/<avatar_id>
            img_url = f"https://sleepercdn.com/avatars/{avatar}" if avatar else ''

            members_data.append({
                'id': roster_id,
                'manager': display_name,
                'team_name': team_name,
                'abbrev': team_name[:3].upper() if team_name else '',
                'division': 'USA',  # temporary fix
                'img': img_url,
            })

        path = self.path['members']
        self.write_data(
            members_data,
            path,
            sort=lambda x: x['id'],
        )

    def fetch_schedule(self):
        print('--> fetching schedule')

        # Read members data to get manager names
        members_data = self.read_data(self.path['members'])
        roster_to_manager = {m['id']: m['manager'] for m in members_data}

        schedule_data = []

        # Fetch schedule for all regular season weeks
        for week in range(1, self.n_regular_season_weeks + 1):
            url = f"{self.BASE_URL}/league/{self.league_id}/matchups/{week}"
            response = requests.get(url)
            response.raise_for_status()
            matchups = response.json()

            # Group matchups by matchup_id
            matchup_groups = {}
            for matchup in matchups:
                matchup_id = matchup.get('matchup_id')
                if matchup_id not in matchup_groups:
                    matchup_groups[matchup_id] = []
                matchup_groups[matchup_id].append(matchup)

            # Process each matchup pair
            for matchup_idx, (matchup_id, teams) in enumerate(sorted(matchup_groups.items()), start=1):
                if len(teams) == 2:
                    # Determine home/away (first team is away, second is home by convention)
                    away_team = teams[0]
                    home_team = teams[1]

                    schedule_data.append({
                        'week': week,
                        'matchup_idx': matchup_idx,
                        'playoff': False,
                        'home': roster_to_manager.get(home_team['roster_id'], f"Team {home_team['roster_id']}"),
                        'home_score': parse_float(home_team.get('points', 0)),
                        'away': roster_to_manager.get(away_team['roster_id'], f"Team {away_team['roster_id']}"),
                        'away_score': parse_float(away_team.get('points', 0)),
                    })

        path = self.path['schedule']
        self.write_data(
            schedule_data,
            path,
            sort=lambda x: (x['week'], x['matchup_idx']),
        )
