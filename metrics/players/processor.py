import re
import json
import os
import metrics.players.reader as reader


# utils
def map_player_id(player_name, position):
    player_name = re.sub(r'[^A-Za-z0-9 ]+', '', player_name).replace('  ', ' ').strip()
    player_name = player_name.replace(' ', '')
    return '%s-%s' % (player_name, position)

def get_score_blanks(scores, opponents, week):
    blanks = []
    for i in range(1, week + 1):
        if opponents[i] != 'BYE' and scores[i] is None:
            blanks.append(i)
    return blanks

def compute_season_stats(scores, week):
    games_played = 0
    total = 0
    for w in scores:
        if w > week or scores[w] is None:
            continue
        else:
            games_played += 1
            total += scores[w]
    if games_played == 0:
        return 0, 0, 0
    avg = total / games_played
    return total, games_played, avg

def approx_equal(x, y, buffer=1.0):
    return abs(x - y) <= buffer


def get_status(proj, score, health, opp):
        if (proj and proj >= 1.0) or (score and score >= 1.0):
            return 'active'
        elif health and health == 'IR':
            return 'injured'
        elif opp and opp == 'BYE':
            return 'bye'
        elif health and health in ['O', 'Q', 'D']:
            return 'unhealthy'
        elif proj is not None or score is not None or opp is not None:
            return 'inactive'
        else:
            return None


class Processor:

    def __init__(self, year, week, total_weeks=18):
        self.players = {}
        self.year = year
        self.week = week
        self.total_weeks = total_weeks
        self.process_player_list()
        self.write_to_file()


    def create_player(self, player_name, position, team):
        id = map_player_id(player_name, position)
        self.players[id] = {
            'player_name': player_name,
            'position': position,
            'team': team,
            'projection': {w: None for w in range(1, self.total_weeks + 1)},
            'score': {w: None for w in range(1, self.total_weeks + 1)},
            'health': {w: None for w in range(1, self.total_weeks + 1)},
            'status': {w: None for w in range(1, self.total_weeks + 1)},
            'opponent': {w: None for w in range(1, self.total_weeks + 1)},
            'rostered': {w: None for w in range(1, self.total_weeks + 1)},
            'started': {w: None for w in range(1, self.total_weeks + 1)},
            'games_played': {w: None for w in range(1, self.total_weeks + 1)},
            'season_total': {w: None for w in range(1, self.total_weeks + 1)},
            'season_avg': {w: None for w in range(1, self.total_weeks + 1)},
            'preseason_total': None,
            'preseason_avg': None,
        }


    def process_player_list(self):

        # preseason
        preseason_file = 'data/players/%d/list/preseason.csv' % self.year
        preseason_data = reader.read_player_list(preseason_file)

        for x in preseason_data:
            id = map_player_id(x['player_name'], x['position'])
            if id not in self.players:
                self.create_player(x['player_name'], x['position'], x['team'])

            # projection, score
            self.players[id]['preseason_total'] = x['season_total']
            self.players[id]['preseason_avg'] = x['season_avg']


        # weekly files
        for w in range(1, self.week + 2):
            list_file = 'data/players/%d/list/week%d.csv' % (self.year, w)
            stat_file = 'data/players/%d/stats/week%d.csv' % (self.year, w)

            list_data = reader.read_player_list(list_file)
            if w <= self.week:
                stat_data = reader.read_player_stats(stat_file)
            else:
                stat_data = []

            # process player list data
            for x in list_data:
                id = map_player_id(x['player_name'], x['position'])
                if id not in self.players:
                    self.create_player(x['player_name'], x['position'], x['team'])

                # projection, score
                self.players[id]['projection'][w] = x['projection']
                if w > 1:
                    self.players[id]['score'][w - 1] = x['prev_score']

                # opponent
                self.players[id]['opponent'][w] = x['opponent']

                # health
                self.players[id]['health'][w] = x['health']

                # rostered, started
                self.players[id]['rostered'][w] = x['rostered']
                self.players[id]['started'][w] = x['started']

                # season total, avg, games played (for prev week)
                if w > 1:
                    self.players[id]['season_total'][w-1] = x['season_total']
                    self.players[id]['season_avg'][w-1] = x['season_avg']
                    self.players[id]['games_played'][w-1] = x['games_played']
            
            # process player stat data
            for x in stat_data:
                id = map_player_id(x['player_name'], x['position'])
                if id not in self.players:
                    self.create_player(x['player_name'], x['position'], x['team'])

                # projection, score
                self.players[id]['projection'][w] = x['projection']
                self.players[id]['score'][w] = x['score']

                # opponent
                self.players[id]['opponent'][w] = x['opponent']

        # corrections
        # fill missing scores
        for w in range(1, self.week + 1):
            for p in self.players:
                if self.players[p]['season_total'][w] is not None:
                    total, games_played, avg = compute_season_stats(self.players[p]['score'], w)
                    if not approx_equal(self.players[p]['season_total'][w], total):
                        blanks = get_score_blanks(self.players[p]['score'], self.players[p]['opponent'], w)
                        n_to_fill = max(self.players[p]['games_played'][w] - games_played, 0)
                        if n_to_fill > 0:
                            fill = round((self.players[p]['season_total'][w] - total) / n_to_fill, 2)
                            for k in blanks[-n_to_fill:]:
                                self.players[p]['score'][k] = fill

        # fill missing season totals
        for w in range(1, self.week + 1):
            for p in self.players:
                if self.players[p]['season_total'][w] is None:
                    total, games_played, avg = compute_season_stats(self.players[p]['score'], w)
                    self.players[p]['season_total'][w] = round(total, 2) if total else 0
                    self.players[p]['games_played'][w] = games_played if games_played else 0
                    self.players[p]['season_avg'][w] = round(avg, 2) if avg else 0

        # fill in status
        for w in range(1, self.week + 1):
            for p in self.players:
                self.players[p]['status'][w] = get_status(
                    self.players[p]['projection'][w], 
                    self.players[p]['score'][w], 
                    self.players[p]['health'][w], 
                    self.players[p]['opponent'][w]
                )


    def write_to_file(self):
        outdir = 'reports/players/%d' % (self.year)
        outfile = 'reports/players/%d/players.json' % (self.year)
        os.makedirs(outdir, exist_ok=True)
        with open(outfile, 'w', encoding='utf-8') as f:
            json.dump(self.players, f, ensure_ascii=False, indent=2)
