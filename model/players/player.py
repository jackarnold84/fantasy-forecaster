from model.players.utils import (
    bound, get_sequence, parse_value, wma,
)
from model.players.weights import get_position_group


class Player:

    def __init__(self, sport, id, name, pos, team, img, stat_records):
        self.id = id
        self.sport = sport
        self.name = name
        self.pos = pos
        self.team = team
        self.img = img
        self.pos_group = get_position_group(self.sport, self.pos)

        # stats
        self.preseason_total = None
        self.preseason_avg = None
        self.injury = {}
        self.opp = {}
        self.score = {}
        self.proj = {}
        self.roster = {}
        self.roster_change = {}
        self.total = {}
        self.avg = {}

        # ratings
        self.raw_rating = {}
        self.rating = {}
        self.sharp_rating = {}

        # fill stats from records
        for x in stat_records:
            week = int(x['week'])
            prev_week = week - 1 if week > 1 else None

            if week == 0:
                self.preseason_total = parse_value(x['total_pts'], float)
                self.preseason_avg = parse_value(x['avg_pts'], float)
            else:
                self.injury[week] = parse_value(x['injury'])
                self.opp[week] = parse_value(x['opp'])  # TODO: bye weeks
                if prev_week:
                    prev_score = parse_value(x['prev_score'], float) or 0
                    self.score[prev_week] = prev_score if prev_score > 0 else None
                proj = parse_value(x['proj'], float) or 0
                self.proj[week] = proj if proj > 0 else None
                self.total[week] = parse_value(x['total_pts'], float)
                self.avg[week] = parse_value(x['avg_pts'], float)
            self.roster[week] = parse_value(x['roster'], float)
            self.roster_change[week] = parse_value(x['roster_change'], float)

        # fill missing season stats
        max_week = max([x['week'] for x in stat_records])
        prev_total = None
        prev_avg = None
        for w in range(1, max_week + 1):
            curr_total = self.total.get(w)
            if curr_total is not None:
                prev_total = curr_total
            else:
                self.total[w] = prev_total

            curr_avg = self.avg.get(w)
            if curr_avg is not None:
                prev_avg = curr_avg
            else:
                self.avg[w] = prev_avg

    def get_status(self, week):
        proj = self.proj.get(week)
        score = self.score.get(week)
        injury = self.injury.get(week)
        opp = self.opp.get(week)
        if (proj and proj >= 1.0) or (score and score >= 1.0):
            return 'active'
        if injury:
            if injury in ['IR', 'IL10', 'IL15', 'IL60', 'SUSP']:
                return 'injured'
            elif injury in ['O', 'Q', 'D', 'DTD']:
                return 'unhealthy'
        if opp and opp == 'BYE':
            return 'bye'
        else:
            return None

    # rating getter
    def get_rating(self, week, rating_type='normal'):
        ratings = self.sharp_rating if rating_type == 'sharp' else self.rating
        rating = ratings.get(week)
        status = self.get_status(week)
        if rating is None:
            return None
        elif status == 'injured':
            return rating * 0.8
        elif status == 'unhealthy':
            return rating * 0.9
        elif status == 'bye' and rating_type == 'sharp':
            return rating * 0.7
        else:
            return rating

    # stat getters
    def get_stat(self, stat_name, week):
        if stat_name == 'proj':
            return self.get_proj(week)
        elif stat_name == 'moving_proj':
            return self.get_moving_proj(week)
        elif stat_name == 'total':
            return self.get_total(week)
        elif stat_name == 'avg':
            return self.get_avg(week)
        elif stat_name == 'moving_avg':
            return self.get_moving_avg(week)
        elif stat_name == 'exp_roster':
            return self.get_exp_roster(week)
        elif stat_name == 'preseason_total':
            return self.get_preseason_total()
        elif stat_name == 'preseason_avg':
            return self.get_preseason_avg()

    def get_preseason_total(self):
        return self.preseason_total

    def get_preseason_avg(self):
        return self.preseason_avg

    def get_preseason_games_played(self):
        avg = self.get_preseason_avg()
        total = self.get_preseason_total()
        if avg is None or total is None:
            return None
        else:
            return round(total / avg) if avg else 0

    def get_total(self, week):
        return self.total.get(week)

    def get_avg(self, week):
        return self.avg.get(week)

    def get_games_played(self, week):
        avg = self.get_avg(week)
        total = self.get_total(week)
        if avg is None or total is None:
            return None
        else:
            return round(total / avg) if avg else 0

    def get_proj(self, week):
        return self.proj.get(week)

    def get_moving_proj(self, week):
        proj_seq = get_sequence(self.proj, week)
        return wma(proj_seq)

    def get_moving_avg(self, week):
        avg_seq = get_sequence(self.score, week)
        return wma(avg_seq)

    def get_exp_roster(self, week):
        roster = self.roster.get(week)
        change = self.roster_change.get(week)
        if roster is None:
            return None
        elif change is None:
            return roster
        adj = abs(change)**0.6 if change >= 0 else -abs(change)**0.75
        exp_roster = roster + adj
        return bound(exp_roster, 0.1, 99.9)
