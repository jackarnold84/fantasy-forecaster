import numpy as np


# convert week map to array
def get_sequence(map, week):
    return [map[w] for w in range(1, week + 1) if map.get(w) is not None]


# weighted moving average
def wma(arr, r=0.75):
    if len(arr) < 1:
        return None
    weights = [*reversed([r**i for i in range(len(arr))])]
    weighted_arr = [arr[i]*weights[i] for i in range(len(arr))]
    return sum(weighted_arr) / sum(weights)


# set a min/max boundary for a value
def bound(x, min_val, max_val):
    return max(min(x, max_val), min_val)


# z score
def z_score(x, mean, sd, new_mean=0, new_sd=1):
    if x is None or mean is None or sd is None:
        return None
    z = (x - mean) / max(sd, 0.001)
    return z*new_sd + new_mean


# parse by type, default to None
def parse_value(x, value_type=str):
    if value_type == str:
        x = str(x)
        return None if x == '' else x
    elif value_type == int:
        try:
            return int(x)
        except:
            return None
    elif value_type == float:
        try:
            x = round(float(x), 3)
            return None if np.isnan(x) else x
        except:
            return None
