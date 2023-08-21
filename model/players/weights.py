# weights used for player rating algorithm

player_rating_mean = 5.0
player_rating_sd = 2.5
team_rating_mean = 60
team_rating_sd = 10

stat_list = [
    'proj',
    'moving_proj',
    'total',
    'avg',
    'moving_avg',
    'exp_roster',
    'preseason_total',
    'preseason_avg',
]

normal_weights = {
    # week               0   1   2   3   4   5   6   7   8   9  10  11
    'proj':            [ 0, 18, 15, 17, 20, 23, 25, 27, 28, 29, 30, 30],
    'moving_proj':     [ 0,  0,  5,  8, 10, 12, 15, 16, 16, 17, 18, 18],
    'total':           [ 0,  0,  5,  5,  5,  7,  7,  9,  9,  9,  9, 10],
    'avg':             [ 0,  0,  5,  5,  5,  6,  6,  6,  6,  6,  6,  6],
    'moving_avg':      [ 0,  0,  0,  5, 10, 12, 13, 14, 14, 14, 14, 14],
    'exp_roster':      [ 0, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
    'preseason_total': [50, 31, 25, 20, 15, 10,  5,  0,  0,  0,  0,  0],
    'preseason_avg':   [50, 31, 25, 20, 15, 10,  9,  8,  7,  5,  3,  2],
}

sharp_weights = {
    # week               0   1   2   3   4   5   6   7
    'proj':            [ 0, 25, 27, 32, 42, 52, 55, 57],
    'moving_proj':     [ 0,  0,  5, 11, 15, 15, 16, 16],
    'total':           [ 0,  0,  0,  0,  0,  0,  0,  0],
    'avg':             [ 0,  0,  0,  0,  0,  0,  0,  0],
    'moving_avg':      [ 0,  0,  3,  6,  8, 10, 12, 12],
    'exp_roster':      [ 0, 15, 15, 15, 13, 11, 10, 10],
    'preseason_total': [50, 30, 25, 18, 11,  6,  2,  0],
    'preseason_avg':   [50, 30, 25, 18, 11,  6,  5,  5],
}

position_group_list = {
    'football': ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST'],
    'baseball': ['SP', 'RP', 'B'],
}

position_group_map = {
    'football': {},
    'baseball': {
        'SP': 'SP',
        'RP': 'RP',
        'default' : 'B',
    }
}

position_pool_size = {
    'football': {
        'QB':   20,
        'RB':   50,
        'WR':   50,
        'TE':   20,
        'K':    15,
        'D/ST': 15,
    },
    'baseball': {
        'SP':   60,
        'RP':   30,
        'B':   140,
    },
}

team_position_weights = {
    'football': {
        'QB':   [1.0, 0.3],
        'RB':   [1.0, 1.0, 0.8, 0.5, 0.3],
        'WR':   [1.0, 1.0, 0.8, 0.5, 0.3],
        'TE':   [1.0, 0.3],
        'K':    [0.2],
        'D/ST': [0.3, 0.2],
    },
    'baseball': {
        'SP':   [1.0, 1.0, 1.0, 0.7, 0.4, 0.2],
        'RP':   [0.7, 0.4, 0.2],
        'B':    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2],
    }
}


# get information from above tables

def get_position_group(sport, pos):
    groups = position_group_map[sport]
    pos_group = groups.get(pos)
    default = groups.get('default')
    return pos_group or default

def get_stat_weight(stat, week, rating_type='normal'):
    weights = sharp_weights if rating_type == 'sharp' else normal_weights
    n_weeks = len(weights[stat])
    idx = -1 if week >= n_weeks else week
    return weights[stat][idx]

def get_position_pool_size(position, sport):
    pool_size = position_pool_size[sport].get(position)
    wildcard = position_pool_size[sport].get('*')
    return pool_size or wildcard

def get_team_position_weight(idx, position, sport, default=0.05):
    pos_weight = team_position_weights[sport].get(position)
    wildcard = team_position_weights[sport].get('*')
    pos_weight = pos_weight or wildcard
    if idx >= len(pos_weight):
        return default
    else:
        return pos_weight[idx]
