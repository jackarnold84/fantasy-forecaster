import re
import json
import os
import metrics.league.reader as reader


def map_player_id(player_name, position):
    player_name = re.sub(r'[^A-Za-z0-9 ]+', '', player_name).replace('  ', ' ').strip()
    player_name = player_name.replace(' ', '')
    return '%s-%s' % (player_name, position)


class Processor:

    def __init__(self, league_id, week, draft_recap_week=1, total_weeks=18):
        self.teams = {}
        self.league_id = league_id
        self.week = week
        self.total_weeks = total_weeks
        self.draft_recap_week = draft_recap_week
        self.process_league_data()
        self.write_to_file()

    def create_team(self, manager_name):
        id = self.map_manager_id(manager_name)
        self.teams[id] = {
            'manager_name': manager_name,
            'team_number': None,
            'division': None,
            'team_name': {w: None for w in range(1, self.total_weeks + 1)},
            'team_abbrev': {w: None for w in range(1, self.total_weeks + 1)},
            'roster': {w: [] for w in range(1, self.total_weeks + 1)},
            'draft': []
        }

    def map_manager_id(self, manager_name):
        aliases = reader.config['leagues'][self.league_id]['aliases']
        if manager_name in aliases:
                return aliases[manager_name]
        else:
            parts = manager_name.split(' ')
            return parts[0] if len(parts[0]) <= 8 else parts[0][0:8]

    def process_league_data(self):

        # weekly files
        for w in range(1, self.week + 1):
            member_file = 'data/leagues/%s/members/week%d.csv' % (self.league_id, w)
            roster_file = 'data/leagues/%s/rosters/week%d.csv' % (self.league_id, w)

            member_data = reader.read_members(member_file)
            roster_data = reader.read_rosters(roster_file)

            name_to_id = {}

            # process member data
            for x in member_data:
                id = self.map_manager_id(x['manager_name'])
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
        draft_file = 'data/leagues/%s/draft.csv' % self.league_id
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


    def write_to_file(self):
        outdir = 'reports/%s' % (self.league_id)
        outfile = 'reports/%s/teams.json' % (self.league_id)
        os.makedirs(outdir, exist_ok=True)
        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump(self.teams, f, ensure_ascii=False, indent=2)
