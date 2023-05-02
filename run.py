import sys
import json
from model.fetch.fetcher import DataFetcher

# config
config = {}
with open('config.json') as f:
    config = json.load(f)


# read arguments
args = [a.lower() for a in sys.argv]
try:
    action = args[1]
    assert action in ['fetch']
    sport_tag = args[2]
    league_tag = args[3]
    week = int(args[4])
    flags = args[5:]
except:
    print('error: invalid arguments')
    print('  run.py fetch <sport> <league> <week>    # fetch data from ESPN')
    print('    [--league-only]')
    print('    [--players-only]')
    print('    [--draft]')
    print('  run.py sim <sport> <league> <week>      # run model simulation')
    exit(1)


# get league config
if (
    sport_tag not in config['leagues'] or
    league_tag not in config['leagues'][sport_tag]
):
    valid_leauges = [
        f'{x} {y}' for x in config['leagues'] for y in config['leagues'][x]
    ]
    print('error: league not found')
    print('  leagues:', valid_leauges)
    exit(1)

league_config = config['leagues'][sport_tag][league_tag]
sport, year = league_config['sport'].split('-')
league_tag = league_config['tag']
league_id = league_config['league_id']


if action == 'fetch':
    fetcher = DataFetcher(sport, year, week, league_id, league_tag)
    if '--draft' in flags:
        fetcher.fetch_draft()
    else:
        if '--players-only' not in flags:
            fetcher.fetch_schedule()
            fetcher.fetch_members()
            fetcher.fetch_rosters()
        if '--league-only' not in flags:
            fetcher.fetch_players()
