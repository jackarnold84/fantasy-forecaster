import numpy as np


class Simulation:

    def __init__(
        self, week, teams, schedule, projections, team_divisions, divisions,
        use_h2h, playoff_live_scores, n_regular_season_weeks, n_playoff_teams,
        n_weeks_per_playoff_matchup,
    ):
        self.week = week
        self.teams = teams
        self.schedule = schedule
        self.projections = projections
        self.team_divisions = team_divisions
        self.divisions = divisions
        self.use_h2h = use_h2h
        self.playoff_live_scores = playoff_live_scores
        self.in_playoffs = week > n_regular_season_weeks + 1 and len(playoff_live_scores) > 0
        self.n_teams = len(teams)
        self.n_regular_season_weeks = n_regular_season_weeks
        self.n_playoff_teams = n_playoff_teams
        self.n_weeks_per_playoff_matchup = n_weeks_per_playoff_matchup

        # simulation results
        self.standings = {'normal': {}, 'shuffled': {}}
        self.game_logs = []

        # run simulation
        self.sim_regular_season()
        self.sim_playoffs()
        self.sim_playoffs('shuffled')

    # get results

    def made_playoffs(self, team, order_type='normal'):
        standings = self.standings[order_type]['playoff']
        return team in standings[0:self.n_playoff_teams]

    def won_division(self, team, order_type='normal'):
        standings = self.standings[order_type]['division']
        return any([team == d[0] for d in standings.values()])

    def won_championship(self, team, order_type='normal'):
        standings = self.standings[order_type]['final']
        return team == standings[0]

    def finished_last(self, team, order_type='normal'):
        standings = self.standings[order_type]['final']
        return team == standings[-1]

    def get_regular_standing(self, team, order_type='normal'):
        standings = self.standings[order_type]['regular']
        return standings.index(team) + 1

    def get_final_standing(self, team, order_type='normal'):
        standings = self.standings[order_type]['final']
        return standings.index(team) + 1

    # simulation functions

    def sim_score(self, team, week, n_weeks=1):
        mean = self.projections[team][week]['mean']
        sd = self.projections[team][week]['sd']
        if n_weeks != 1:
            return sum([np.random.normal(mean, sd) for _ in range(n_weeks)])
        else:
            return np.random.normal(mean, sd)

    def sim_regular_season(self):
        wins = {t.name: 0 for t in self.teams}
        points = {t.name: 0 for t in self.teams}
        h2h = {t1.name: {t2.name: 0 for t2 in self.teams} for t1 in self.teams}
        h2h_breaker = {t.name: 0 for t in self.teams}

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
                home_win = home_score > away_score
                away_win = away_score > home_score
                home_result = 1 if home_win else 0 if away_win else 0.5
                away_result = 0 if home_win else 1 if away_win else 0.5
                wins[home] += home_result
                wins[away] += away_result
                h2h[home][away] += home_result
                h2h[away][home] += away_result
                points[home] += home_score
                points[away] += away_score
                self.game_logs.append((w, away if away_win else home))

        if self.use_h2h:
            buckets = {}
            for t in wins:
                buckets[wins[t]] = buckets.get(wins[t], []) + [t]
            for teams in buckets.values():
                for t in teams:
                    h2h_breaker[t] = sum([h2h[t][o] for o in teams])

        normal_order = sorted(
            wins, key=lambda t: (wins[t], h2h_breaker[t], points[t]), reverse=True,
        )
        shuffled_order = sorted(
            wins, key=lambda t: (wins[t], np.random.random()), reverse=True,
        )
        for order_type in ['normal', 'shuffled']:
            order = shuffled_order if order_type == 'shuffled' else normal_order
            division_order = {
                d: [t for t in order if self.team_divisions[t] == d]
                for d in self.divisions
            }
            division_winners = {division_order[d][0] for d in division_order}
            playoff_order = (
                [t for t in order if t in division_winners] +
                [t for t in order if t not in division_winners]
            )
            self.standings[order_type]['regular'] = order
            self.standings[order_type]['division'] = division_order
            self.standings[order_type]['playoff'] = playoff_order

    def sim_playoffs(self, order_type='normal'):

        def get_result(home, away):
            w = max(self.n_regular_season_weeks + 1, self.week)
            n = self.n_weeks_per_playoff_matchup
            home_score = 0
            away_score = 0
            if self.in_playoffs and (home, away) in self.playoff_live_scores:
                live = self.playoff_live_scores[(home, away)]
                n -= live['thru']
                home_score += live['diff']
                away_score -= live['diff']
            home_score += self.sim_score(home, w, n)
            away_score += self.sim_score(away, w, n)
            return [home, away] if home_score >= away_score else [away, home]

        standings = self.standings[order_type]['playoff']
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

        elif self.n_playoff_teams == 6:
            # winners bracket
            g1_w, g1_l = get_result(standings[3], standings[4])
            g2_w, g2_l = get_result(standings[2], standings[5])
            g3_w, g3_l = get_result(g1_w, standings[0])
            g4_w, g4_l = get_result(g2_w, standings[1])
            g5_w, g5_l = get_result(g3_w, g4_w)
            # winners consolation
            g6_w, g6_l = get_result(g1_l, g2_l)
            g7_w, g7_l = get_result(g3_l, g6_l)
            g8_w, g8_l = get_result(g4_l, g6_w)
            final_standings += [g5_w, g5_l, g7_w, g8_w, g7_l, g8_l]

            if self.n_teams == 10:
                g1_w, g1_l = get_result(standings[6], standings[7])
                g2_w, g2_l = get_result(standings[8], standings[9])
                g3_w, g3_l = get_result(g1_w, g2_l)
                g4_w, g4_l = get_result(g1_l, g2_w)
                g5_w, g5_l = get_result(g3_w, g4_w)
                g6_w, g6_l = get_result(g3_l, g4_l)
                final_standings += [g5_w, g5_l, g6_w, g6_l]
            else:
                assert False, 'playoff configuration not recognized'
        else:
            assert False, 'playoff configuration not recognized'

        self.standings[order_type]['final'] = final_standings
