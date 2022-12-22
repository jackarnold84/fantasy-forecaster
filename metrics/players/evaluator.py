import numpy as np
import json
from metrics.players.processor import Processor
import metrics.players.utils as utils


class Evaluator:

    def __init__(self, year, week):
        self.players = Processor(year, week).players
        self.players_calc = Processor(year, week).players
        self.max_week = week
        self.evaluate()

    # get player information

    def get_projection(self, id, week):
        return self.players[id]['projection'][week]

    def get_season_total(self, id, week):
        return self.players[id]['season_total'][week]

    def get_moving_avg(self, id, week, type=''):
        scores = [self.players[id]['score'][i] for i in range(1, week + 1)]
        return utils.wma(scores, type)

    def get_moving_projection(self, id, week, type='sharp'):
        projs = [self.players[id]['projection'][i] for i in range(1, week + 1)]
        projs = [x if x is not None and x > 1.0 else None for x in projs]
        return utils.wma(projs, type)

    def get_expected_rostered(self, id, week):
        rosts = [self.players[id]['rostered'][i] for i in range(1, week + 1)]
        diffs = utils.diffs_with_blanks(rosts)
        current = utils.recent_instance(rosts)
        trend = utils.wma(diffs[-4:], type='sharp')
        if trend:
            exp = utils.rostered_sigmoid(current + trend)
            if trend > 0:
                exp = max(current, exp)
            elif trend < 0:
                exp = min(current, exp)
            return exp
        else:
            return current

    def get_preseason_total(self, id, week):
        return self.players[id]['proj_season_total']

    def get_preseason_avg(self, id, week):
        return self.players[id]['proj_season_avg']


    # evaluate players

    def evaluate(self):

        # compute additional stats
        for id in self.players:
            for z in utils.z_stats:
                if z not in self.players_calc[id]:
                    self.players_calc[id][z] = {}
            self.players_calc[id]['z'] = {z: {} for z in utils.z_stats}
            for w in range(1, self.max_week + 1):
                self.players_calc[id]['moving_avg'][w] = self.get_moving_avg(id, w)
                self.players_calc[id]['sharp_moving_avg'][w] = self.get_moving_avg(id, w, type='sharp')
                self.players_calc[id]['moving_projection'][w] = self.get_moving_projection(id, w)
                self.players_calc[id]['expected_rostered'][w] = self.get_expected_rostered(id, w)
                self.players_calc[id]['moving_avg'][w] = self.get_moving_avg(id, w)

        # compute z score statistics
        for w in range(1, self.max_week + 1):
            pos_population = {
                p: {z: [] for z in utils.z_stats} for p in utils.positions
            }

            # fill population by position
            for id in self.players_calc:
                pos = self.players_calc[id]['position']
                for stat in utils.z_stats:
                    x = self.players_calc[id][stat]
                    x = x[w] if type(x) == dict else x
                    if x is not None and x > utils.z_stats_thresholds[stat]:
                        pos_population[pos][stat].append(x)

            # compute population statistics
            for p in pos_population:
                for s in pos_population[p]:
                    pos_population[p][s] = {
                        'avg': utils.mean(pos_population[p][s]),
                        'sd': utils.std(pos_population[p][s]),
                        'count': len(pos_population[p][s])
                    }

            # add z scores to players
            for id in self.players_calc:
                pos = self.players_calc[id]['position']
                for stat in utils.z_stats:
                    x = self.players_calc[id][stat]
                    x = x[w] if type(x) == dict else x
                    z = utils.z_score(
                        x,
                        pos_population[pos][stat]['avg'], 
                        pos_population[pos][stat]['sd'],
                        pos_population[pos][stat]['count'],
                    )
                    self.players_calc[id]['z'][stat][w] = z


        test = self.players_calc['ChrisOlave-WR']
        print(json.dumps(test, indent=2))

        
            

            
                


