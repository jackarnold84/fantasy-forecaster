leagues = {
    'football-2023': {
        'purdue': {
            'name': 'Practice Squad',
            'league_tag': 'purdue',
            'sport_tag': 'football-2023',
            'league_id': '410886999',
            'player_metrics': True,
            'teams': 10,
            'playoff_teams': 4,
            'divisions': False,
            'tiebreaker': 'points',
            'weeks_per_playoff_matchup': 2,
            'total_weeks': 18,
            'regular_season_weeks': 14,
            'n_iter': 20000,
            'model_params': {
                'score_mean': 122,
                'score_sd': 25,
                'team_sd': 9,
            }
        },
        'mfl': {
            'name': 'MFL',
            'league_tag': 'mfl',
            'sport_tag': 'football-2023',
            'league_id': '522384933',
            'player_metrics': True,
            'teams': 10,
            'playoff_teams': 4,
            'divisions': False,
            'tiebreaker': 'points',
            'weeks_per_playoff_matchup': 2,
            'total_weeks': 18,
            'regular_season_weeks': 14,
            'n_iter': 20000,
            'model_params': {
                'score_mean': 121,
                'score_sd': 24,
                'team_sd': 10,
            }
        }
    },
    'basketball-2024': {
        'demon': {
            'name': 'Demon League',
            'league_tag': 'demon',
            'sport_tag': 'basketball-2024',
            'league_id': '501268457',
            'player_metrics': True,
            'teams': 10,
            'playoff_teams': 6,
            'divisions': False,
            'tiebreaker': 'h2h',
            'weeks_per_playoff_matchup': 1,
            'total_weeks': 23,
            'regular_season_weeks': 20,
            'n_iter': 10000,
            'model_params': {
                'score_mean': 4.5,
                'score_sd': 2,
                'team_sd': 0.8,
            }
        }
    },
    'baseball-2023': {
        'purdue': {
            'name': 'Practice Squad',
            'league_tag': 'purdue',
            'sport_tag': 'baseball-2023',
            'league_id': '1805609855',
            'player_metrics': True,
            'teams': 8,
            'playoff_teams': 4,
            'divisions': False,
            'tiebreaker': 'points',
            'weeks_per_playoff_matchup': 2,
            'total_weeks': 20,
            'regular_season_weeks': 16,
            'n_iter': 20000,
            'model_params': {
                'score_mean': 220,
                'score_sd': 40,
                'team_sd': 14,
            }
        }
    }
}

aliases = {
    'Josh K': 'Josh',
    'Jack Arnold': 'Jack',
    'Shiv Patel': 'Shiv',
    'Rohan Shahani': 'Rohan',
    'Kaiwen Shen': 'Kevin',
    'Tony Choe': 'Tony',
    'Joey Attardo': 'Joey',
    'Nicholas Rosenorn': 'Nick',
    'Tim Zhou': 'Tim',
    'CG Tanner': 'Tanner',
    'Jack Brennan': 'Jack B',
    'Jacob Moza': 'Moza',
    'Levi Killion': 'Levi',
    'Drew Fuiten': 'Drew',
    'Jaden Glascock': 'Jaden',
    'Kyle Killion': 'Kyle',
    'Jake Martin': 'Jake',
    'Jake Walters': 'Walt',
    'Ian Killion': 'Big E',
    'Jack Kelley': 'John',
}
