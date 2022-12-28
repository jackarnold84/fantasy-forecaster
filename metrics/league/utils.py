import numpy as np

# consts

positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']

position_weight_order = {
    'normal': {
        'QB':   [1.0, 0.3],
        'RB':   [1.0, 1.0, 0.8, 0.5, 0.3],
        'WR':   [1.0, 1.0, 0.8, 0.5, 0.3],
        'TE':   [1.0, 0.3],
        'K':    [0.2],
        'D/ST': [0.3, 0.2],
    },
    'sharp': {
        'QB':   [1.0, 0.2],
        'RB':   [1.0, 1.0, 0.7, 0.3],
        'WR':   [1.0, 1.0, 0.7, 0.3],
        'TE':   [1.0, 0.2],
        'K':    [0.2],
        'D/ST': [0.3],
    }
}

rating_adjust_params = {
    'normal': {
        'team': {'mean': 56.8, 'sd': 6.2},
        'QB':   {'mean':  7.4, 'sd': 2.0},
        'RB':   {'mean': 20.0, 'sd': 4.0},
        'WR':   {'mean': 19.8, 'sd': 4.5},
        'TE':   {'mean':  7.1, 'sd': 2.6},
    },
    'sharp': {
        'team': {'mean': 51.7, 'sd': 6.2},
    }
}

rating_scale_params = {
    'min': 25,
    'max': 99,
    'mean': 70,
    'sd': 12,
}


# functions

def position_weight(pos, rank, type='normal', default=0.1):
    type = type if type in position_weight_order else 'normal'
    if len(position_weight_order[type][pos]) > rank:
        return position_weight_order[type][pos][rank]
    else:
        return default


def sort_list_of_dicts(arr, by, reverse=True):
    # removes 'None' values and sorts by value
    new_arr = [x for x in arr if x[by] is not None]
    new_arr = sorted(new_arr, key=lambda d: d[by], reverse=reverse)
    return new_arr


def mean(arr, top=None):
    if not arr:
        return None
    if top:
        filt = sorted(arr, reverse=True)[0:top]
        return np.mean(filt)
    else:
        return np.mean(arr)

def std(arr, top=None):
    if not arr:
        return None
    if top:
        filt = sorted(arr, reverse=True)[0:top]
        return np.std(filt)
    else:
        return np.std(arr)

def z_score(x, avg, sd, new_avg=0, new_sd=1):
    z = (x - avg) / sd
    return z*new_sd + new_avg
