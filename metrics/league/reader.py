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
        print('--> Note: file is empty (%s)' % file)
    except FileNotFoundError:
        print('--> Note: file does not exist (%s)' % file)
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
def name_clean(x, lower=False):
    x = re.sub(r'[^A-Za-z0-9 ]+', '', x).replace('  ', ' ').strip()
    if lower:
        x = x.lower()
    return x

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



# read members file
# (from ESPN members tab)
def read_members(file):
    df = read_csv_file(file)

    data = []
    for x in df.iloc:
        if x[1] == 'ABBRV' or pd.isna(x[0]):
            continue

        team_number = x[0]
        team_abbrev = x[1]
        team_name = name_clean(x[2], lower=True)
        division = name_clean(x[3])
        manager_name = name_clean(x[4])

        # TODO: aliases
        
        data.append(
            {
                'manager_name': manager_name,
                'team_name': team_name,
                'team_abbrev': team_abbrev,
                'team_number': team_number,
                'division': division,
            }
        )

    return data



# read rosters file
# (from ESPN rosters tab)
def read_rosters(file):
    df = read_csv_file(file)
    rows = df.to_dict('records')

    filter_text = ['SLOT', 'View Team', 'Propose Trade']
    rows = [x for x in rows if not any([s in str(x[0]) for s in filter_text])]

    joined_rows = []
    for i in range(len(rows)):
        if not rows[i][0]:
            continue
        elif not pd.isna(rows[i][0]) and not pd.isna(rows[i][1]) and not pd.isna(rows[i][2]):
            joined_rows.append({
                'info': rows[i],
                'name': rows[i + 1],
                'team_pos': rows[i + 2]
            })
        elif not pd.isna(rows[i][0]) and pd.isna(rows[i][1]) and pd.isna(rows[i][2]):
            joined_rows.append({
                'fantasy_team': rows[i],
            })

    current_team = None
    
    data = []
    for x in joined_rows:

        # current team
        if 'fantasy_team' in x:
            team_name, _ = x['fantasy_team'][0].rsplit('(')
            team_name = name_clean(team_name, lower=True)
            current_team = team_name
            continue

        # player name and health
        name_health = x['name'][1]
        player_name, health = extract_name_and_health(name_health)

        # team and position
        team_pos = x['team_pos'][1]
        team, position = extract_team_and_pos(team_pos)

        # aquired method
        aquired = x['info'][2].strip()

        data.append(
            {
                'team_name': current_team,
                'player_name': player_name,
                'position': position,
                'team': team,
                'health': health,
                'aquired': aquired
            }
        )

    return data




# read draft recap file
# (from ESPN draft recap tab)
def read_draft_recap(file):
    df = read_csv_file(file)

    current_round = None
    current_pick = 1
    
    data = []
    for x in df.iloc:
        if 'NO.' in x[0]:
            continue

        # current team
        if 'Round' in x[0]:
            _, round_no = x[0].rsplit(' ')
            current_round = int(round_no)
            continue
        
        # player name, team, position
        name_team, position = x[1].replace(u'\xa0', u' ').rsplit(', ', 1)
        player_name, team = name_team.rsplit(' ', 1)
        assert(position in POSITIONS), 'unknown position encountered'

        # fantasy team name
        team_name = name_clean(x[2], lower=True)

        data.append(
            {
                'overall_pick': current_pick,
                'round': current_round,
                'player_name': player_name,
                'position': position,
                'team': team,
                'team_name': team_name,
            }
        )
        current_pick += 1

    return data
