import numpy as np
import pandas as pd
import os
import reader
import processor
from tqdm import tqdm
import plotly
import plotly.express as px
from jinja2 import Template


def build_homepage():
    league_data = reader.config['leagues']

    league_links = [{
        'name': league_data[x]['name'],
        'link': 'reports/%s/current.html' % x
    } for x in league_data]

    with open('templates/home.html', 'r') as file:
        template_text = file.read()

    template = Template(template_text)

    html = template.render(
        league_links=league_links
    )

    with open('index.html', "w") as html_file:
        html_file.write(html)

    print('Homepage built at index.html')

        

class Builder:

    def __init__(self, league_id, week, n_sim=10000):

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

    
    def build_report(self):

        # print statistics
        print('===== %s =====' % self.league_name)
        print('Week %d' % self.week)

        df = self.proc.simulator.schedule_df
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

        data = [(t, points[t]/self.week, proj[t]) for t in teams]
        print(pd.DataFrame(data, columns=['Team', 'Avg', 'Proj']).round(1))
        print()


        # standings
        wins, points, proj = self.proc.simulator.fill_standings(self.week)
        data = [[t, wins[t], points[t]/self.week] for t in self.proc.teams]

        df = pd.DataFrame(data, columns=['Team', 'Wins', 'Avg'])
        df = df.sort_values(['Wins', 'Avg'], ascending=False).reset_index(drop=True)
        df['Avg'] = df['Avg'].round(1)
        df[''] = list(df.index + 1)
        df = df[['', 'Team', 'Wins', 'Avg']]

        standings_table = df


        # expected final standings
        efs = self.proc.expected_final_standings(self.week)
        df = pd.DataFrame(efs.items(), columns=['Team', 'EFS'])
        df = df.sort_values('EFS').reset_index(drop=True)
        df[''] = list(df.index + 1)
        df = df[['', 'Team']]
        expected_final_list = list(df['Team'])
        expected_final_list = ['%d. %s' % (i+1, x) for i, x in enumerate(expected_final_list)]


        # expected vs actual wins
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


        # expected sos
        current, future = self.proc.expected_sos(self.week)
        data = [(t, current[t], future[t]) for t in self.proc.teams]
        df = pd.DataFrame(data, columns=['Team', 'Current', 'Future'])
        df = df.sort_values(['Current', 'Future'], ascending=False).reset_index(drop=True)
        df['Current'] = df['Current'].round(1)
        df['Future'] = df['Future'].round(1)
        sos_table = df


        # upcoming game importance
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


        # playoff odds
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

        fig = px.bar(
            df,
            x='Odds', y='Team',
            orientation='h',
            text_auto=True,
            template='simple_white',
            labels={'Team': ''},
            color_discrete_sequence=[self.theme['blue']],
            height=350,
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 10})
        fig.update_xaxes(visible=False, showticklabels=False, fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        fig.update_layout(showlegend=False)
        fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_ticksuffix = '%')

        playoff_odds_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        # championship odds
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

        fig = px.bar(
            df,
            x='Odds', y='Team',
            orientation='h',
            text_auto=True,
            template='simple_white',
            labels={'Team': ''},
            color_discrete_sequence=[self.theme['green']],
            height=350,
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 10})
        fig.update_xaxes(visible=False, showticklabels=False, fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        fig.update_layout(showlegend=False)
        fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_ticksuffix = '%')

        championship_odds_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        # punishment odds
        odds = self.proc.punishment_odds(self.week)
        eliminated, clinched, limits = self.proc.playoff_eligibility
        for t in odds:
            if not limits[t]['max'] < len(self.proc.teams):
                odds[t] = max(odds[t], 0.001)

        df = pd.DataFrame(odds.items(), columns=['Team', 'Odds'])
        df['Odds'] = (df['Odds'] * 100).round(1)
        df = df.sort_values('Odds')

        fig = px.bar(
            df,
            x='Odds', y='Team',
            orientation='h',
            text_auto=True,
            template='simple_white',
            labels={'Team': ''},
            color_discrete_sequence=[self.theme['red']],
            height=350,
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 10})
        fig.update_xaxes(visible=False, showticklabels=False, fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        fig.update_layout(showlegend=False)
        fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_ticksuffix = '%')

        punishment_odds_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        # betting lines table
        playoff, champion = self.proc.sportsbook_odds(self.week)
        true_champion = self.proc.champion_odds(self.week)
        data = [(t, playoff[t], champion[t], true_champion[t]) for t in self.proc.teams]
        df = pd.DataFrame(data, columns=['Team', 'Make Playoffs', 'Win League', 'True'])
        df = df.sort_values('True', ascending=False).reset_index(drop=True)
        df = df[['Team', 'Make Playoffs', 'Win League']]
        betting_lines_table = df


        # playoff odds over time (with menu)
        data = [self.proc.playoff_odds(w) for w in range(1, self.week + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        fig = px.line(
            df,
            markers=True,
            template='simple_white',
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
            height=500
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 0, 'r': 20})
        fig.update_layout(yaxis_ticksuffix='%')
        fig.update_layout(legend={'orientation': 'h', 'y': -0.2, 'font': {'size': 14}, 'title': ''})
        fig.update_xaxes(range=[0.7, max(df.shape[0] + 0.3, 7)], fixedrange=True)
        fig.update_yaxes(range=[-5, df.values.max()+9], fixedrange=True)
        fig.update_layout(
            updatemenus=[{
                'buttons': [{
                    'label': '  %s  ' % col,
                    'method': 'update',
                    'args': [
                        {'visible': [True for c in df.columns]}
                        if col == 'All' else
                        {'visible': [True if c == col else False for c in df.columns]}
                    ]
                } for col in ['All'] + list(df.columns)
                ],
                'x': 0.5, 'y': 1.2, 
                'xanchor': 'center', 'yanchor': 'middle',
                'pad': {'l': 10, 'r': 10, 'b': 10, 't': 10},
                'font': {'size': 20}
            }]
        )

        playoff_time_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        # championship odds over time (with menu)
        data = [self.proc.champion_odds(w) for w in range(1, self.week + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        fig = px.line(
            df,
            markers=True,
            template='simple_white',
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
            height=500
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 0, 'r': 20})
        fig.update_layout(yaxis_ticksuffix='%')
        fig.update_layout(legend={'orientation': 'h', 'y': -0.2, 'font': {'size': 14}, 'title': ''})
        fig.update_xaxes(range=[0.7, max(df.shape[0] + 0.3, 7)], fixedrange=True)
        fig.update_yaxes(range=[-5, df.values.max()+9], fixedrange=True)
        fig.update_layout(
            updatemenus=[{
                'buttons': [{
                    'label': '  %s  ' % col,
                    'method': 'update',
                    'args': [
                        {'visible': [True for c in df.columns]}
                        if col == 'All' else
                        {'visible': [True if c == col else False for c in df.columns]}
                    ]
                } for col in ['All'] + list(df.columns)
                ],
                'x': 0.5, 'y': 1.2, 
                'xanchor': 'center', 'yanchor': 'middle',
                'pad': {'l': 10, 'r': 10, 'b': 10, 't': 10},
                'font': {'size': 20}
            }]
        )

        championship_time_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        # punishment odds over time (with menu)
        data = [self.proc.punishment_odds(w) for w in range(1, self.week + 1)]
        df = pd.DataFrame(data)

        df = df * 100
        df = df.round(1)
        df.index = df.index + 1

        fig = px.line(
            df,
            markers=True,
            template='simple_white',
            labels={'value': '', 'index': 'Week', 'variable': 'Team'},
            height=500
        )
        fig.update_layout(margin={'t': 10, 'b': 10, 'l': 0, 'r': 20})
        fig.update_layout(yaxis_ticksuffix='%')
        fig.update_layout(legend={'orientation': 'h', 'y': -0.2, 'font': {'size': 14}, 'title': ''})
        fig.update_xaxes(range=[0.7, max(df.shape[0] + 0.3, 7)], fixedrange=True)
        fig.update_yaxes(range=[-5, df.values.max()+9], fixedrange=True)
        fig.update_layout(
            updatemenus=[{
                'buttons': [{
                    'label': '  %s  ' % col,
                    'method': 'update',
                    'args': [
                        {'visible': [True for c in df.columns]}
                        if col == 'All' else
                        {'visible': [True if c == col else False for c in df.columns]}
                    ]
                } for col in ['All'] + list(df.columns)
                ],
                'x': 0.5, 'y': 1.2, 
                'xanchor': 'center', 'yanchor': 'middle',
                'pad': {'l': 10, 'r': 10, 'b': 10, 't': 10},
                'font': {'size': 20}
            }]
        )

        punishment_time_plot = plotly.offline.plot(
            fig, include_plotlyjs=False, output_type='div', 
            config= dict(displayModeBar = False)
        )


        with open('templates/report.html', 'r') as file:
            template_text = file.read()

        template = Template(template_text)

        html = template.render(
            week=self.week,
            league_name=self.league_name,
            standings_table=standings_table,
            expected_final_list=expected_final_list,
            expected_wins_table=expected_wins_table,
            sos_table=sos_table,
            upcoming_games_table=upcoming_games_table,
            betting_lines_table=betting_lines_table,
            playoff_odds_plot=playoff_odds_plot,
            championship_odds_plot=championship_odds_plot,
            punishment_odds_plot=punishment_odds_plot,
            playoff_time_plot=playoff_time_plot,
            championship_time_plot=championship_time_plot,
            punishment_time_plot=punishment_time_plot
        )

        outdir = 'reports/%s' % (self.league_id)
        outfile = 'reports/%s/current.html' % (self.league_id)
        os.makedirs(outdir, exist_ok=True) 
        with open(outfile, "w") as html_file:
            html_file.write(html)

        print('Page built at %s' % outfile)
        print('=====================================')

        