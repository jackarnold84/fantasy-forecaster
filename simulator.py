import numpy as np
import pandas as pd
import reader
from tqdm import tqdm

class Simulator:

    def __init__(self, league_id, current_week):

        self.league_id = league_id
        self.schedule_df = reader.read_league_data(league_id)
        self.schedule = self.schedule_df.to_dict('records')
        self.teams = sorted(list(set(self.schedule_df['home_team'])))
        self.N_TEAMS = len(self.teams)
        self.player_scores = {t: [] for t in self.teams}
        for x in self.schedule:
            if not np.isnan(x['home_score']):
                self.player_scores[x['home_team']].append(x['home_score'])
            if not np.isnan(x['away_score']):
                self.player_scores[x['away_team']].append(x['away_score'])

        for t in self.player_scores:
            self.player_scores[t] = list(self.player_scores[t])

        self.CURRENT_WEEK = current_week
        self.MEAN = reader.config['leagues'][league_id]['score_mean']
        self.STD = reader.config['leagues'][league_id]['score_std']
        self.T_STD = reader.config['leagues'][league_id]['team_std']
        self.PLAYOFF = reader.config['leagues'][league_id]['playoff_type']
        self.PLAYOFF_WEEKS = reader.config['leagues'][league_id]['playoff_weeks']
        self.PLAYOFF_TEAMS = reader.config['leagues'][league_id]['playoff_teams']
        self.league_name = reader.config['leagues'][league_id]['name']


    # ==================
    # helper methods
    # ==================

    # get projected score for a player
    def get_projections(self, week, proj_method=None):

        if proj_method == 'global':
            return {t: self.MEAN for t in self.teams}

        # default (mle method)
        else:
            proj = {}
            for t in self.teams:
                d = np.mean(self.player_scores[t][0:week])
                proj[t] = (d*week*self.T_STD**2 + self.MEAN*self.STD**2) / (week*self.T_STD**2 + self.STD**2)
            return proj


    # simulate single game score
    def sim_game(self, home_proj, away_proj, sd=None):
        sd = sd if sd else self.STD
        home_points = np.random.normal(home_proj, sd)
        away_points = np.random.normal(away_proj, sd)
        return home_points, away_points


    # simulate two week game score
    def sim_2_week_game(self, home_proj, away_proj, sd=None):
        sd = sd if sd else self.STD
        home_points = np.random.normal(home_proj, sd) + np.random.normal(home_proj, sd)
        away_points = np.random.normal(away_proj, sd) + np.random.normal(away_proj, sd)
        return home_points, away_points
    

    # standings order based on wins and points for
    def get_standings_order(self, wins, points):
        values = {t: wins[t]*1e12 + points[t] for t in self.teams}
        values_sort = {k: v for k, v in sorted(values.items(), key=lambda item: item[1])}
        return list(reversed(values_sort.keys()))


    # =======================
    # simulation methods
    # =======================

    # set up and fill in standings up to the current week
    def fill_standings(self, week, proj_method=None):
        wins = {t: 0 for t in self.teams}
        points = {t: 0 for t in self.teams}
        projections = self.get_projections(week, proj_method)

        for x in self.schedule:
            if x['week'] > week:
                continue
            if x['home_score'] > x['away_score']:
                wins[x['home_team']] += 1
            else:
                wins[x['away_team']] += 1

            points[x['home_team']] += x['home_score']
            points[x['away_team']] += x['away_score']
        
        return wins, points, projections


    # simulate remaining regular season
    def season_sim(self, wins, points, projections, week, sd=None):
        wins = wins.copy()
        points = points.copy()

        for x in self.schedule:
            if x['week'] <= week:
                continue

            home_score, away_score = self.sim_game(projections[x['home_team']], projections[x['away_team']], sd)
            if home_score > away_score:
                wins[x['home_team']] += 1
            else:
                wins[x['away_team']] += 1

            points[x['home_team']] += home_score
            points[x['away_team']] += away_score

        return wins, points


    # sim playoffs
    def playoff_sim(self, wins, points, projections, sd=None):
        standings = self.get_standings_order(wins, points)
        final_standings = []

        def get_result(p1, p2):
            if self.PLAYOFF_WEEKS == 2:
                p1_score, p2_score = self.sim_2_week_game(projections[p1], projections[p2], sd)
            else:
                p1_score, p2_score = self.sim_game(projections[p1], projections[p2], sd)
            return (p1, p2) if p1_score > p2_score else (p2, p1)

        if self.PLAYOFF == '10-team-4-playoff':
            # winners bracket
            g1_w, g1_l = get_result(standings[0], standings[3])
            g2_w, g2_l = get_result(standings[1], standings[2])

            g3_w, g3_l = get_result(g1_w, g2_w)
            g4_w, g4_l = get_result(g1_l, g2_l)

            final_standings += [g3_w, g3_l, g4_w, g4_l]

            # consolation bracket
            g1_w, g1_l = get_result(standings[4], standings[5])
            g2_w, g2_l = get_result(standings[6], standings[7])
            g3_w, g3_l = get_result(standings[8], standings[9])

            g4_w, g4_l = get_result(g1_w, g2_w)
            g5_w, g5_l = get_result(g1_l, g3_w)
            g6_w, g6_l = get_result(g2_l, g3_l)

            final_standings += [g4_w, g4_l, g5_w, g5_l, g6_w, g6_l]

        elif self.PLAYOFF == '8-team-4-playoff':
            # winners bracket
            g1_w, g1_l = get_result(standings[0], standings[3])
            g2_w, g2_l = get_result(standings[1], standings[2])

            g3_w, g3_l = get_result(g1_w, g2_w)
            g4_w, g4_l = get_result(g1_l, g2_l)

            final_standings += [g3_w, g3_l, g4_w, g4_l]

            # consolation bracket
            g5_w, g5_l = get_result(standings[4], standings[5])
            g6_w, g6_l = get_result(standings[6], standings[7])

            g7_w, g7_l = get_result(g5_w, g6_w)
            g8_w, g8_l = get_result(g5_l, g6_l)

            final_standings += [g7_w, g7_l, g8_w, g8_l]

        elif self.PLAYOFF == '16-team-6-playoff':
            # winners bracket
            g1_w, g1_l = get_result(standings[3], standings[4])
            g2_w, g2_l = get_result(standings[2], standings[5])

            g3_w, g3_l = get_result(standings[0], g1_w)
            g4_w, g4_l = get_result(standings[1], g2_w)
            g5_w, g5_l = get_result(g1_l, g2_l)

            g6_w, g6_l = get_result(g3_w, g4_w)
            g7_w, g7_l = get_result(g5_w, g3_l)
            g8_w, g8_l = get_result(g4_l, g5_l)

            final_standings += [g6_w, g6_l, g7_w, g8_w, g7_l, g8_l]

            # consolation bracket
            # (incomplete)
            final_standings += list(np.random.permutation([standings[6], standings[7], standings[8]]))
            final_standings += list(np.random.permutation([standings[9], standings[10], standings[11]]))
            final_standings += list(np.random.permutation([standings[12], standings[13], standings[14], 
                                                    standings[15]]))

        return final_standings



    # simulate N seasons  
    def sim_seasons(self, week, n_sim=10000, proj_method=None):

        # set up and fill in standings
        wins, points, projections = self.fill_standings(week, proj_method)

        # season projections
        regular_standings = {t: [] for t in self.teams}
        final_standings = {t: [] for t in self.teams}

        for _ in tqdm(range(n_sim)):
            # regular season
            sim_wins, sim_points = self.season_sim(wins, points, projections, week)
            standings = self.get_standings_order(sim_wins, sim_points)
            for i, t in enumerate(standings):
                regular_standings[t].append(i + 1)

            # playoffs
            standings = self.playoff_sim(sim_wins, sim_points, projections)
            for i, t in enumerate(standings):
                final_standings[t].append(i + 1)

        return regular_standings, final_standings

    
    # get playoff eligibility
    def playoff_eligibility(self, week, n_sim=10000):

        regular_standings = {t: [] for t in self.teams}
        final_standings = {t: [] for t in self.teams}
        wins, points, projections = self.fill_standings(week)
        for _ in tqdm(range(n_sim)):
            # regular season
            sim_wins, sim_points = self.season_sim(wins, points, projections, week, sd=1e6)
            standings = self.get_standings_order(sim_wins, sim_points)
            for i, t in enumerate(standings):
                regular_standings[t].append(i + 1)
            # playoffs
            standings = self.playoff_sim(sim_wins, sim_points, projections)
            for i, t in enumerate(standings):
                final_standings[t].append(i + 1)

        eliminated = {t: True for t in self.teams}
        clinched = {t: True for t in self.teams}
        limits = {t: {} for t in self.teams}
        for t in self.teams:
            if any([x <= self.PLAYOFF_TEAMS for x in regular_standings[t]]):
                eliminated[t] = False
            if any([x > self.PLAYOFF_TEAMS for x in regular_standings[t]]):
                clinched[t] = False
            limits[t] = {'min': np.min(final_standings[t]), 'max': np.max(final_standings[t])}

        return eliminated, clinched, limits

    
    # get game importance (for playoff odds)
    def game_importance(self, upcoming_week, n_sim=10000):
        
        week = upcoming_week - 1
        games = [g for g in self.schedule if g['week'] == upcoming_week]
        if not games:
            return None

        def get_playoff_odds(reg_standings):
            playoff_odds = {}
            for t in self.teams:
                counts = [1 if x <= self.PLAYOFF_TEAMS else 0 for x in reg_standings[t]]
                playoff_odds[t] = np.mean(counts)
            return playoff_odds

        for i in range(len(games)):
            g = games[i]
            sim = Simulator(self.league_id, week)
            for j in range(len(sim.schedule)):
                x = sim.schedule[j]
                if x['week'] == g['week'] and x['home_team'] == g['home_team']:
                    sim.schedule[j]['week'] = 0

                    sim.schedule[j]['home_score'] = self.MEAN + 1   # home wins
                    sim.schedule[j]['away_score'] = self.MEAN - 1
                    reg1, final1 = sim.sim_seasons(week, n_sim)
                    
                    sim.schedule[j]['home_score'] = self.MEAN - 1
                    sim.schedule[j]['away_score'] = self.MEAN + 1   # away wins
                    reg2, final2 = sim.sim_seasons(week, n_sim)

                    odds1 = get_playoff_odds(reg1)
                    odds2 = get_playoff_odds(reg2)

                    diff = sum([abs(odds1[t] - odds2[t]) for t in self.teams])
                    games[i]['importance'] = diff

        return games


        