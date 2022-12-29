import plotly
import plotly.express as px

def bar_plot(df, x, y, color, labels={}, percentage=True):
    fig = px.bar(
        df,
        x=x, y=y,
        orientation='h',
        text_auto=True,
        template='simple_white',
        labels=labels,
        color_discrete_sequence=[color],
        height=350,
    )
    fig.update_layout(margin={'t': 10, 'b': 10, 'l': 10})
    fig.update_xaxes(visible=False, showticklabels=False, fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    fig.update_layout(showlegend=False)
    fig.update_traces(textfont_size=13, textangle=0, textposition="outside", cliponaxis=False)
    if percentage:
        fig.update_layout(xaxis_ticksuffix = '%')

    plt = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type='div', 
        config= dict(displayModeBar = False)
    )
    return plt


def odds_over_time_plot(df, labels={}):
    fig = px.line(
        df,
        markers=True,
        template='simple_white',
        labels=labels,
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

    plt = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type='div', 
        config= dict(displayModeBar = False)
    )
    return plt

