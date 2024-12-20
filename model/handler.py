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
    action = payload.get('action', '')
    sport_tag = payload.get('sport', '')
    league_tag = payload.get('league', '')
    week = payload.get('week', None)
    iters = payload.get('iter', None)

    # validate
    cfg = Config()
    if not action or not sport_tag or not league_tag:
        raise Exception('required parameters: action, sport, league')
    if sport_tag not in cfg.leagues or league_tag not in cfg.leagues[sport_tag]:
        raise Exception('provided sport/league not found in config')

    if week is None:
        week = cfg.get_current_week(sport_tag)
    else:
        week = int(week)

    if iters is not None:
        iters = int(iters)

    # perform action
    if action == 'sim':
        league = League(sport_tag, league_tag, week, iters)
        Processor(league)

    elif action in ['fetchLeague', 'fetchPlayers', 'fetchDraft']:
        fetcher = DataFetcher(sport_tag, league_tag, week)
        print('--> initialized data fetcher')

        if action == 'fetchLeague':
            fetcher.fetch_schedule()
            fetcher.fetch_members()
            fetcher.fetch_rosters()

        elif action == 'fetchPlayers':
            fetcher.fetch_players()

        elif action == 'fetchDraft':
            fetcher.fetch_draft()

    else:
        raise Exception('invalid action provided')

    return {
        'status': 'SUCCESS',
        'action': action,
        'sport': sport_tag,
        'league': league_tag,
        'week': week,
    }
