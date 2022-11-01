import numpy as np
import pandas as pd
import reader
import simulator
import utils
from tqdm import tqdm


class Processor:

    def __init__(self, league_id, current_week, n_sim=10000):
        
        self.simulator = simulator.Simulator(league_id, current_week)
        self.regular_sim, self.final_sim = self.simulator.sim_seasons(current_week, n_sim=n_sim)
        self.playoff_teams = reader.config['leagues'][league_id]['playoff_teams']
        self.teams = self.simulator.teams

        self.sim_data = {}
        for w in range(1, current_week):
            reg_stand, final_stand = self.simulator.sim_seasons(w, n_sim=n_sim//5)
            self.sim_data[w] = {
                'regular': reg_stand,
                'final': final_stand
            }

        self.sim_data[current_week] = {
            'regular': self.regular_sim,
            'final': self.final_sim
        }

        self.playoff_eligibility = self.simulator.playoff_eligibility(current_week, n_sim)
        self.game_importance = self.simulator.game_importance(current_week + 1, n_sim)


    def playoff_odds(self, week):
        playoff_odds = {}
        for t in self.teams:
            counts = [1 if x <= self.playoff_teams else 0 for x in self.sim_data[week]['regular'][t]]
            playoff_odds[t] = np.mean(counts)
        return playoff_odds

    def champion_odds(self, week):
        champion_odds = {}
        for t in self.teams:
            counts = [1 if x==1 else 0 for x in self.sim_data[week]['final'][t]]
            champion_odds[t] = np.mean(counts)
        return champion_odds

    def punishment_odds(self, week):
        punishment_odds = {}
        n_teams = len(self.teams)
        for t in self.teams:
            counts = [1 if x==n_teams else 0 for x in self.sim_data[week]['final'][t]]
            punishment_odds[t] = np.mean(counts)
        return punishment_odds

    def expected_regular_standings(self, week):
        return {t: np.mean(self.sim_data[week]['regular'][t]) for t in self.teams}

    def expected_final_standings(self, week):
        return {t: np.mean(self.sim_data[week]['final'][t]) for t in self.teams}

    def expected_wins(self, week):
        expected_wins = {t: 0 for t in self.teams}
        df = self.simulator.schedule_df
        for w in range(1, week + 1):
            sub = df[df['week'] == w]
            scores = list(sub['home_score']) + list(sub['away_score'])
            for i in sub.index:
                game = df.iloc[i]
                expected_wins[game['home_team']] += sum([1 for x in scores if x < game['home_score']])
                expected_wins[game['away_team']] += sum([1 for x in scores if x < game['away_score']])
            
        for t in expected_wins:
            expected_wins[t] = expected_wins[t] / (len(self.teams) - 1)

        return expected_wins

    def expected_sos(self, week):
        current = {t: [] for t in self.teams}
        future = {t: [] for t in self.teams}
        wins, points, proj = self.simulator.fill_standings(week)
        
        for x in self.simulator.schedule:
            if x['week'] <= week:
                current[x['home_team']].append(x['away_score'])
                current[x['away_team']].append(x['home_score'])
            else:
                future[x['home_team']].append(proj[x['away_team']])
                future[x['away_team']].append(proj[x['home_team']])

        current = {t: np.mean(current[t]) for t in current}
        future = {t: np.mean(future[t] if future[t] else 0) for t in future}
        return current, future

    def sportsbook_odds(self, week):        
        playoff_odds = self.playoff_odds(week)
        champion_odds = self.champion_odds(week)

        playoff_odds = {t: utils.sportsbook_convert(playoff_odds[t]) for t in playoff_odds}
        champion_odds = {t: utils.sportsbook_convert(champion_odds[t]) for t in champion_odds}
        return playoff_odds, champion_odds
