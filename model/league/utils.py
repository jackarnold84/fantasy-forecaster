from config import Config


# get team name from full manager name
def get_team_name(manager_name, use_alias=True):
    cfg = Config()
    if use_alias and manager_name in cfg.aliases:
        return cfg.aliases[manager_name]
    first_name = manager_name.split(' ')[0][0:10]
    return first_name.lower().capitalize()


# z score
def z_score(x, mean, sd, new_mean=0, new_sd=1):
    if x is None or mean is None or sd is None:
        return None
    elif sd <= 0:
        return new_mean
    z = (x - mean) / sd
    return z*new_sd + new_mean


# projection using MLE method
def get_mle_projection(x, n, mean_scores, sd_scores, sd_team):
    f1 = x * n * (sd_team**2)
    f2 = mean_scores * (sd_scores**2)
    f3 = n * (sd_team**2) + (sd_scores**2)
    return (f1 + f2) / f3
