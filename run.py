import time
from model.config import leagues
from model.fetch.fetcher import DataFetcher
from model.league.league import League
from model.process.processor import Processor


def input_selection(options):
    for i, l in enumerate(options):
        print(f'({i + 1}) {l}')

    while True:
        sel = input('enter number: ')
        if sel.lower() == 'q':
            exit(1)
        try:
            idx = int(sel) - 1
            choice = options[idx]
            print()
            return choice
        except:
            print('--> invalid choice (enter q to quit)')


print('--- select a sport ---')
sport_options = list(leagues.keys())
sport_tag = input_selection(sport_options)

print('--- select a league ---')
league_options = list(leagues[sport_tag].keys())
league_tag = input_selection(league_options)

print('--- upcoming week ---')
week = input('enter week: ')
try:
    week = int(week)
    assert week >= 0
    print()
except:
    print('--> invalid week recieved')
    exit(1)

fetcher = DataFetcher(sport_tag, league_tag, week)
print('--> initialized')
print()

while True:
    print(f'{sport_tag} {league_tag} week={week}')
    print('--- select an action ---')
    action_options = [
        'sim',
        'fetch league data',
        'fetch player data',
        'fetch draft data',
        'quit',
    ]
    action = input_selection(action_options)

    if action == 'sim':
        league = League(sport_tag, league_tag, week)
        processor = Processor(league)
    elif action == 'fetch league data':
        fetcher.fetch_schedule()
        fetcher.fetch_members()
        fetcher.fetch_rosters()
    elif action == 'fetch player data':
        fetcher.fetch_players()
    elif action == 'fetch draft data':
        fetcher.fetch_players()
        fetcher.fetch_draft()
    else:
        print('--> exiting')
        exit(0)
    print('done.\n')
    time.sleep(0.5)
