import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


confirmed_ = '../data/time_series_covid19_confirmed_global.csv'
deaths_ = '../data/time_series_covid19_deaths_global.csv'
recovered_ = '../data/time_series_covid19_recovered_global.csv'

df_confirmed = pd.read_csv(confirmed_)
df_deaths = pd.read_csv(deaths_)
df_recovered = pd.read_csv(recovered_)

countries_with_states = [el for el in df_confirmed['Country/Region'].unique()
                         if len(df_confirmed[df_confirmed['Country/Region'] == el]) > 1
                         ]


# Definitions:
# Data wrangling


def revampDataframe(df):
    '''Transpose, remove unnecessary columns, group countries with province/state into one entry'''
    new_df = pd.DataFrame()

    for el in df['Country/Region'].unique():
        if el not in countries_with_states:
            t = df[(df['Country/Region'] == el)].drop(columns=['Province/State',
                                                               'Country/Region',
                                                               'Lat',
                                                               'Long']).T
        elif el in countries_with_states:
            t = pd.DataFrame(df[df['Country/Region'] == el].
                             drop(columns=['Province/State',
                                           'Country/Region',
                                           'Lat',
                                           'Long']).sum().T)
        t.rename(columns={t.columns[0]: el}, inplace=True)
        new_df[el] = t[el]

    new_df['Total'] = new_df.sum(axis=1)
    return new_df


def newDaily(df):
    ''' Return df with difference of a DataFrame element with the element
        in the same column of the previous row'''
    return df.diff()


# New datasets
confirmed = revampDataframe(df_confirmed)
deaths = revampDataframe(df_deaths)
recovered = revampDataframe(df_recovered)

new_daily_confirmed = newDaily(confirmed)
new_daily_confirmed['Total overall'] = confirmed['Total']

new_daily_deaths = newDaily(deaths)
new_daily_deaths['Total overall'] = deaths['Total']


# More Definitions: Plotting
def generalOverview(c, r, d, col):
    '''Plot overlap of confirmed, recovered and deaths over time'''
    a = pd.DataFrame()

    a['confirmed'] = c[col]
    a['recovered'] = r[col]
    a['deaths'] = d[col]

    fig = go.Figure(data=[go.Bar(name='confirmed', x=a.index, y=a.confirmed),
                          go.Bar(name='recoverd', x=a.index,
                                 y=a.recovered, marker_color='green'),
                          go.Bar(name='deaths', x=a.index, y=a.deaths, marker_color='red')])
    fig.update_layout(barmode='overlay',
                      title_text='Overview over time: ' + col,
                      autosize=False,
                      height=800,
                      )
    # fig.show()

    return fig


def plotCountriesCurrentState(c, r, d):
    ''' Plot current state of 50 countries with most confirmed cases '''
    a = pd.DataFrame()
    date = c.tail(1).index[0]
    c_ = c.drop(columns='Total').tail(1).T
    c_.rename(columns={c_.columns[0]: 'confirmed'}, inplace=True)
    r_ = r.drop(columns='Total').tail(1).T
    r_.rename(columns={r_.columns[0]: 'recovered'}, inplace=True)
    d_ = d.drop(columns='Total').tail(1).T
    d_.rename(columns={d_.columns[0]: 'deaths'}, inplace=True)

    a['confirmed'] = c_['confirmed']
    a['recovered'] = r_['recovered']
    a['deaths'] = d_['deaths']

    a.sort_values(by='confirmed', ascending=False, inplace=True)
    a = a.head(50)

    fig = go.Figure(data=[go.Bar(name='Total confirmed',
                                 y=a.index,
                                 x=a.confirmed,
                                 orientation='h'),
                          go.Bar(name='Total recoverd',
                                 y=a.index,
                                 x=a.recovered,
                                 orientation='h',
                                 marker_color='green'),
                          go.Bar(name='Total deaths',
                                 y=a.index,
                                 x=a.deaths,
                                 orientation='h',
                                 marker_color='red')])
    fig.update_layout(barmode='overlay',
                      title_text='Countries with most confirmed cases ' + date,
                      autosize=False,
                      width=1800,
                      height=1000,
                      )

    return fig


def plotDaysToDouble(c, col):

    def daysToDouble(a):
        days_to_double = pd.DataFrame()
        dtb = []
        date = []
        value = []
        ini = a.iloc[0] * 2
        counter = 0
        for i in range(len(a)):
            if a.iloc[i] >= ini:
                dtb.append(i - counter)
                value.append(a.iloc[i])
                date.append(a.index[i])
                ini = a[i] * 2
                counter = i
        days_to_double['Num_of_days'] = dtb
        days_to_double['value'] = value
        days_to_double['date'] = date
        return days_to_double

    d = daysToDouble(c[col])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d.date,
                             y=d.Num_of_days,
                             hovertemplate='<i>Date</i>: %{x}<br>' +
                             '<b>Confirmed cases:</b> %{customdata}<br>' +
                             '<b>Days to double:</b> %{y}' +
                             "<extra></extra>",
                             customdata=d.value,
                             line=dict(color='orange')),
                  )
    fig.update_layout(title_text='Days for confirmed cases to double: ' + col)

    return fig


def plotGrowthRate(c, d, col):
    ''' growth rate = ((present/past) ** 1/n ) - 1
    We're plotting day to day, so n = 1
    '''
    def calculateGrowthRate(df):
        present_past = df / df.shift(fill_value=0)
        growth_rate = (present_past - 1) * 100
        return growth_rate

    confirmed_gr = calculateGrowthRate(c)
    death_gr = calculateGrowthRate(d)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=confirmed_gr.index,
                             y=confirmed_gr[col],
                             mode='lines',
                             name='confirmed',
                             line=dict(color='green')))
    fig.add_trace(go.Scatter(x=death_gr.index, y=death_gr[col],
                             mode='lines',
                             name='deaths',
                             line=dict(color='red')))
    fig.update_layout(
        title_text='Growth rate (in %) - time interval 1 day: ' + col)

    return fig


# Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H1(children='Covid-19'),

    dcc.Graph(id='top50',
              figure=plotCountriesCurrentState(confirmed, recovered, deaths)),

    html.Div(children='Choose a country'),

    html.Div([html.Div([dcc.Dropdown(id='country',
                                     options=[{'label': i, 'value': i}
                                              for i in confirmed.columns],
                                     value='Total')])]),

    dcc.Graph(id='countries_overlay'),

    dcc.Graph(id='days_to_double'),

    dcc.Graph(id='countries_growth_rate'
              )
])


@app.callback(Output('countries_overlay', 'figure'),
              [Input('country', 'value')])
def update_country_graph(country):
    f = generalOverview(confirmed, recovered, deaths, country)
    return f


@app.callback(Output('days_to_double', 'figure'),
              [Input('country', 'value')])
def update_days_to_double_graph(country):
    g = plotDaysToDouble(confirmed, country)
    return g


@app.callback(Output('countries_growth_rate', 'figure'),
              [Input('country', 'value')])
def update_growth_rate_graph(country):
    h = plotGrowthRate(confirmed, deaths, country)
    return h


if __name__ == '__main__':
    app.run_server(debug=True)
