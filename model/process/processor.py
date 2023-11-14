import json
import numpy as np
from model.players.weights import position_group_list
from model.league.league import League
from model.league.sim import Simulation
from model.process.utils import safe_round


class Processor:

    def __init__(self, league: League):
        self.sport_tag = league.sport_tag
        self.leauge_tag = league.league_tag
        self.league = league
        self.player_universe = league.player_universe
        self.teams = [t.name for t in league.teams]
        self.week = self.league.week

        self.players_output = {}
        self.teams_output = {}
        self.league_output = {}

        print('--> processing model results')
        self.get_forecasts()
        self.get_standings()
        self.get_team_info()
        self.get_team_ratings()
        self.get_team_projections()
        self.get_expected_vs_actual()
        self.get_sos()
        self.get_game_importance()
        self.get_player_info()

        # write results
        outfile = 'data/output.json'
        data = {
            'meta': {
                'name': league.name,
                'sport': league.sport,
                'year': league.year,
                'tag': self.leauge_tag,
                'week': self.week,
            },
            'teams': self.teams_output,
            'league': self.league_output,
            'players': self.players_output,
        }
        with open(outfile, 'r') as f:
            try:
                output = json.load(f)
            except Exception as e:
                print('warning: error reading existing output')
                output = {}

        if self.sport_tag not in output:
            output[self.sport_tag] = {}
        output[self.sport_tag][self.leauge_tag] = data

        with open(outfile, 'w') as f:
            json.dump(output, f, indent=4)

        print(f'--> results written to {outfile}')

    def get_forecasts(self):
        forecast_options = [
            ('playoffs', Simulation.made_playoffs),
            ('division', Simulation.won_division),
            ('championship', Simulation.won_championship),
            ('punishment', Simulation.finished_last),
        ]
        result = {f: [] for f, _ in forecast_options}
        for w in range(0, self.week + 1):
            for forecast_type, get in forecast_options:
                eliminated = {
                    t: not any([
                        get(s, t, 'shuffled') for s in self.league.sims[w]
                    ])
                    for t in self.teams
                }
                clinched = {
                    t: all([
                        get(s, t, 'shuffled') for s in self.league.sims[w]
                    ])
                    for t in self.teams
                }
                forecast = {
                    t: np.mean([get(s, t) for s in self.league.sims[w]])
                    for t in self.teams
                }
                for t in self.teams:
                    if not eliminated[t]:
                        forecast[t] = max(forecast[t], 0.001)
                    if not clinched[t]:
                        forecast[t] = min(forecast[t], 0.999)
                forecast_result = [
                    {'week': w, 'team': t, 'prob': round(forecast[t], 3)}
                    for t in self.teams
                ]
                forecast_result = sorted(
                    forecast_result, key=lambda x: x['prob'], reverse=True,
                )
                result[forecast_type].append(forecast_result)

        self.league_output['forecasts'] = result

    def get_standings(self):
        wins = {t: 0 for t in self.teams}
        points = {t: 0 for t in self.teams}
        h2h = {t1: {t2: 0 for t2 in self.teams} for t1 in self.teams}
        h2h_breaker = {t: 0 for t in self.teams}
        for w in self.league.schedule:
            for x in self.league.schedule[w]:
                home = x['home']
                away = x['away']
                if w < self.week:
                    home_score = x['home_score']
                    away_score = x['away_score']
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

        if self.league.use_h2h:
            buckets = {}
            for t in wins:
                buckets[wins[t]] = buckets.get(wins[t], []) + [t]
            for teams in buckets.values():
                for t in teams:
                    h2h_breaker[t] = sum([h2h[t][o] for o in teams])

        league_order = sorted(
            wins, key=lambda t: (wins[t], h2h_breaker[t], points[t]), reverse=True,
        )
        division_order = {
            d: [t for t in league_order if self.league.team_divisions[t] == d]
            for d in self.league.divisions
        }
        self.league_output['standings'] = {}
        self.league_output['standings']['league'] = [
            {
                'team': t,
                'rank': i + 1,
                'wins': wins[t],
                'avg': round(points[t] / ((self.week - 1) or 1), 1)
            }
            for i, t in enumerate(league_order)
        ]
        self.league_output['standings']['divisions'] = {
            d: [
                {
                    'team': t,
                    'rank': i + 1,
                    'wins': wins[t],
                    'avg': round(points[t] / ((self.week - 1) or 1), 1)
                }
                for i, t in enumerate(division_order[d])
            ]
            for d in self.league.divisions
        }

    def get_team_info(self):
        metadata = {
            t.name: {
                'id': t.id,
                'name': t.name,
                'nickname': t.nickname,
                'abbrev': t.abbrev,
                'division': t.division,
                'img': t.img,
            }
            for t in self.league.teams
        }

        roster_aquisitions = {
            t.name: t.get_roster_aquisitions(self.week)
            for t in self.league.teams
        }

        def get_rating_sorter(p, w):
            player = self.player_universe.players.get(p)
            if not player:
                return 0
            pos = player.pos
            rating = player.rating.get(w) or 0
            if pos in ['TE', 'RP']:
                return rating * 0.9
            elif pos in ['DST', 'K']:
                return rating * 0.4
            else:
                return rating

        roster_players = [
            {
                t.name: sorted(
                    t.get_roster(w),
                    key=lambda x: get_rating_sorter(x, w),
                    reverse=True,
                )
                for t in self.league.teams
            }
            for w in range(0, self.week + 1)
        ]

        self.teams_output['metadata'] = metadata
        self.teams_output['roster'] = {}
        self.teams_output['roster']['players'] = roster_players
        self.teams_output['roster']['aquisitions'] = roster_aquisitions

    def get_team_ratings(self):
        positions = position_group_list[self.league.sport]
        ratings_by_week = []
        for w in range(0, self.week + 1):
            ratings_by_pos = {}
            for pos in ['OVR', *positions]:
                p = None if pos == 'OVR' else pos
                ratings = [
                    {
                        'week': w,
                        'pos': pos,
                        'team': t.name,
                        'rating': round(t.get_team_rating(w, p), 2),
                    }
                    for t in self.league.teams
                ]
                ratings = sorted(
                    ratings,
                    key=lambda x: x['rating'],
                    reverse=True
                )
                ratings_by_pos[pos] = ratings
            ratings_by_week.append(ratings_by_pos)

        self.teams_output['ratings'] = ratings_by_week

    def get_team_projections(self):
        n_weeks = self.league.n_total_weeks
        projections_by_week = []
        for w in range(0, self.week + 1):
            proj = self.league.get_projections(w)
            projections = [
                {
                    'week': w,
                    'team': t.name,
                    'proj': [
                        round(proj[t.name][w + i]['mean'], 1)
                        for i in range(min(5, n_weeks - w))
                    ],
                }
                for t in self.league.teams
            ]
            projections = sorted(
                projections,
                key=lambda x: x['proj'],
                reverse=True,
            )
            projections_by_week.append(projections)

        self.teams_output['proj'] = projections_by_week

    def get_expected_vs_actual(self):
        expected_wins = {t: 0 for t in self.teams}
        actual_wins = {t: 0 for t in self.teams}
        for w in self.league.schedule:
            matchups = self.league.schedule[w]
            if w < self.week:
                scores = [x['home_score'] for x in matchups] + \
                    [x['away_score'] for x in matchups]
                for x in matchups:
                    expected_wins[x['home']] += len(
                        [s for s in scores if s < x['home_score']]
                    )
                    expected_wins[x['away']] += len(
                        [s for s in scores if s < x['away_score']]
                    )
                    home_win = x['home_score'] >= x['away_score']
                    actual_wins[x['home']] += 1 if home_win else 0
                    actual_wins[x['away']] += 0 if home_win else 1

        for t in expected_wins:
            exp_wins = expected_wins[t] / (self.league.n_teams - 1)
            expected_wins[t] = round(exp_wins, 1)

        expected_vs_actual = [
            {
                'team': t,
                'expected': expected_wins[t],
                'actual': actual_wins[t],
                'diff': round(actual_wins[t] - expected_wins[t], 1),
            }
            for t in self.teams
        ]
        expected_vs_actual = sorted(
            expected_vs_actual,
            key=lambda x: (x['expected'], x['actual']),
            reverse=True,
        )
        self.league_output['expectedWins'] = expected_vs_actual

    def get_sos(self):
        against = {t: 0 for t in self.teams}
        future_against = {t: 0 for t in self.teams}
        proj = self.league.get_projections(self.week)
        for w in self.league.schedule:
            matchups = self.league.schedule[w]
            if w < self.week:
                for x in matchups:
                    against[x['home']] += x['away_score']
                    against[x['away']] += x['home_score']
            else:
                for x in matchups:
                    future_against[x['home']] += proj[x['away']][w]['mean']
                    future_against[x['away']] += proj[x['home']][w]['mean']

        ranked_future_against = sorted(
            self.teams,
            key=lambda x: (future_against[x], against[x]),
            reverse=True,
        )
        is_playoffs = self.week > self.league.n_regular_season_weeks

        games_played = max(self.week - 1, 1)
        games_remaining = self.league.n_regular_season_weeks - self.week + 1
        for t in self.teams:
            against[t] = round(against[t] / games_played, 1)
            if future_against[t]:
                future_against[t] = round(
                    future_against[t] / games_remaining, 1
                )
        sos = [
            {
                'team': t,
                'current': against[t],
                'future': 0 if is_playoffs else ranked_future_against.index(t) + 1,
            }
            for t in self.teams
        ]
        sos = sorted(
            sos,
            key=lambda x: (x['current'], -x['future']),
            reverse=True,
        )
        self.league_output['sos'] = sos

    def get_game_importance(self):
        importance_by_week = [[]]
        for w in range(1, min(self.week, self.league.n_regular_season_weeks) + 1):
            importance_by_matchup = []
            matchups = self.league.schedule[w]
            for x in matchups:
                home_win = [
                    s for s in self.league.sims[w] if (w, x['home']) in s.game_logs
                ]
                away_win = [
                    s for s in self.league.sims[w] if (w, x['away']) in s.game_logs
                ]

                odds1 = {
                    t: np.mean([s.made_playoffs(t) for s in home_win])
                    for t in self.teams
                }
                odds2 = {
                    t: np.mean([s.made_playoffs(t) for s in away_win])
                    for t in self.teams
                }
                diff = sum([abs(odds1[t] - odds2[t]) for t in self.teams])
                importance_by_matchup.append({
                    'week': w,
                    'home': x['home'],
                    'away': x['away'],
                    'importance': round(diff * 100)
                })
            importance_by_matchup = sorted(
                importance_by_matchup,
                key=lambda x: x['importance'],
                reverse=True,
            )
            importance_by_week.append(importance_by_matchup)

        self.league_output['matchupImportance'] = importance_by_week

    def get_player_info(self):
        metadata = {
            p.id: {
                'id': p.id,
                'name': p.name,
                'pos': p.pos,
                'group': p.pos_group,
                'team': p.team,
                'img': p.img,
                'status': p.get_status(self.week),
                'ratings': [safe_round(p.get_rating(w), 2) for w in range(0, self.week + 1)],
            }
            for p in self.player_universe.players.values()
        }
        self.players_output = metadata
