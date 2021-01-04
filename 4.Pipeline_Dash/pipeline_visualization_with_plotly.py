import pandas as pd
import plotly.graph_objects as go


# VARIABLES ######################################################################################

global all_grouped_df
all_grouped_df = {}

confirmed_ = '../data/time_series_covid19_confirmed_global.csv'
deaths_ = '../data/time_series_covid19_deaths_global.csv'
recovered_ = '../data/time_series_covid19_recovered_global.csv'


# DEFINITIONS ######################################################################################

def import_df(file):
    df = pd.read_csv(file)
    return df


def group_by_country(df):
    df_grouped = df.drop(columns=['Lat', 'Long']).groupby(by=['Country/Region']).sum()
    return df_grouped


def group_by_current_date(df_grouped):
    global date
    current_date = pd.DataFrame(df_grouped[date])
    return current_date


def sort_top_50(current_date):
    top50 = current_date.sort_values(by=date, ascending=False).head(50)
    return top50


def make_go_bar_for_top50(top50, bar_name, color):
    global date
    bar = go.Bar(name=bar_name,
                 x=top50[date],
                 y=top50.index,
                 marker_color=color,
                 orientation='h')
    return bar


def pipeline_to_make_bar_for_top50(file, bar_name, color):
    global all_grouped_df

    df = import_df(file)
    all_grouped_df[file] = group_by_country(df)

    current_date = group_by_current_date(all_grouped_df[file])
    top50 = sort_top_50(current_date)
    bar = make_go_bar_for_top50(top50, bar_name, color)
    return bar


def plot_most_confirmed_cases(files, bar_names, colors, d):
    global date
    date = d
    bars = []
    for file, bar_name, color in zip(files, bar_names, colors):
        bars.append(pipeline_to_make_bar_for_top50(file=file,
                                                   bar_name=bar_name,
                                                   color=color))
    fig = go.Figure(data=bars)
    fig.update_layout(barmode='overlay',
                      autosize=False,
                      width=1800,
                      height=1000,
                      title_text='Countries with most confirmed cases {d}'.format(d=date))
    return fig


def make_go_bar_for_country(df_grouped, bar_name, color, country):
    bar = go.Bar(name=bar_name,
                 x=df_grouped.index,
                 y=df_grouped[country],
                 marker_color=color)
    return bar


def plot_country(files, bar_names, colors, country):
    global all_grouped_df

    bars = []
    for file, bar_name, color in zip(files, bar_names, colors):
        country_df = pd.DataFrame(all_grouped_df[file].loc[country])
        print(country_df)
        bars.append(make_go_bar_for_country(country_df, bar_name, color, country))

    fig = go.Figure(data=bars)

    fig.update_layout(barmode='overlay',
                      autosize=False,
                      width=1800,
                      height=1000,
                      title_text='Overview over time')

    return fig


def main():

    fig = plot_most_confirmed_cases(files=[confirmed_, recovered_, deaths_],
                                    bar_names=['confirmed', 'recovered', 'deaths'],
                                    colors=['blue', 'green', 'red'],
                                    d='11/25/20')
    fig.show()

    fig2 = plot_country(files=[confirmed_, recovered_, deaths_],
                        bar_names=['confirmed', 'recovered', 'deaths'],
                        colors=['blue', 'green', 'red'],
                        country='Germany')
    fig2.show()

    return


# if __name__ == '__main__':

main()
