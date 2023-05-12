import sys
from model.fetch.fetcher import DataFetcher
from model.config import leagues


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


# validate sport + league exists
valid_leauges = [f'{x} {y}' for x in leagues for y in leagues[x]]
if (
    sport_tag not in leagues or
    league_tag not in leagues[sport_tag]
):
    print('error: league not found')
    print('  leagues:', valid_leauges)
    exit(1)


# actions
if action == 'fetch':
    fetcher = DataFetcher(sport_tag, league_tag, week)
    if '--draft' in flags:
        fetcher.fetch_draft()
    else:
        if '--players-only' not in flags:
            fetcher.fetch_schedule()
            fetcher.fetch_members()
            fetcher.fetch_rosters()
        if '--league-only' not in flags:
            fetcher.fetch_players()
