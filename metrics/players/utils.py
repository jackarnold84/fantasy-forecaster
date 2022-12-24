import numpy as np

# consts

z_stats = [
    'projection',
    'moving_projection',
    'season_total',
    'season_avg',
    'moving_avg',
    'sharp_moving_avg',
    'expected_rostered',
    'preseason_total',
    'preseason_avg',
]

z_stats_thresholds = {
    'projection': 3.0,
    'moving_projection': 3.0,
    'season_total': 3.0,
    'season_avg': 3.0,
    'moving_avg': 3.0,
    'sharp_moving_avg': 3.0,
    'expected_rostered': 0.05,
    'preseason_total': 40.0,
    'preseason_avg': 3.0,
}

z_stats_week_adj = {
    'projection': 1,
    'moving_projection': 1,
    'season_total': 0,
    'season_avg': 0,
    'moving_avg': 0,
    'sharp_moving_avg': 0,
    'expected_rostered': 1,
    'preseason_total': 0,
    'preseason_avg': 0,
}

positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']

# approx this number will be given a positive rating
position_pool_size = {
    'QB': 20,
    'RB': 50,
    'WR': 50,
    'TE': 20,
    'K': 15,
    'D/ST': 15,
}

position_color_map = {
    'QB': 'light-blue',
    'RB': 'light-green',
    'WR': 'light-orange',
    'TE': 'light-purple',
    'K': 'light-red',
    'D/ST': 'light-grey',
}

status_correction = {
    'rating': {
        'active': 1.0,
        'bye': 1.0,
        'unhealthy': 0.9,
        'injured': 0.8,
        'inactive': 0.8,
        None: 1.0,
    },
    'sharp_rating': {
        'active': 1.0,
        'bye': 0.8,
        'unhealthy': 0.8,
        'injured': 0.6,
        'inactive': 0.6,
        None: 0.8,
    }
}

rating_mean = 5.0
rating_sd = 2.40


# functions

def z_score(x, avg, sd, count, new_avg=0, new_sd=1):
    if x is None or avg is None or sd is None or count is None:
        return None
    if count < 8:
        return None
    z = (x - avg) / sd
    return z*new_sd + new_avg


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

def rank(arr, rank):
    if not arr:
        return None
    sorted_arr = sorted(arr, reverse=True)
    if len(sorted_arr) >= rank - 1:
        return sorted_arr[-1]
    else:
        return sorted_arr[rank - 1]

def rnd(x, ndigits=1):
    return round(x, ndigits) if x else None


# custom weighted moving average
def wma(arr, type=''):
    if type == 'sharp':
        base = 2
        ends = [8, 7, 5, 3]
    elif type == 'flat':
        base = 1
        ends = [1]
    else:
        base = 8
        ends = [12, 11, 10, 9]

    # determine if computable
    cnt = sum([1 for x in arr[-5:] if x is not None])
    if cnt < 3:
        return None

    weights = [base for _ in range(
        len(arr) - len(ends))] + list(reversed(ends))
    N = len(arr)
    a = 0
    b = 0
    for i in range(N):
        if arr[i] is not None:
            a += arr[i] * weights[i]
            b += weights[i]
    return a / b


def recent_instance(arr, within=3):
    for x in reversed(arr[-3:]):
        if x is not None:
            return x
    return None


def diffs_with_blanks(arr):
    def subt(x, y):
        return x - y if x is not None and y is not None else None
    return [None] + [subt(arr[i], arr[i-1]) for i in range(1, len(arr))]


def rostered_sigmoid(x):
    sig_x = 100 * (1+np.exp(-0.07*(x-50)))
    if x > 96.0 or x < 4.0:
        return sig_x
