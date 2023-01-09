import pandas as pd
from jinja2 import Template
import os
from metrics.players.processor import Processor
import metrics.players.utils as utils
import metrics.players.weights as weights


class Evaluator:

    def __init__(self, year, week, total_weeks=18):
        self.year = year
        self.max_week = week + 1
        self.total_weeks = total_weeks
        self.player_processor = Processor(year, week)
        self.players = self.player_processor.players
        self.players_calc = Processor(year, week).players
        self.evaluate()
        self.player_processor.write_to_file()
        self.build_ratings_report()

    # get player information
    def get_moving_avg(self, id, week, type=''):
        week = min(week, self.total_weeks - 1)
        scores = [self.players_calc[id]['score'][i] for i in range(1, week + 1)]
        return utils.wma(scores, type)

    def get_moving_projection(self, id, week, type='sharp'):
        week = min(week, self.total_weeks - 1)
        projs = [self.players_calc[id]['projection'][i] for i in range(1, week + 1)]
        projs = [x if x is not None and x > 1.0 else None for x in projs]
        return utils.wma(projs, type)

    def get_total_projection(self, id, week):
        week = min(week, self.total_weeks - 1)
        projs = [self.players_calc[id]['projection'][i] for i in range(1, week + 1)]
        projs = [x for x in projs if x is not None]
        return sum(projs)

    def get_expected_rostered(self, id, week):
        week = min(week, self.total_weeks - 1)
        rosts = [self.players_calc[id]['rostered'][i] for i in range(1, week + 1)]
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


    # evaluate players
    def evaluate(self):

        # filter out injuries
        for w in range(1, min(self.max_week + 1, self.total_weeks)):
            for id in self.players_calc:
                status = self.players_calc[id]['status'][w]
                if status and status != 'active':
                    self.players_calc[id]['projection'][w] = None
                    self.players_calc[id]['score'][w] = None

        # compute additional stats
        for id in self.players_calc:
            for z in utils.z_stats:
                if z not in self.players_calc[id]:
                    self.players_calc[id][z] = {}
            self.players_calc[id]['z'] = {z: {} for z in utils.z_stats}
            for w in range(1, self.max_week + 1):
                self.players_calc[id]['moving_avg'][w] = self.get_moving_avg(id, w)
                self.players_calc[id]['sharp_moving_avg'][w] = self.get_moving_avg(id, w, type='sharp')
                self.players_calc[id]['moving_projection'][w] = self.get_moving_projection(id, w)
                self.players_calc[id]['avg_projection'][w] = self.get_moving_projection(id, w, type='flat')
                self.players_calc[id]['total_projection'][w] = self.get_total_projection(id, w)
                self.players_calc[id]['expected_rostered'][w] = self.get_expected_rostered(id, w)
                self.players_calc[id]['moving_avg'][w] = self.get_moving_avg(id, w)

        # compute z score statistics
        for w in range(1, min(self.max_week + 1, self.total_weeks + 1)):
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

        # compute rating
        for id in self.players_calc:
            self.players_calc[id]['rating'] = {}
            self.players_calc[id]['sharp_rating'] = {}
            self.players_calc[id]['z']['rating'] = {}
            self.players_calc[id]['z']['sharp_rating'] = {}

            # weekly ratings, sharp ratings
            for w in range(0, self.max_week):
                tot = 0
                tot_weight = 0
                for stat in weights.normal_weights[w]:
                    wk = min(max(w + utils.z_stats_week_adj[stat], 1), self.total_weeks)
                    z = self.players_calc[id]['z'][stat][wk]
                    if z is not None:
                        tot += z * weights.normal_weights[w][stat]
                        tot_weight += weights.normal_weights[w][stat]
                rating = tot / tot_weight if tot_weight else None
                self.players_calc[id]['rating'][w] = rating

                tot = 0
                tot_weight = 0
                for stat in weights.short_term_weights[w]:
                    wk = min(max(w + utils.z_stats_week_adj[stat], 1), self.total_weeks)
                    z = self.players_calc[id]['z'][stat][wk]
                    if z is not None:
                        tot += z * weights.short_term_weights[w][stat]
                        tot_weight += weights.short_term_weights[w][stat]
                rating = tot / tot_weight if tot_weight else None
                self.players_calc[id]['sharp_rating'][w] = rating


        # compute z score based rating
        for w in range(0, self.max_week):
            pos_population = {
                p: {'rating': [], 'sharp_rating': []} for p in utils.positions
            }

            # fill population by position
            for id in self.players_calc:
                pos = self.players_calc[id]['position']
                for stat in ['rating', 'sharp_rating']:
                    x = self.players_calc[id][stat]
                    x = x[w] if type(x) == dict else x
                    if x is not None:
                        pos_population[pos][stat].append(x)

            # compute population statistics
            for p in pos_population:
                for s in pos_population[p]:
                    pos_population[p][s] = {
                        'avg': utils.mean(pos_population[p][s], top=utils.position_pool_size[p]),
                        'sd': utils.std(pos_population[p][s], top=utils.position_pool_size[p]),
                        'count': min(len(pos_population[p][s]), utils.position_pool_size[p]),
                    }

            # add z based ratings to players
            for id in self.players_calc:
                pos = self.players_calc[id]['position']
                wk = min(w + 1, self.total_weeks)
                status = self.players_calc[id]['status'][wk]
                for stat in ['rating', 'sharp_rating']:
                    x = self.players_calc[id][stat]
                    x = x[w] if type(x) == dict else x
                    z = utils.z_score(
                        x,
                        pos_population[pos][stat]['avg'], 
                        pos_population[pos][stat]['sd'],
                        pos_population[pos][stat]['count'],
                        new_avg=utils.rating_mean,
                        new_sd=utils.rating_sd
                    )
                    if z and z > 0:
                        z = z * utils.status_correction[stat][status]
                    self.players_calc[id]['z'][stat][w] = z

        # add ratings to players
        for id in self.players:
            self.players[id]['preseason_rating'] = utils.rnd(self.players_calc[id]['z']['rating'][0])
            self.players[id]['rating'] = {w: None for w in range(1, self.total_weeks + 1)}
            self.players[id]['sharp_rating'] = {w: None for w in range(1, self.total_weeks + 1)}
            for w in range(1, self.max_week):
                self.players[id]['rating'][w] = utils.rnd(self.players_calc[id]['z']['rating'][w])
                self.players[id]['sharp_rating'][w] = utils.rnd(self.players_calc[id]['z']['sharp_rating'][w])        


    # build report that lists player ratings by week by position
    def build_ratings_report(self):

        tables = {w: {} for w in ['Preseason'] + list(range(1, self.max_week))}

        for w in ['Preseason'] + list(range(1, self.max_week)):
            if w == 'Preseason':
                data = [
                    [x['player_name'], x['position'], x['team'], x['preseason_rating'], '--']
                    for x in self.players.values()
                ]
            else:
                data = [
                    [x['player_name'], x['position'], x['team'], x['rating'][w], x['sharp_rating'][w]]
                    for x in self.players.values()
                ]
            df = pd.DataFrame(data, columns=['Name', 'Pos', 'Team', 'Rating', 'Live'])
            
            for p in utils.positions:
                df_pos =  df[df['Pos'] == p]
                df_pos = df_pos.sort_values('Rating', ascending=False).reset_index(drop=True)
                df_pos = df_pos.iloc[0:utils.position_pool_size[p]]
                tables[w][p] = df_pos

        # write to html file
        with open('templates/player-data.html', 'r') as file:
            template_text = file.read()

        template = Template(template_text)
        html = template.render(
            tables=tables,
            color_map=utils.position_color_map
        )

        outdir = 'reports/players/%d/' % (self.year)
        outfile = 'reports/players/%d/ratings.html' % (self.year)
        os.makedirs(outdir, exist_ok=True)
        with open(outfile, "w") as html_file:
            html_file.write(html)

        print('--> Player ratings page built (%s)' %  outfile)
