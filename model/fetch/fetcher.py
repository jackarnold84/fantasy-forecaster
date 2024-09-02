import pathlib
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from model.config import leagues
from model.credentials import path_to_chromedriver
from model.fetch.utils import (clean_symbol, clean_text, get_data_paths,
                               get_player_id, get_primary_pos, get_urls,
                               parse_float, parse_int, parse_score,
                               player_pos_mapper)


class DataFetcher:

    def __init__(self, sport_tag, league_tag, week):
        league_config = leagues[sport_tag][league_tag]
        self.sport, self.year = sport_tag.split('-')
        self.week = str(week)
        self.league_id = league_config['league_id']
        self.league_tag = league_tag
        self.url = get_urls(self.sport, self.league_id)
        self.path = get_data_paths(self.sport, self.year, self.league_tag)

        # set up webdriver
        service = Service(executable_path=path_to_chromedriver)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(service=service, options=options)

    def driver_get(self, url, wait=10, wait_query=None):
        self.driver.get(url)
        if wait_query:
            try:
                WebDriverWait(self.driver, wait).until(
                    EC.presence_of_element_located(wait_query)
                )
                time.sleep(1)
            except Exception:
                print('Error: selenium timeout occured for %s' % url)
        else:
            time.sleep(wait)

    def driver_quit(self):
        self.driver.quit()

    def read_data(self, path):
        if not pathlib.Path(path).is_file():
            return []
        df = pd.read_csv(path)
        return df.to_dict('records')

    def write_data(self, data, path, sort):
        data = sorted(data, key=sort)
        df = pd.DataFrame(data)
        dir = path.rsplit('/', 1)[0]
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    def update_data(self, data, path, sort, filter):
        current_data = self.read_data(path)
        current_data = [x for x in current_data if filter(x)]
        new_data = current_data + data
        self.write_data(new_data, path, sort)

    def insert_data(self, data, path, sort, key):
        current_data = self.read_data(path)
        data_map = {key(x): x for x in current_data}
        for x in data:
            data_map[key(x)] = x
        new_data = [*data_map.values()]
        self.write_data(new_data, path, sort)

    def fetch_schedule(self):
        url = self.url['schedule']
        print('--> fetching schedule')
        self.driver_get(url, wait=10, wait_query=(By.CLASS_NAME, 'teamName'))
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        schedule_data = []
        matchup_tables = soup.select('.matchup--table')
        for i, table in enumerate(matchup_tables):
            tbody = table.select_one('tbody')
            table_caption = table.select_one('.table-caption')
            if 'Matchups to be determined' in tbody.text:
                break
            for j, row in enumerate(tbody.select('tr')):
                entries = row.select('td')
                schedule_data.append({
                    'week': i + 1,
                    'matchup_idx': j + 1,
                    'playoff': 'playoff' in table_caption.text.lower(),
                    'home': clean_text(entries[4].text),
                    'home_score': parse_score(entries[3].text),
                    'away': clean_text(entries[1].text),
                    'away_score': parse_score(entries[2].text),
                })

        path = self.path['schedule']
        self.write_data(
            schedule_data,
            path,
            sort=lambda x: (
                x['playoff'], parse_int(x['week']), x['matchup_idx'],
            ),
        )
        print('--> schedule written to %s' % path)

    def fetch_members(self):
        url = self.url['members']
        print('--> fetching members')
        self.driver_get(url, wait=10, wait_query=(By.CLASS_NAME, 'teamName'))
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        members_data = []
        members_table = soup.select_one('.leagueMembersTable')
        tbody = members_table.select_one('tbody')
        for row in tbody.select('tr'):
            entries = row.select('td')
            if not entries[0].text:
                continue
            team_logo_holder = row.select_one('.team-logo')
            team_logo = team_logo_holder.select_one('img').attrs['src']
            members_data.append({
                'id': int(entries[0].text),
                'manager': clean_text(entries[3].text),
                'team_name': clean_text(entries[2].text),
                'abbrev': entries[1].text,
                'division': 'USA',  # temporary fix
                'img': team_logo,
            })

        path = self.path['members']
        self.write_data(
            members_data,
            path,
            sort=lambda x: x['id'],
        )
        print('--> members written to %s' % path)

    def fetch_rosters(self):
        url = self.url['rosters']
        print('--> fetching rosters')
        self.driver_get(url, wait=10, wait_query=(By.CLASS_NAME, 'teamName'))
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        # get team names from member table
        member_data = self.read_data(self.path['members'])
        team_name_to_id = {
            x['team_name']: x['id'] for x in member_data
        }

        roster_data = []
        for roster_table in soup.select('.rosterTable'):
            tbody = roster_table.select_one('tbody')
            team_name_holder = roster_table.select_one('.teamName')
            team_name = clean_text(team_name_holder.text)
            assert team_name in team_name_to_id, 'error: team name not found %s' % team_name
            manager_id = team_name_to_id[team_name]
            for j, row in enumerate(tbody.select('tr')):
                entries = row.select('td')
                player_name_holder = row.select_one('.player-column__athlete')
                if not player_name_holder:
                    continue
                player_name_holder = player_name_holder.select_one('span')
                player_name = clean_text(player_name_holder.text)
                player_pos_holder = row.select_one('.playerinfo__playerpos')
                player_pos = get_primary_pos(player_pos_holder.text)
                player_id = get_player_id(player_name, player_pos)
                roster_data.append({
                    'week': self.week,
                    'manager_id': manager_id,
                    'slot_idx': j + 1,
                    'player_id': player_id,
                    'aquired': entries[2].text,
                })

        path = self.path['rosters']
        self.update_data(
            roster_data,
            path,
            sort=lambda x: (
                parse_int(x['week'], 0), x['manager_id'], x['slot_idx'],
            ),
            filter=lambda x: str(x['week']) != str(self.week)
        )
        print('--> rosters written to %s' % path)

    def fetch_draft(self):
        url = self.url['draft']
        print('--> fetching draft')
        self.driver_get(url, wait=10, wait_query=(By.CLASS_NAME, 'teamName'))

        # select by team
        view_by_filters = self.driver.find_elements(By.CLASS_NAME, 'clr-link')
        view_by_filters[1].click()
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        draft_data = []
        for i, recap_table in enumerate(soup.select('.draftRecapTable')):
            tbody = recap_table.select_one('tbody')
            for row in tbody.select('tr'):
                elements = row.select('td')
                pick_number = elements[0].text
                player_info_holders = elements[1].select('span')
                player_name = clean_text(player_info_holders[0].text)
                player_pos = get_primary_pos(player_info_holders[2].text)
                player_pos = player_pos_mapper(player_pos)
                player_id = get_player_id(player_name, player_pos)
                round_number = elements[2].text

                draft_data.append({
                    'pick': parse_int(pick_number),
                    'round': parse_int(round_number),
                    'manager_id': i + 1,
                    'player_id': player_id,
                })

        path = self.path['draft']
        self.write_data(
            draft_data,
            path,
            sort=lambda x: x['pick'],
        )
        print('--> draft written to %s' % path)

    # players
    def fetch_players(self):
        url = self.url['players']
        print('--> fetching players')
        self.driver_get(url, wait=10, wait_query=(
            By.CLASS_NAME, 'player-column__athlete'))

        # set status to all players
        status_filter = self.driver.find_element(By.ID, 'filterStatus')
        select = Select(status_filter)
        select.select_by_value('ALL')
        time.sleep(2)

        # preseason projections if week = 0
        if self.week == '0':
            stat_filter = self.driver.find_element(By.ID, 'filterStat')
            select = Select(stat_filter)
            select.select_by_value('projections')
            time.sleep(2)
        else:
            stat_filter = self.driver.find_element(By.ID, 'filterStat')
            select = Select(stat_filter)
            select.select_by_value('currSeason')

        # read pages
        soup_pages = []

        def paginate(n=5):
            soup_pages.append(
                BeautifulSoup(self.driver.page_source, 'lxml')
            )
            for _ in range(n - 1):
                self.driver.find_element(
                    By.CLASS_NAME, 'Pagination__Button--next'
                ).click()
                time.sleep(2)
                soup_pages.append(
                    BeautifulSoup(self.driver.page_source, 'lxml')
                )

        # for reading multiple positions
        add_pos_idx = []
        if self.sport == 'baseball':
            add_pos_idx = [1]

        paginate()
        if add_pos_idx:
            for idx in add_pos_idx:
                position_filters = self.driver.find_elements(
                    By.CLASS_NAME, 'control'
                )
                position_filters[idx].click()
                time.sleep(2)
                paginate()

        # fill
        player_info = []
        player_stats = []
        seen = set()

        for soup in soup_pages:
            joined_tables = soup.select('.Table')
            joined_tbodies = [t.select_one('tbody') for t in joined_tables]
            if len(joined_tbodies) == 3:
                player_table_rows = joined_tbodies[0].select('tr')
                stats_table_rows = joined_tbodies[1].select('tr')
                points_table_rows = joined_tbodies[2].select('tr')
            elif len(joined_tables) == 2:
                player_table_rows = joined_tbodies[0].select('tr')
                stats_table_rows = joined_tbodies[1].select('tr')
                points_table_rows = stats_table_rows
            else:
                player_table_rows = joined_tbodies[0].select('tr')
                stats_table_rows = player_table_rows
                points_table_rows = player_table_rows

            for i in range(len(player_table_rows)):
                player_row = player_table_rows[i]
                stats_row = stats_table_rows[i]
                points_row = points_table_rows[i]

                name_holder = player_row.select_one('.player-column__athlete')
                name = clean_text(name_holder.select_one('span').text)
                team_holder = player_row.select_one('.playerinfo__playerteam')
                team = clean_symbol(team_holder.text)
                pos_holder = player_row.select_one('.playerinfo__playerpos')
                pos = get_primary_pos(pos_holder.text)
                img = player_row.select_one('img').attrs['src']
                opp_holder = player_row.select_one('.opp')
                opp = clean_symbol(opp_holder.text)
                injury_holder = player_row.select_one(
                    '.playerinfo__injurystatus'
                )
                injury = clean_symbol(
                    injury_holder.text
                ) if injury_holder else None

                # score, projections (football specific)
                prev_score = None
                proj = None
                if self.sport == 'football':
                    game_status = points_row.select_one('.game-status-inline') \
                        or points_row.select_one('.game-status')
                    proj_holder = game_status.find_next('div')
                    prev_score_holder = proj_holder.find_next('div')
                    proj = parse_float(proj_holder.text)
                    prev_score = parse_float(prev_score_holder.text)

                roster = parse_float(stats_row.select_one('.own').text, 0)
                roster_change = parse_float(
                    stats_row.select_one('.poc').text, 0
                )

                total_pts = None
                avg_pts = None
                table_entries = points_row.select('.table--cell')
                if len(table_entries) >= 3:
                    total_pts = parse_float(table_entries[-3].text, 0)
                    avg_pts = parse_float(table_entries[-2].text, 0)

                # fill data
                player_id = get_player_id(name, pos)
                if player_id in seen:
                    print('warning: duplicate player_id (%s)' % player_id)
                    continue
                seen.add(player_id)

                player_info.append({
                    'id': player_id,
                    'name': name,
                    'pos': pos,
                    'team': team,
                    'img': img,
                })

                player_stats.append({
                    'week': self.week,
                    'id': player_id,
                    'injury': injury,
                    'opp': opp,
                    'proj': proj,
                    'prev_score': prev_score,
                    'roster': roster,
                    'roster_change': roster_change,
                    'total_pts': total_pts,
                    'avg_pts': avg_pts,
                })

        # write player info
        path = self.path['player_info']
        self.insert_data(
            player_info,
            path,
            sort=lambda x: x['id'],
            key=lambda x: x['id'],
        )
        print('--> player info written to %s' % path)

        # write player stats
        path = self.path['player_stats']
        self.update_data(
            player_stats,
            path,
            sort=lambda x: (parse_int(x['week'], 0), x['id']),
            filter=lambda x: str(x['week']) != self.week,
        )
        print('--> player stats written to %s' % path)
