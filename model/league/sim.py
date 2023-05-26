import numpy as np


class Simulation:

    def __init__(
        self, week, teams, schedule, projections, team_divisions,
        n_regular_season_weeks, n_playoff_teams, n_weeks_per_playoff_matchup,
    ):
        self.week = week
        self.teams = teams
        self.schedule = schedule
        self.projections = projections
        self.team_divisons = team_divisions
        self.divisions = set(team_divisions.values())
        self.n_teams = len(teams)
        self.n_regular_season_weeks = n_regular_season_weeks
        self.n_playoff_teams = n_playoff_teams
        self.n_weeks_per_playoff_matchup = n_weeks_per_playoff_matchup

        # simulation results
        self.regular_standings = []
        self.divison_standings = {}
        self.playoff_standings = []
        self.final_standings = []
        self.game_logs = []

        # run simulation
        self.sim_regular_season()
        self.sim_playoffs()

    # get results

    def made_playoffs(self, team):
        return team in self.playoff_standings[0:self.n_playoff_teams]

    def won_division(self, team):
        return any([team == d[0] for d in self.divison_standings.values()])

    def won_championship(self, team):
        return team == self.final_standings[0]

    def finished_last(self, team):
        return team == self.final_standings[-1]

    def get_regular_standing(self, team):
        return self.regular_standings.index(team) + 1

    def get_final_standing(self, team):
        return self.final_standings.index(team) + 1

    # simulation functions

    def sim_score(self, team, week, n_weeks=1):
        mean = self.projections[team][week]['mean']
        sd = self.projections[team][week]['sd']
        if n_weeks > 1:
            return sum([np.random.normal(mean, sd) for _ in range(n_weeks)])
        else:
            return np.random.normal(mean, sd)

    def sim_regular_season(self):
        wins = {t: 0 for t in self.teams}
        points = {t: 0 for t in self.teams}

        for w in self.schedule:
            for x in self.schedule[w]:
                home = x['home']
                away = x['away']
                if w < self.week:
                    home_score = x['home_score']
                    away_score = x['away_score']
                else:
                    home_score = self.sim_score(home, w)
                    away_score = self.sim_score(away, w)
                home_win = home_score >= away_score
                wins[home] += 1 if home_win else 0
                wins[away] += 0 if home_win else 1
                points[home] += home_score
                points[away] += away_score
                self.game_logs.append((w, home if home_win else away))

        order = sorted(
            self.teams,
            key=lambda t: (wins[t], points[t]),
            reverse=True,
        )
        division_order = {
            d: [t for t in order if self.team_divisons[t] == d]
            for d in self.divisions
        }
        division_winners = {division_order[d][0] for d in division_order}
        playoff_order = (
            [t for t in order if t in division_winners] +
            [t for t in order if t not in division_winners]
        )
        self.regular_standings = order
        self.divison_standings = division_order
        self.playoff_standings = playoff_order

    def sim_playoffs(self):

        def get_result(home, away):
            w = self.n_regular_season_weeks + 1
            n = self.n_weeks_per_playoff_matchup
            home_score = self.sim_score(home, w, n)
            away_score = self.sim_score(away, w, n)
            return [home, away] if home_score >= away_score else [away, home]

        standings = self.playoff_standings
        final_standings = []

        if self.n_playoff_teams == 4:
            # winners bracket
            g1_w, g1_l = get_result(standings[0], standings[3])
            g2_w, g2_l = get_result(standings[1], standings[2])
            g3_w, g3_l = get_result(g1_w, g2_w)
            g4_w, g4_l = get_result(g1_l, g2_l)
            final_standings += [g3_w, g3_l, g4_w, g4_l]

            # consolation bracket
            if self.n_teams == 8:
                g5_w, g5_l = get_result(standings[4], standings[5])
                g6_w, g6_l = get_result(standings[6], standings[7])
                g7_w, g7_l = get_result(g5_w, g6_w)
                g8_w, g8_l = get_result(g5_l, g6_l)
                final_standings += [g7_w, g7_l, g8_w, g8_l]

            elif self.n_teams == 10:
                g1_w, g1_l = get_result(standings[4], standings[5])
                g2_w, g2_l = get_result(standings[6], standings[7])
                g3_w, g3_l = get_result(standings[8], standings[9])
                g4_w, g4_l = get_result(g1_w, g2_w)
                g5_w, g5_l = get_result(g1_l, g3_w)
                g6_w, g6_l = get_result(g2_l, g3_l)
                final_standings += [g4_w, g4_l, g5_w, g5_l, g6_w, g6_l]

            elif self.n_teams == 12:
                g1_w, g1_l = get_result(standings[4], standings[5])
                g2_w, g2_l = get_result(standings[6], standings[7])
                g3_w, g3_l = get_result(standings[8], standings[9])
                g4_w, g4_l = get_result(standings[10], standings[11])
                g5_w, g5_l = get_result(g1_w, g2_w)
                g6_w, g6_l = get_result(g1_l, g3_w)
                g7_w, g7_l = get_result(g2_l, g4_w)
                g8_w, g8_l = get_result(g3_l, g4_l)
                final_standings += [
                    g5_w, g5_l, g6_w, g6_l, g7_w, g7_l, g8_w, g8_l
                ]

            else:
                assert False, 'playoff configuration not recognized'
        else:
            assert False, 'playoff configuration not recognized'

        self.final_standings = final_standings
