import re


def get_urls(sport, league_id):
    return {
        'schedule': f'https://fantasy.espn.com/{sport}/league/schedule?leagueId={league_id}',
        'members': f'https://fantasy.espn.com/{sport}/tools/leaguemembers?leagueId={league_id}',
        'rosters': f'https://fantasy.espn.com/{sport}/league/rosters?leagueId={league_id}',
        'draft': f'https://fantasy.espn.com/{sport}/league/draftrecap?leagueId={league_id}',
        'players': f'https://fantasy.espn.com/{sport}/players/add?leagueId={league_id}',
    }


def get_data_paths(sport, year, league_tag):
    return {
        'schedule': f'data/{sport}-{year}/leagues/{league_tag}/schedule.csv',
        'members': f'data/{sport}-{year}/leagues/{league_tag}/members.csv',
        'rosters': f'data/{sport}-{year}/leagues/{league_tag}/rosters.csv',
        'draft': f'data/{sport}-{year}/leagues/{league_tag}/draft.csv',
        'player_info': f'data/{sport}-{year}/players/info.csv',
        'player_stats': f'data/{sport}-{year}/players/stats.csv',
    }


# cleaning functions

def fix_spacing(text):
    text = text.strip()
    text = re.sub(r'[\r|\n|\t]', ' ', text)
    text = re.sub(r'[ ]+', ' ', text)
    return text


def alphanumeric(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)


def parse_float(x, default=None):
    try:
        return float(x)
    except:
        return default


def parse_int(x, default=None):
    try:
        return int(x)
    except:
        return default


def clean_text(s):
    return fix_spacing(alphanumeric(s))


def clean_symbol(s):
    if not s or s == '--':
        return None
    return fix_spacing(s).split(' ')[0].upper()


def get_player_id(name, pos):
    return '%s-%s' % (
        clean_text(name).lower().replace(' ', ''),
        pos.upper(),
    )


def get_primary_pos(pos):
    return fix_spacing(pos.split(',')[0]).upper()


# correcting positions
def player_pos_mapper(pos):
    mapper = {
        'LF': 'OF',
        'CF': 'OF',
        'RF': 'OF',
    }
    return mapper.get(pos) or pos
