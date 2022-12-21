from metrics.players.processor import Processor


class Evaluator:

    def __init__(self, year, week):
        
        self.players = Processor(year, week).players
        print(self.players['JustinFields-QB'])



