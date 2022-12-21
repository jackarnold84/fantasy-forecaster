from metrics.league.processor import Processor


class Evaluator:

    def __init__(self, league_id, week, players, draft_recap_week=1):
        
        self.teams = Processor(league_id, week, draft_recap_week).teams
        self.players = players

        print(self.teams['Jack Arnold'])
        print(self.players['JamesConner-RB'])


