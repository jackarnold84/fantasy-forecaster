import numpy as np
from model.players.universe import PlayerUniverse
from model.league.utils import get_team_name


class Team:

    def __init__(
        self, id, manager_name, nickname, abbrev, division, img, 
        week, schedule_records, roster_records, draft_records, n_teams,
        player_universe: PlayerUniverse,
    ):
        self.id = str(id)
        self.name = get_team_name(manager_name)
        self.nickname = nickname
        self.abbrev = abbrev.upper()
        self.division = division
        self.img = img
        self.week = int(week)
        self.n_teams = n_teams
        self.player_universe = player_universe

        self.scores = {}
        self.roster = {w: [] for w in range(0, self.week + 1)}

        schedule_records = [x for x in schedule_records if x['week'] < self.week]
        for x in schedule_records:
            if get_team_name(x['home']) == self.name:
                self.scores[x['week']] = x['home_score']
            if get_team_name(x['away']) == self.name:
                self.scores[x['week']] = x['away_score']

        for x in roster_records:
            if x['week'] == 0:
                continue
            if str(x['manager_id']) == self.id:
                self.roster[x['week']].append({
                    'id': x['player_id'],
                    'aquired': x['aquired'],
                })

        for x in draft_records:
            if str(x['manager_id']) == self.id:
                self.roster[0].append({
                    'id': x['player_id'],
                    'aquired': 'draft',
                })

    def get_roster(self, week):
        return [x['id'] for x in self.roster[week]]

    def get_roster_aquisitions(self, week):
        return {
            'draft': len([x for x in self.roster[week] if x['aquired'] == 'Draft']),
            'free_agency': len([x for x in self.roster[week] if x['aquired'] == 'Free Agency']),
            'trade': len([x for x in self.roster[week] if x['aquired'] == 'Trade']),
        }

    def get_team_rating(self, week, position=None, rating_type='normal'):
        players = self.get_roster(week)
        return self.player_universe.get_team_rating(players, week, position, rating_type, n_teams=self.n_teams)
    
    def get_scoring_average(self, week):
        scores = [self.scores[w] for w in self.scores if w < week]
        return np.mean(scores) if scores else None
