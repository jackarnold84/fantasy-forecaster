# reader.py:
# process raw league schedule data from 'data/' folder

import pandas as pd
import json


with open('config.json') as f:
    config = json.load(f)


def read_league_data(league_id):

    in_file = 'data/leagues/%s/schedule.csv' % league_id
    aliases = config['leagues'][league_id]['aliases']

    def alias(name):
        if name in aliases:
            return aliases[name]
        else:
            parts = name.split(' ')
            return parts[0] if len(parts[0]) <= 8 else parts[0][0:8]

    week_counter = 0
    playoff_week_counter = 0
    current_week = 0
    matchup_type = 'Regular Season'
    data = {'week': [], 'type': [], 'away_team': [], 'away_score': [], 'home_team': [], 'home_score': []}

    df = pd.read_csv(in_file, header=None)
    for r in df.iloc:

        if 'Playoff Round' in str(r[0]):
            playoff_week_counter += 1
            current_week = None
            matchup_type = 'Playoff R%d' % playoff_week_counter
        elif 'NFL Week' in str(r[0]):
            week_counter += 1
            current_week = week_counter
        elif 'Matchup' in str(r[0]):
            week_counter += 1
            current_week = week_counter
        
        elif str(r[1]) == 'nan':
            continue
        elif 'AWAY TEAM' in str(r[0]):
            continue

        else:
            data['week'].append(current_week)
            data['type'].append(matchup_type)
            data['away_score'].append(float(r[2]))
            data['home_score'].append(float(r[3]))
            data['away_team'].append(alias(r[1]))
            data['home_team'].append(alias(r[4]))

    result = pd.DataFrame(data)
    return result
