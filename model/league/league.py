import numpy as np
import pandas as pd
from tqdm import tqdm
from model.players.universe import PlayerUniverse
from model.league.team import Team
from model.league.sim import Simulation
from model.league.utils import get_team_name, z_score, get_mle_projection
from model.config import leagues


class League:

    def __init__(self, sport_tag, league_tag, week):
        print('--> init league')
        league_config = leagues[sport_tag][league_tag]
        self.sport, self.year = sport_tag.split('-')
        self.week = int(week)
        self.sport_tag = sport_tag
        self.league_tag = league_tag
        self.name = league_config['name']
        self.use_divisions = league_config['divisions']
        self.n_teams = league_config['teams']
        self.n_playoff_teams = league_config['playoff_teams']
        self.n_weeks_per_playoff_matchup = league_config['weeks_per_playoff_matchup']
        self.n_regular_season_weeks = league_config['regular_season_weeks']
        self.n_total_weeks = league_config['total_weeks']
        self.n_iter = league_config['n_iter']
        self.model_params = league_config['model_params']
        self.player_universe = PlayerUniverse(self.sport_tag, self.week)

        # read data
        path_prefix = f'data/{self.sport}-{self.year}/leagues/{self.league_tag}'
        league_members_path = f'{path_prefix}/members.csv'
        league_schedule_path = f'{path_prefix}/schedule.csv'
        league_rosters_path = f'{path_prefix}/rosters.csv'
        league_draft_path = f'{path_prefix}/draft.csv'

        member_records = pd.read_csv(league_members_path).to_dict('records')
        schedule_records = pd.read_csv(league_schedule_path).to_dict('records')
        schedule_records = [x for x in schedule_records if not x['playoff']]
        roster_records = pd.read_csv(league_rosters_path).to_dict('records')
        roster_records = [x for x in roster_records if x['week'] <= week]
        draft_records = pd.read_csv(league_draft_path).to_dict('records')

        # set up teams
        print('--> setting up teams')
        self.teams = [
            Team(
                x['id'], x['manager'], x['team_name'], x['abbrev'],
                x['division'], x['img'], self.week, schedule_records,
                roster_records, draft_records, self.player_universe,
            )
            for x in member_records
        ]
        self.team_divisions = {t.name: t.division for t in self.teams}

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
        for w in range(0, self.week + 1):
            n_iter = self.n_iter // 5 if w < self.week else self.n_iter
            proj = self.get_projections(w)
            self.sims[w] = [
                Simulation(
                    self.week, self.teams, self.schedule,
                    proj, self.team_divisions,
                    self.n_regular_season_weeks,
                    self.n_playoff_teams,
                    self.n_weeks_per_playoff_matchup,
                )
                for _ in tqdm(range(n_iter))
            ]

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
                r1 = np.mean([mle_proj, sharp_rating_proj])
                r2 = np.mean(
                    [mle_proj, np.mean([sharp_rating_proj, rating_proj])]
                )
                r3 = np.mean([mle_proj, rating_proj])
                projections[t.name][week] = {'mean': r1, 'sd': score_sd}
                projections[t.name][week + 1] = {'mean': r2, 'sd': score_sd}
                for w in range(week + 2, self.n_total_weeks + 1):
                    projections[t.name][w] = {'mean': r3, 'sd': score_sd}
            else:
                for w in range(week, self.n_total_weeks + 1):
                    projections[t.name][w] = {'mean': mle_proj, 'sd': score_sd}

        return projections