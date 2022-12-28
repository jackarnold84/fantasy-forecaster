from metrics.league.processor import Processor
import metrics.league.utils as utils


class Evaluator:


    def __init__(self, league_id, week, players, draft_recap_week=1):
        
        self.teams = Processor(league_id, week, draft_recap_week).teams
        self.players = players
        self.week = week

        # evaluation dev:
        print('Team Evaluation:')
        week = 16
        for t in self.teams:
            team_rating = self.evaluate_team(self.teams[t]['roster'][week], week, position='QB', type='normal')
            print(t, round(team_rating, 1))



    def evaluate_team(self, players, week=None, position=None, type='normal', scale=True):
        assert(type in ['normal', 'sharp', 'preseason']), 'unknown type parameter'

        # get players by position (for calulation)
        players_by_position = {
            pos: [p.copy() for p in players if p['position'] == pos] 
            for pos in utils.positions
        }
        
        # query player ratings
        for pos in players_by_position:
            for p in players_by_position[pos]:
                id = p['id']
                if id in self.players:
                    if type == 'normal':
                        p['rating'] = self.players[id]['rating'][week]
                    elif type == 'sharp':
                        p['rating'] = self.players[id]['sharp_rating'][week]
                    elif type == 'preseason':
                        p['rating'] = self.players[id]['preseason_rating']
                else:
                    p['rating'] = None

        # sort by player ratings
        for pos in players_by_position:
            players_by_position[pos] = utils.sort_list_of_dicts(
                players_by_position[pos], by='rating'
            )

        # compute weighted rating
        rating = 0
        for pos in players_by_position:
            for i, x in enumerate(players_by_position[pos]):
                if position is None or position == pos:
                    rating += max(utils.position_weight(pos, i, type) * x['rating'], 0)

        # adjust rating to unified scale
        if scale:
            rating = self.scale_rating(rating, position, type)

        return rating


    def scale_rating(self, rating, position=None, type='normal'):
        type = type if type in utils.rating_adjust_params else 'normal'
        position = position if position in utils.rating_adjust_params[type] else 'team'
        mean = utils.rating_adjust_params[type][position]['mean']
        sd = utils.rating_adjust_params[type][position]['sd']
        new_rating = utils.z_score(
            rating, mean, sd,
            utils.rating_scale_params['mean'],
            utils.rating_scale_params['sd']
        )
        new_rating = max(utils.rating_scale_params['min'], new_rating)
        new_rating = min(utils.rating_scale_params['max'], new_rating)
        return new_rating


    # use to get rating adjustment parameters
    def get_rating_statistics(self, type='normal'):
        print('evaluating rating type: %s' % type)
        for pos in [None] + utils.positions:
            ratings_list = []

            for w in range(1, self.week + 1):
                for t in self.teams:
                    rating = self.evaluate_team(
                        self.teams[t]['roster'][w], w, position=pos, type=type, scale=False
                    )
                    if rating > 0:
                        ratings_list.append(rating)

            print('%s:\t mean=%.2f\t sd=%.2f' % (
                pos or 'Team',
                utils.mean(ratings_list),
                utils.std(ratings_list))
            )
