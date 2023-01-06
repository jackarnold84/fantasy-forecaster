import numpy as np
import pandas as pd
import os
import reader
import processor
from jinja2 import Template
import build.utils as utils


def build_homepage():

    # leauges
    league_data = reader.config['leagues']
    league_links = [{
        'name': league_data[x]['name'],
        'link': 'reports/%s/current.html' % x
    } for x in league_data]

    # player ratings
    years = os.listdir('reports/players')
    player_rating_links = [{
        'name': '%s Ratings' % y,
        'link': 'reports/players/%s/ratings.html' % y
    } for y in years]

    with open('templates/home.html', 'r') as file:
        template_text = file.read()
    template = Template(template_text)

    html = template.render(
        league_links=league_links,
        player_rating_links=player_rating_links,
    )

    with open('index.html', "w") as html_file:
        html_file.write(html)
    print('Homepage built at index.html')

        

class Builder:

    def __init__(self, league_id, week, n_sim=10000):

        print('========= %s =========' % league_id)
        print('Week %d' % week)
        self.proc = processor.Processor(league_id, week, n_sim=n_sim)
        self.league_id = league_id
        self.league_name = self.proc.simulator.league_name
        self.week = week
        self.theme = {
            'blue': '#1F77B4',
            'orange': '#FF7F0E',
            'green': '#2CA02C',
            'red': '#D62728',
            'purple': '#9467BD',
            'brown': '#8C564B',
            'pink': '#E377C2',
            'grey': '#7F7F7F',
            'yellow': '#BCBD22',
            'cyan': '#17BECF'
        }


    def print_league_statistics(self):
        print('\nLeague Stats:')
        df = self.proc.simulator.schedule_df
        df = df[df['type'] == 'Regular Season']
        df = df[df['week'] <= self.week]
        scores = np.array(list(df['away_score']) + list(df['home_score']))
        teams = self.proc.teams
        team_scores = []
        for t in teams:
            x1 = df[df['away_team'] == t]['away_score']
            x2 = df[df['home_team'] == t]['home_score']
            team_scores.append(list(x1) + list(x2))

        overall_mean = np.mean(scores)
        overall_std = np.std(scores)
        team_std = np.std(np.mean(team_scores, axis=1))

        wins, points, proj = self.proc.simulator.fill_standings(self.week)
        data = [
            ['Mean', self.proc.simulator.MEAN, overall_mean],
            ['Std', self.proc.simulator.STD, overall_std],
            ['Team Std', self.proc.simulator.T_STD, team_std]
        ]
        
        print(pd.DataFrame(data, columns=['', 'Used', 'Actual']).round(1))
        print()

        data = [(t, points[t]/df['week'].max(), proj[t]) for t in teams]
        print(pd.DataFrame(data, columns=['Team', 'Avg', 'Proj']).round(1))
        print()

    
    # plot and table generators

    def get_standings_table(self):
        df = self.proc.simulator.schedule_df
        df = df[df['type'] == 'Regular Season']
        df = df[df['week'] <= self.week]
        wins, points, proj = self.proc.simulator.fill_standings(self.week)
        data = [[t, wins[t], points[t]/df['week'].max()] for t in self.proc.teams]

        df = pd.DataFrame(data, columns=['Team', 'Wins', 'Avg'])
        df = df.sort_values(['Wins', 'Avg'], ascending=False).reset_index(drop=True)
        df['Avg'] = df['Avg'].round(1)
        df[''] = list(df.index + 1)
        df = df[['', 'Team', 'Wins', 'Avg']]

        standings_table = df
        return standings_table

    def get_expected_final_standings(self):
        efs = self.proc.expected_final_standings(self.week)
        df = pd.DataFrame(efs.items(), columns=['Team', 'EFS'])
        df = df.sort_values('EFS').reset_index(drop=True)
        df[''] = list(df.index + 1)
        df = df[['', 'Team']]
        expected_final_list = list(df['Team'])
        expected_final_list = ['%d. %s' % (i+1, x) for i, x in enumerate(expected_final_list)]
        return expected_final_list

    def get_expected_wins_table(self):
        wins, points, proj = self.proc.simulator.fill_standings(self.week)
        expected = self.proc.expected_wins(self.week)
        actual = wins
        data = [(t, expected[t], actual[t]) for t in self.proc.teams]
        df = pd.DataFrame(data, columns=['Team', 'Expected', 'Actual'])
        df['Difference'] = df['Actual'] - df['Expected']
        df = df.sort_values(['Expected', 'Actual'], ascending=False).reset_index(drop=True)
        df['Expected'] = df['Expected'].round(1)
        df['Difference'] = df['Difference'].round(1)
        df['Difference'] = ['+%.1f' % x if x > 0 else str(x) for x in df['Difference']]
        expected_wins_table = df
        return expected_wins_table

    def get_expected_sos(self):
        current, future = self.proc.expected_sos(self.week)
        data = [(t, current[t], future[t]) for t in self.proc.teams]
        df = pd.DataFrame(data, columns=['Team', 'Current', 'Future'])
        df = df.sort_values(['Current', 'Future'], ascending=False).reset_index(drop=True)
        df['Current'] = df['Current'].round(1)
        df['Future'] = df['Future'].round(1)
        sos_table = df
        return sos_table

    def get_upcoming_game_importance(self):
        if self.proc.game_importance:
            games = self.proc.game_importance

            data = [[
                '%s vs %s' % (x['away_team'], x['home_team']),
                x['importance']
            ] for x in games]
            df = pd.DataFrame(data, columns=['Week %d' % (self.week+1), 'Importance'])

            df = df.sort_values('Importance', ascending=False).reset_index(drop=True)
            df['Importance'] = [min(x * 100, 99) for x in df['Importance']]
            df['Importance'] = ['%d' % x for x in df['Importance']]
            upcoming_games_table = df
        else:
            upcoming_games_table = None
        return upcoming_games_table

    def get_playoff_odds_plot(self):
        odds = self.proc.playoff_odds(self.week)
        eliminated, clinched, limits = self.proc.playoff_eligibility
        for t in odds:
            if not eliminated[t]:
                odds[t] = max(odds[t], 0.001)
            if not clinched[t]:
                odds[t] = min(odds[t], 0.999)

        df = pd.DataFrame(odds.items(), columns=['Team', 'Odds'])
        df['Odds'] = (df['Odds'] * 100).round(1)
        df = df.sort_values('Odds')

        playoff_odds_plot = utils.bar_plot(
            df,
            x='Odds', y='Team',
            color=self.theme['blue'],
            labels={'Team': ''},
        )
        return playoff_odds_plot

    def get_division_odds_plot(self):
        odds = self.proc.division_odds(self.week)

        df = pd.DataFrame(odds.items(), columns=['Team', 'Odds'])
        df['Odds'] = (df['Odds'] * 100).round(1)
        df = df.sort_values('Odds')

        division_odds_plot = utils.bar_plot(
            df,
            x='Odds', y='Team',
            color=self.theme['purple'],
            labels={'Team': ''},
        )
        return division_odds_plot

    def get_championship_odds_plot(self):
        odds = self.proc.champion_odds(self.week)
        eliminated, clinched, limits = self.proc.playoff_eligibility
        for t in odds:
            if not eliminated[t]:
                odds[t] = max(odds[t], 0.001)
            if not clinched[t]:
                odds[t] = min(odds[t], 0.999)

        df = pd.DataFrame(odds.items(), columns=['Team', 'Odds'])
        df = df.sort_values('Odds')
        df['Odds'] = (df['Odds'] * 100).round(1)

        championship_odds_plot = utils.bar_plot(
            df,
            x='Odds', y='Team',
            color=self.theme['green'],
            labels={'Team': ''},
        )
        return championship_odds_plot

    def get_punishment_odds_plot(self):
        odds = self.proc.punishment_odds(self.week)
        eliminated, clinched, limits = self.proc.playoff_eligibility
        for t in odds:
            if not limits[t]['max'] < len(self.proc.teams):
                odds[t] = max(odds[t], 0.001)

        df = pd.DataFrame(odds.items(), columns=['Team', 'Odds'])
        df['Odds'] = (df['Odds'] * 100).round(1)
        df = df.sort_values('Odds')

        punishment_odds_plot = utils.bar_plot(
            df,
            x='Odds', y='Team',
            color=self.theme['red'],
            labels={'Team': ''},
        )
        return punishment_odds_plot

    def get_betting_lines_table(self):
        playoff, champion = self.proc.sportsbook_odds(self.week)
        true_champion = self.proc.champion_odds(self.week)
        data = [(t, playoff[t], champion[t], true_champion[t]) for t in self.proc.teams]
        df = pd.DataFrame(data, columns=['Team', 'Make Playoffs', 'Win League', 'True'])
        df = df.sort_values('True', ascending=False).reset_index(drop=True)
        df = df[['Team', 'Make Playoffs', 'Win League']]
        betting_lines_table = df
        return betting_lines_table

    def get_playoff_over_time_plot(self):
        max_week = int(self.proc.simulator.schedule_df['week'].max())
        data = [self.proc.playoff_odds(w) for w in range(1, min(self.week, max_week) + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        playoff_time_plot = utils.odds_over_time_plot(
            df,
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
        )
        return playoff_time_plot

    def get_championshipt_over_time_plot(self):
        data = [self.proc.champion_odds(w) for w in range(1, self.week + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        championship_time_plot = utils.odds_over_time_plot(
            df,
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
        )
        return championship_time_plot

    def get_punishment_over_time_plot(self):
        data = [self.proc.punishment_odds(w) for w in range(1, self.week + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        punishment_time_plot = utils.odds_over_time_plot(
            df,
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
        )
        return punishment_time_plot

    
    def build_report(self):

        # print statistics
        self.print_league_statistics()

        # report types
        use_divisions = self.proc.simulator.use_divisions
        playoff_report = self.proc.simulator.playoff_report
        if playoff_report:
            print('Building in playoff report mode')

        # get plots and tables
        standings_table = self.get_standings_table()
        expected_final_list = self.get_expected_final_standings()
        expected_wins_table = self.get_expected_wins_table()
        sos_table = self.get_expected_sos()
        upcoming_games_table = self.get_upcoming_game_importance()
        playoff_odds_plot = self.get_playoff_odds_plot()
        division_odds_plot = self.get_division_odds_plot()
        championship_odds_plot = self.get_championship_odds_plot()
        punishment_odds_plot = self.get_punishment_odds_plot()
        betting_lines_table = self.get_betting_lines_table()
        playoff_time_plot = self.get_playoff_over_time_plot()
        championship_time_plot = self.get_championshipt_over_time_plot()
        punishment_time_plot = self.get_punishment_over_time_plot()

        # build using template
        with open('templates/metrics-report.html', 'r') as file:
            template_text = file.read()
        template = Template(template_text)

        html = template.render(
            week=self.week,
            league_name=self.league_name,
            use_divisions=use_divisions,
            standings_table=standings_table,
            expected_final_list=expected_final_list,
            expected_wins_table=expected_wins_table,
            sos_table=sos_table,
            upcoming_games_table=upcoming_games_table,
            betting_lines_table=betting_lines_table,
            playoff_odds_plot=playoff_odds_plot,
            division_odds_plot=division_odds_plot,
            championship_odds_plot=championship_odds_plot,
            punishment_odds_plot=punishment_odds_plot,
            playoff_time_plot=playoff_time_plot,
            championship_time_plot=championship_time_plot,
            punishment_time_plot=punishment_time_plot,
            playoff_report=playoff_report
        )

        # write to file
        outdir = 'reports/%s' % (self.league_id)
        outfile = 'reports/%s/current.html' % (self.league_id)
        data_outfile = 'reports/%s/schedule.csv' % (self.league_id)
        os.makedirs(outdir, exist_ok=True)

        self.proc.simulator.schedule_df.to_csv(data_outfile, index=False)
        with open(outfile, "w") as html_file:
            html_file.write(html)

        print('Page built at %s\n' % outfile)
