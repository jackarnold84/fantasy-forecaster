import numpy as np
from config import Config
from db.db import read_s3
from league.sim import Simulation
from league.team import Team
from league.trader import Trader
from league.utils import get_mle_projection, get_team_name, z_score
from players.universe import PlayerUniverse
from tqdm import tqdm


class League:

    def __init__(self, sport_tag, league_tag, week, iters=None):
        print('--> init league')
        league_config = Config().leagues[sport_tag][league_tag]
        self.sport, self.year = sport_tag.split('-')
        self.week = int(week)
        self.sport_tag = sport_tag
        self.league_tag = league_tag
        self.name = league_config['name']
        self.use_divisions = league_config['divisions']
        self.use_h2h = league_config['tiebreaker'] == 'h2h'
        self.run_trader = league_config.get('trade_finder', False)
        self.n_teams = league_config['teams']
        self.n_playoff_teams = league_config['playoff_teams']
        self.n_weeks_per_playoff_matchup = league_config['weeks_per_playoff_matchup']
        self.n_regular_season_weeks = league_config['regular_season_weeks']
        self.n_total_weeks = league_config['total_weeks']
        self.n_iter = iters or league_config['n_iter']
        self.model_params = league_config['model_params']
        self.player_universe = PlayerUniverse(self.sport_tag, self.week)

        # read data
        path_prefix = f'data/{self.sport}-{self.year}/leagues/{self.league_tag}'
        league_members_path = f'{path_prefix}/members.csv'
        league_schedule_path = f'{path_prefix}/schedule.csv'
        league_rosters_path = f'{path_prefix}/rosters.csv'
        league_draft_path = f'{path_prefix}/draft.csv'

        member_records = read_s3(league_members_path).to_dict('records')
        schedule_records = read_s3(league_schedule_path).to_dict('records')
        self.playoff_schedule_records = [
            x for x in schedule_records if x['playoff']
        ]
        schedule_records = [x for x in schedule_records if not x['playoff']]
        roster_records = read_s3(league_rosters_path).to_dict('records')
        roster_records = [x for x in roster_records if x['week'] <= week]
        draft_records = read_s3(league_draft_path).to_dict('records')

        # set up teams
        print('--> setting up teams')
        self.teams = [
            Team(
                x['id'], x['manager'], x['team_name'], x['abbrev'],
                x['division'], x['img'], self.week, schedule_records,
                roster_records, draft_records, self.n_teams, self.player_universe,
            )
            for x in member_records
        ]
        self.team_divisions = {t.name: t.division for t in self.teams}
        self.divisions = set(self.team_divisions.values())

        # set up schedule
        self.schedule = {
            w: [] for w in range(1, self.n_regular_season_weeks + 1)
        }
        for x in schedule_records:
            self.schedule[x['week']].append({
                'home': get_team_name(x['home']),
                'away': get_team_name(x['away']),
                'home_score': x['home_score'],
                'away_score': x['away_score'],
                'complete': x['week'] < self.week,
            })

        # run simulations
        print('--> running simulations')
        self.sims = {}
        for w in tqdm(range(0, self.week + 1), desc='week'):
            n_iter = self.n_iter // 4 if w < self.week else self.n_iter
            proj = self.get_projections(w)
            playoff_live_scores = self.get_playoff_live_scores(w)
            self.sims[w] = [
                Simulation(
                    w, self.teams, self.schedule,
                    proj, self.team_divisions, self.divisions,
                    self.use_h2h, playoff_live_scores,
                    self.n_regular_season_weeks,
                    self.n_playoff_teams,
                    self.n_weeks_per_playoff_matchup,
                )
                for _ in range(n_iter)
            ]

        # trade finder
        self.trade_finder = []
        if self.run_trader:
            print("--> running trade finder")
            trader = Trader(self.sport, self.week,
                            self.teams, self.player_universe)
            self.trade_finder = trader.run()

    def get_projections(self, week):
        score_mean = self.model_params['score_mean']
        score_sd = self.model_params['score_sd']
        team_sd = self.model_params['team_sd']
        projections = {
            t.name: {} for t in self.teams
        }

        # get population values
        team_ratings = [
            t.get_team_rating(week) for t in self.teams
        ]
        sharp_team_ratings = [
            t.get_team_rating(week, rating_type='sharp') for t in self.teams
        ]
        valid_ratings = np.mean(team_ratings) > 0

        # compute proj types for each team
        for t in self.teams:
            avg = t.get_scoring_average(week) or score_mean
            mle_proj = get_mle_projection(
                avg, week - 1, score_mean, score_sd, team_sd
            )
            rating = t.get_team_rating(week)
            rating_proj = z_score(
                rating,
                np.mean(team_ratings), np.std(team_ratings),
                score_mean, team_sd,
            )
            sharp_rating = t.get_team_rating(week, rating_type='sharp')
            sharp_rating_proj = z_score(
                sharp_rating,
                np.mean(sharp_team_ratings), np.std(sharp_team_ratings),
                score_mean, team_sd,
            )

            # compute mixed ratings
            if valid_ratings:
                for i in range(0, self.n_total_weeks - week + 1):
                    w = week + i
                    r = sharp_rating_proj if i == 0 else rating_proj
                    mixed_proj = 0.5 * (0.8**i) * mle_proj + \
                        0.5 * (0.85**i) * r + \
                        (1 - 0.5*0.8**i - 0.5*0.85**i) * score_mean
                    projections[t.name][w] = {
                        'mean': mixed_proj, 'sd': score_sd,
                    }
            else:
                for i in range(0, self.n_total_weeks - week + 1):
                    w = week + i
                    mixed_proj = 0.5 * (0.9**i) * mle_proj + \
                        (1 - 0.5*0.9**i) * score_mean
                    projections[t.name][w] = {
                        'mean': mixed_proj, 'sd': score_sd,
                    }

        return projections

    def get_playoff_live_scores(self, week):
        self.playoff_live_scores = {}
        records = [x for x in self.playoff_schedule_records if x['week'] < week]
        records.sort(key=lambda x: x['week'])
        if self.week > self.n_regular_season_weeks + 1:
            for x in records:
                home = get_team_name(x['home'])
                away = get_team_name(x['away'])
                diff = x['home_score'] - x['away_score']
                playoff_week = x['week'] - self.n_regular_season_weeks
                mod = playoff_week % self.n_weeks_per_playoff_matchup
                thru = self.n_weeks_per_playoff_matchup if mod == 0 else mod
                self.playoff_live_scores[(home, away)] = {
                    'diff': diff, 'thru': thru,
                }
                self.playoff_live_scores[(away, home)] = {
                    'diff': -diff, 'thru': thru,
                }
        return self.playoff_live_scores
