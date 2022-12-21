import pandas as pd
import re

# consts
POSITIONS = ['QB', 'RB', 'WR', 'TE', 'K', 'D/ST']
HEALTH_INDICATORS = ['IR', 'O', 'Q', 'D']
RECORDS_PER_PAGE = 50


# utils
def read_csv_file(file):
    df = pd.DataFrame()
    try:
        df = pd.read_csv(file, header=None)
    except pd.errors.EmptyDataError:
        print('--> Note: file is empty', file)
    except FileNotFoundError:
        print('--> Note: file does not exist', file)
    return df

def parse_float(x):
    try:
        return round(float(x), 2)
    except ValueError:
        return None

def parse_float_percentage(x):
    try:
        return round(float(x) / 100, 3)
    except ValueError:
        return None

def parse_int(x):
    try:
        return int(x)
    except ValueError:
        return None


# clean functions
def name_clean(x):
    return re.sub(r'[^A-Za-z0-9 ]+', '', x).replace('  ', ' ').strip()

def extract_name_and_health(name_health):
    player_name = name_health
    health = 'H'
    for ind in HEALTH_INDICATORS:
        if name_health.endswith(ind):
            player_name, _ = name_health.rsplit(ind, 1)
            health = ind
            break
    player_name = player_name.strip()
    return player_name, health

def extract_team_and_pos(team_pos):
    team, position = None, None
    for pos in POSITIONS:
        if team_pos.endswith(pos):
            team, _ = team_pos.rsplit(pos, 1)
            position = pos
            break
    team = team.strip()
    return team, position

def extract_opponent(opp_str):
    opponent = None
    if 'BYE' in opp_str:
        opponent = 'BYE'
    elif opp_str and '--' not in opp_str:
        opponent = opp_str.strip()
    return opponent



# read player list
# (from ESPN add players tab)
def read_player_list(file):
    df = read_csv_file(file)
    rows = df.to_dict('records')

    filter_text = ['PLAYER', 'PLAYERS']
    rows = [x for x in rows if not any([s in x[0] for s in filter_text])]
    assert(len(rows) % 3 == 0), 'unequal player record chunks'

    joined_rows = []
    for i in range(len(rows) // 3):
        start = i * 3   
        joined_rows.append({
            'info': rows[start],
            'player_name': rows[start + 1],
            'team_pos': rows[start + 2]
        })
    
    data = []
    for x in joined_rows:

        # player name and health
        name_health = x['player_name'][0]
        player_name, health = extract_name_and_health(name_health)

        # team and position
        team_pos = x['team_pos'][0]
        team, position = extract_team_and_pos(team_pos)

        #  projection, score
        projection = parse_float(x['info'][5])
        score = parse_float(x['info'][6])
        prev_score = parse_float(x['info'][14])

        # roster%, start%
        started = parse_float_percentage(x['info'][8])
        rostered = parse_float_percentage(x['info'][9])

        # season stats
        pos_rank = parse_int(x['info'][11])
        season_total = parse_float(x['info'][12])
        season_avg = parse_float(x['info'][13])

        # opponent
        opponent = extract_opponent(x['info'][3])
        
        # games played
        if season_total and season_avg:
            games_played = int(round(season_total / season_avg, 0))
        else:
            games_played = 0

        data.append(
            {
                'player_name': player_name, 
                'team': team, 
                'position': position, 
                'health': health,
                'projection': projection, 
                'score': score,
                'opponent': opponent,
                'prev_score': prev_score,
                'started': started,
                'rostered': rostered,
                'pos_rank': pos_rank, 
                'season_total': season_total, 
                'season_avg': season_avg, 
                'games_played': games_played
            }
        )

    return data



# read player stats
# (from ESPN scoring leaders page)
def read_player_stats(file):
    df = read_csv_file(file)
    rows = df.to_dict('records')

    filter_text = ['PLAYER', 'TOTAL', 'FPTS', 'PASSING', 'C/A']
    rows = [x for x in rows if not any([s in x[0] for s in filter_text])]
    assert(len(rows) % (5 * RECORDS_PER_PAGE) == 0), 'unequal player record chunks'

    joined_rows = []
    for i in range(len(rows) // (5 * RECORDS_PER_PAGE)):
        start = i * (5 * RECORDS_PER_PAGE)
        for j in range(RECORDS_PER_PAGE):       
            k = start + j
            joined_rows.append({
                'player': {
                    'info': rows[start + 3 * j],
                    'name': rows[start + 3 * j + 1],
                    'team_pos': rows[start + 3 * j + 2]
                },
                'stats': rows[k + 3 * RECORDS_PER_PAGE],
                'score': rows[k + 4 * RECORDS_PER_PAGE]
        })

    data = []
    for x in joined_rows:

        # player name and health
        name_health = x['player']['name'][0]
        player_name, health = extract_name_and_health(name_health)

        # team and position
        team_pos = x['player']['team_pos'][0]
        team, position = extract_team_and_pos(team_pos)

        #  projection, score
        projection = parse_float(x['player']['info'][5])
        score = parse_float(x['score'][0])

        # opponent
        opponent = extract_opponent(x['player']['info'][3])

        data.append(
                {
                    'player_name': player_name, 
                    'team': team, 
                    'position': position, 
                    'health': health,
                    'projection': projection, 
                    'score': score,
                    'opponent': opponent
                }
            )

    return data
