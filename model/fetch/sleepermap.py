from difflib import SequenceMatcher

import requests
from db.db import read_s3
from fetch.utils import get_data_paths


class SleeperPlayerMapper:
    BASE_URL = "https://api.sleeper.app/v1"

    # Manual team mapping overrides: Sleeper team -> ESPN team
    TEAM_MAPPING = {
        'WAS': 'WSH',  # Washington Commanders
    }

    def read_data(self, path):
        df = read_s3(path)
        if df is None:
            return []
        return df.to_dict('records')

    def normalize_sleeper_team(self, sleeper_team):
        """Convert Sleeper team code to ESPN team code if override exists."""
        return self.TEAM_MAPPING.get(sleeper_team, sleeper_team)

    def __init__(self, sport_tag):
        self.sport, self.year = sport_tag.split('-')

        # read espn players
        paths = get_data_paths(self.sport, self.year, '')
        player_info_path = paths['player_info']
        self.player_info = self.read_data(player_info_path)

        # read sleeper players
        req_url = f"{self.BASE_URL}/players/nfl"
        print('--> fetching sleeper players')
        response = requests.get(req_url)
        response.raise_for_status()
        self.sleeper_players = response.json()

    def sleeper_id_to_player_id(self, sleeper_id):
        # Get sleeper player data
        sleeper_id_str = str(sleeper_id)
        if sleeper_id_str not in self.sleeper_players:
            return None

        sleeper_player = self.sleeper_players[sleeper_id_str]

        # Extract relevant fields from sleeper player
        sleeper_pos = sleeper_player.get('position', '').upper()
        sleeper_team = self.normalize_sleeper_team(
            sleeper_player.get('team', '').upper())
        sleeper_first = sleeper_player.get('first_name', '').lower().strip()
        sleeper_last = sleeper_player.get('last_name', '').lower().strip()

        # Special handling for DEF/DST position
        is_defense = sleeper_pos == 'DEF'

        # Search for matching player in player_info
        for player in self.player_info:
            # player_info format: id, name, pos, team, img
            # Dict keys match the CSV column names
            player_pos = str(player.get('pos', '')).upper()
            player_team = str(player.get('team', '')).upper()
            player_name = str(player.get('name', '')).lower()

            # Match on position and team
            # For defense, match DEF to DST
            if is_defense:
                if player_pos != 'DST' or player_team != sleeper_team:
                    continue
                if sleeper_last in player_name:
                    return player.get('id')
            else:
                if player_pos != sleeper_pos or player_team != sleeper_team:
                    continue
                # Match on name (flexible matching)
                # Check if both first and last name appear in the player name
                if sleeper_first in player_name and sleeper_last in player_name:
                    return player.get('id')

        # If no exact match found, try fuzzy matching
        return self.fuzzy_match_player(sleeper_id)

    def fuzzy_match_player(self, sleeper_id):
        # Get sleeper player data
        sleeper_id_str = str(sleeper_id)
        if sleeper_id_str not in self.sleeper_players:
            return None

        sleeper_player = self.sleeper_players[sleeper_id_str]

        # Extract relevant fields from sleeper player
        sleeper_pos = sleeper_player.get('position', '').upper()
        sleeper_team = self.normalize_sleeper_team(
            sleeper_player.get('team', '').upper())
        sleeper_first = sleeper_player.get('first_name', '').lower().strip()
        sleeper_last = sleeper_player.get('last_name', '').lower().strip()
        sleeper_full_name = f"{sleeper_first} {sleeper_last}"

        # Special handling for DEF/DST position
        is_defense = sleeper_pos == 'DEF'

        # Minimum similarity threshold (0.0 to 1.0)
        SIMILARITY_THRESHOLD = 0.6

        best_match = None
        best_similarity = 0.0

        # Search for fuzzy match among players with same position and team
        for player in self.player_info:
            player_pos = str(player.get('pos', '')).upper()
            player_team = str(player.get('team', '')).upper()
            player_name = str(player.get('name', '')).lower()

            # Position and team must match exactly
            # For defense, match DEF to DST
            if is_defense:
                if player_pos != 'DST' or player_team != sleeper_team:
                    continue
            else:
                if player_pos != sleeper_pos or player_team != sleeper_team:
                    continue

            # Calculate similarity ratio between names
            similarity = SequenceMatcher(
                None, sleeper_full_name, player_name).ratio()

            # Keep track of best match
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = player.get('id')

        # Return best match only if it meets the threshold
        if best_similarity >= SIMILARITY_THRESHOLD:
            return best_match

        return None
