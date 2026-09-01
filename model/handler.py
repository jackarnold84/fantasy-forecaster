from config import Config
from fetch.fetcher import DataFetcher
from league.league import League
from process.processor import Processor


def handler(event, _):
    payload = event
    if event.get('detail-type') == 'Scheduled Event':
        payload = event.get('detail', {})

    # read payload
    print('--> received payload:', payload)
    # An omitted action is the normal scheduled/manual update: collect current
    # ESPN data and then run the forecast.  `fetch` and `sim` are useful for
    # targeted recovery or debugging.
    action = payload.get('action', 'run')
    sport_tag = payload.get('sport', '')
    league_tag = payload.get('league', '')
    week = payload.get('week', None)
    iters = payload.get('iter', None)

    # validate
    cfg = Config()
    if not sport_tag or not league_tag:
        raise Exception('required parameters: sport, league')
    if sport_tag not in cfg.leagues or league_tag not in cfg.leagues[sport_tag]:
        raise Exception('provided sport/league not found in config')

    if week is None:
        week = cfg.get_current_week(sport_tag)
    else:
        week = int(week)

    if iters is not None:
        iters = int(iters)

    is_sleeper = cfg.leagues[sport_tag][league_tag].get('app', 'espn') == 'sleeper'

    if action not in {'run', 'fetch', 'sim'}:
        raise Exception('invalid action provided; use run, fetch, or sim')

    # Sleeper projections/players are sourced from the existing shared data,
    # so its normal update deliberately skips collection.
    if action in {'run', 'fetch'} and not is_sleeper:
        fetcher = DataFetcher(sport_tag, league_tag, week)
        print('--> initialized ESPN API fetcher')
        fetcher.fetch_league()
        fetcher.fetch_players()
    elif action == 'fetch' and is_sleeper:
        print('--> Sleeper fetch skipped; it uses existing shared player data')

    if action in {'run', 'sim'}:
        league = League(sport_tag, league_tag, week, iters)
        Processor(league)

    return {
        'status': 'SUCCESS',
        'action': action,
        'sport': sport_tag,
        'league': league_tag,
        'week': week,
    }
