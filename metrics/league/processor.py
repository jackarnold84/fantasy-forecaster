import reader
import re
import json


def map_player_id(player_name, position):
    player_name = re.sub(r'[^A-Za-z0-9 ]+', '', player_name).replace('  ', ' ').strip()
    player_name = player_name.replace(' ', '')
    return '%s-%s' % (player_name, position)

def map_manager_id(manager_name):
    # TODO: map aliases
    return manager_name


class League:

    def __init__(self, league_id, week, draft_recap_week=1):
        self.teams = {}
        self.league_id = league_id
        self.week = week
        self.total_weeks = 17
        self.draft_recap_week = draft_recap_week
        self.process_league_data()
        self.write_to_file('%s.json' % league_id)

    def create_team(self, manager_name):
        id = map_manager_id(manager_name)
        self.teams[id] = {
            'manager_name': manager_name,
            'team_number': None,
            'division': None,
            'team_name': {w: None for w in range(1, self.total_weeks + 1)},
            'team_abbrev': {w: None for w in range(1, self.total_weeks + 1)},
            'roster': {w: [] for w in range(1, self.total_weeks + 1)},
            'draft': []
        }

    def process_league_data(self):

        # weekly files
        for w in range(1, self.week + 1):
            member_file = 'members/week%d.csv' % w
            roster_file = 'rosters/week%d.csv' % w

            member_data = reader.read_members(member_file)
            roster_data = reader.read_rosters(roster_file)

            name_to_id = {}

            # process member data
            for x in member_data:
                id = map_manager_id(x['manager_name'])
                if id not in self.teams:
                    self.create_team(x['manager_name'])

                # team number, division
                self.teams[id]['team_number'] = x['team_number']
                self.teams[id]['division'] = x['division']

                # team name, abbreviation
                self.teams[id]['team_name'][w] = x['team_name']
                self.teams[id]['team_abbrev'][w] = x['team_abbrev']
                name_to_id[x['team_name']] = id

            # process roster data
            for x in roster_data:
                id = name_to_id[x['team_name']]
                player_id = map_player_id(x['player_name'], x['position'])
                self.teams[id]['roster'][w].append({
                    'id': player_id,
                    'position': x['position'],
                    'aquired': x['aquired'],
                })

        # draft
        draft_file = 'draft.csv'
        draft_data = reader.read_draft_recap(draft_file)

        name_to_id = {}
        for t in self.teams:
            name = self.teams[t]['team_name'][self.draft_recap_week]
            name_to_id[name] = t

        # process member data
        for x in draft_data:
            id = name_to_id[x['team_name']]
            player_id = map_player_id(x['player_name'], x['position'])
            self.teams[id]['draft'].append({
                    'id': player_id,
                    'position': x['position'],
                    'overall_pick': x['overall_pick'],
                })


    def write_to_file(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.teams, f, ensure_ascii=False, indent=2)


l = League(league_id='purdue-league-2022', week=15, draft_recap_week=13)
