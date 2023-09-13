import numpy as np
import pandas as pd
from model.players.player import Player
from model.players.utils import z_score, bound
from model.players.weights import (
    team_position_weights, position_group_list, stat_list,
    player_rating_mean, player_rating_sd, team_rating_mean, team_rating_sd,
    get_stat_weight, get_position_pool_size, get_team_position_weight,
)


class PlayerUniverse:

    def __init__(self, sport_tag, week):
        print('--> init player universe')
        self.sport, self.year = sport_tag.split('-')
        self.week = int(week)
        self.players = {}

        # read data
        player_info_path = f'data/{self.sport}-{self.year}/players/info.csv'
        player_stats_path = f'data/{self.sport}-{self.year}/players/stats.csv'
        info_records = pd.read_csv(player_info_path).to_dict('records')
        stat_records = pd.read_csv(player_stats_path).to_dict('records')

        stat_records_by_id = {}
        for x in stat_records:
            if x['id'] in stat_records_by_id:
                stat_records_by_id[x['id']].append(x)
            else:
                stat_records_by_id[x['id']] = [x]

        # fill players
        for x in info_records:
            if x['id'] not in stat_records_by_id:
                continue
            self.players[x['id']] = Player(
                self.sport, x['id'], x['name'],
                x['pos'], x['team'], x['img'],
                stat_records_by_id[x['id']],
            )

        # compute player ratings
        self.compute_player_ratings()

    def compute_player_ratings(self):
        print('--> computing player ratings')
        positions = position_group_list[self.sport]
        for pos in positions:
            eval_group = [
                p for p in self.players.values() if p.pos_group == pos
            ]
            pool_size = get_position_pool_size(pos, self.sport)

            for week in range(0, self.week + 1):
                for rating_type in ['normal', 'sharp']:
                    # get parameters for stat relative to group
                    stat_params = {}
                    for stat in stat_list:
                        values = [p.get_stat(stat, week) for p in eval_group]
                        values = [v for v in values if v is not None]
                        if len(values) > 8:
                            stat_params[stat] = {
                                'mean': np.mean(values),
                                'sd': np.std(values),
                                'weight': get_stat_weight(stat, week, rating_type),
                            }

                    # compute raw ratings
                    for p in eval_group:
                        weights_sum = 0
                        value_sum = 0
                        for stat in stat_params:
                            value = p.get_stat(stat, week)
                            if value is not None:
                                weight = stat_params[stat]['weight']
                                weights_sum += weight
                                value_sum += z_score(
                                    value,
                                    stat_params[stat]['mean'],
                                    stat_params[stat]['sd'],
                                ) * weight
                        raw_rating = value_sum / weights_sum if weights_sum else None
                        p.raw_rating[week] = raw_rating

                    # set ratings
                    values = [p.raw_rating[week] for p in eval_group]
                    values = [v for v in values if v is not None]
                    if not values:
                        continue
                    values = sorted(values, reverse=True)[0:pool_size]
                    mean, sd = np.mean(values), np.std(values)
                    for p in eval_group:
                        raw_rating = p.raw_rating[week]
                        if raw_rating:
                            rating = z_score(
                                raw_rating, mean, sd, player_rating_mean, player_rating_sd,
                            )
                            rating = bound(rating, -20, 20)
                            if rating_type == 'sharp':
                                p.sharp_rating[week] = rating
                            else:
                                p.rating[week] = rating

    def get_team_rating(self, players, week, position=None, rating_type='normal', scale=True, n_teams=10):
        positions = [position] if position else position_group_list[self.sport]
        rating_sum = 0
        for pos in positions:
            eval_group = [
                p for p in players if p in self.players and self.players[p].pos_group == pos
            ]
            ratings = [
                self.players[p].get_rating(week, rating_type) or 0 for p in eval_group
            ]
            ratings = sorted(ratings, reverse=True)
            for i, r in enumerate(ratings):
                weight = get_team_position_weight(i, pos, self.sport)
                rating_sum += max(r, 0) * weight

        # scale rating
        rating = rating_sum
        if scale:
            tp_weights = team_position_weights[self.sport]
            weight_lists = [
                tp_weights[pos] for pos in tp_weights if pos in positions
            ]
            weights = [w for l in weight_lists for w in l]
            mean = sum(weights) * player_rating_mean
            sd = sum([(w**2) * (player_rating_sd**2) for w in weights])**0.5
            scaled_rating = z_score(
                rating_sum, mean, sd, team_rating_mean, team_rating_sd
            )
            scaled_rating += 5 * (n_teams - 10)
            rating = max(scaled_rating, 0)
        return rating
