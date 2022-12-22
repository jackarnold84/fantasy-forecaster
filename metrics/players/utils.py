import numpy as np

# consts

positions = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']

z_stats = [
    'projection',
    'moving_projection',
    'season_total',
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
    'moving_avg': 3.0,
    'sharp_moving_avg': 3.0,
    'expected_rostered': 0.05,
    'preseason_total': 40.0,
    'preseason_avg': 3.0,
}


# functions

def z_score(x, avg, sd, count):
    if x is None or avg is None or sd is None or count is None:
        return None
    if count < 10:
        return None
    return (x - avg) / sd if x is not None else None


def mean(arr):
    return np.mean(arr) if arr else None

def std(arr):
    return np.std(arr) if arr else None


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
