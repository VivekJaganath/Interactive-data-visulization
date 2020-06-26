import pandas as pd
import plotly.express as px

import json
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IDV Mini-Project-COVID"


#json_file = "europe_geo.json"

with open('europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

df_world = pd.read_csv("owid-covid-data.csv")
search_df_europe = df_world['continent'] == 'Europe'
df_europe = df_world[search_df_europe]
df_europe = df_europe.rename({'location': 'country'}, axis=1)
df_europe_cases = df_europe.groupby(['date', 'country'])['total_cases', 'total_deaths'].max()
df_europe_cases = df_europe_cases.reset_index()
df_europe_cases['date'] = pd.to_datetime(df_europe_cases['date'])
df_europe_cases['date'] = df_europe_cases['date'].dt.strftime('%B %d, %Y')
#print(df_europe_cases)

df_recovered = pd.read_csv("time_series_covid19_recovered_global.csv")
del df_recovered['Province/State']
del df_recovered['Lat']
del df_recovered['Long']
df_recovered = df_recovered.rename({'Country/Region': 'country'}, axis=1)
df_recovered = df_recovered.groupby(['country']).sum()
df_recovered = df_recovered.reset_index()
df_recovered = pd.melt(df_recovered, id_vars=["country"], var_name="date", value_name="total_recovery")
df_recovered['total_recovery'] = df_recovered['total_recovery'].astype(float)
df_recovered['date'] = pd.to_datetime(df_recovered['date'])
df_recovered['date'] = df_recovered['date'].dt.strftime('%B %d, %Y')

df_merged = pd.merge(df_europe_cases, df_recovered, on=['country', 'date'])


colors = {
    'background': '#F0FFFF',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.H1("IDV Mini-Project COVID-19",
            style = {
                'textAlign' : 'center',
                'color' : colors['text']
            }),
    html.Div([dcc.Graph(id='the_graph'),
              html.Label(['Choose cases:'], style={'font-weight': 'bold', "text-align": "left"}),
              dcc.Dropdown(id='cases',
                           options=[{'label': 'Confirmed', 'value': 'C'}, {'label': 'Death', 'value': 'D'},
                                    {'label': 'Recovered', 'value': 'R'}],
                           value='C', clearable=True, searchable=True,
                           placeholder='Choose Cases...', style={'height': '30px', 'width': '200px'})],
             className='six columns'),
    html.Div([dcc.Graph(id='line_graph'),
              html.Label(['Choose country:'], style={'font-weight': 'bold', "text-align": "left"}),
              dcc.Dropdown(id='country',
                           options=[{'label': x, 'value': x} for x in df_europe_cases.sort_values('country')
                           ['country'].unique()], value='Albania', clearable=True, searchable=True,
                           placeholder='Choose Country...', style={'height': '30px', 'width': '200px'},)
              ], className='five columns')
    ])
#----------------


@app.callback(
    Output('line_graph', 'figure'),
    [Input('country', 'value')])

def build_graph(country_input):
    df_per_country = df_merged[(df_merged['country'] == country_input)]
    df_per_country = df_per_country.rename({'total_cases': 'total_cases_'+country_input,
                                            'total_deaths': 'total_deaths_'+country_input,
                                            'total_recovery': 'total_recovery_'+country_input}, axis=1)
    df_germany = df_merged[(df_merged['country'] == "Germany")]
    df_germany = df_germany.rename({'total_cases': 'total_cases_Germany', 'total_deaths': 'total_deaths_Germany',
                                    'total_recovery': 'total_recovery_Germany'},  axis=1)
    df_merge = pd.merge(df_germany, df_per_country, on='date')
    #print(df_merge.to_string())
    df_merge = pd.DataFrame(df_merge)
    fig = px.line(df_merge, x='date', y=["total_cases_Germany", "total_deaths_Germany", "total_recovery_Germany",
                                         "total_cases_"+country_input, "total_deaths_"+country_input,
                                         "total_recovery_"+country_input],
                  height=720, width=980, title='Comparing COVID cases of '+country_input+' against Germany',
                  template='plotly_dark')
    fig.update_layout(title=dict(font=dict(size=20)))
    return fig


@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input('cases', 'value')])

def build_map(case):
    if case == 'R':
        case_chosen = 'total_recovery'
    elif case == 'D':
        case_chosen = 'total_deaths'
    else:
        case_chosen = 'total_cases'

    fig_map = px.choropleth(data_frame=df_merged, geojson=europe_geo_json, locations='country',
                            scope="europe", color=case_chosen, hover_name='country', featureidkey='properties.name',
                            projection="natural earth", color_continuous_scale=px.colors.sequential.Rainbow,
                            title='Total COVID-19 Cases Across Europe', width=1050, height=720, template='plotly_dark')

    fig_map.update_layout(title=dict(font=dict(size=20)))
    return fig_map


if __name__ == '__main__':
    app.run_server(debug=False)

