import pandas as pd
import plotly.express as px

import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

df = pd.read_csv("owid-covid-data.csv")
search_df_europe = df['continent'] == 'Europe'
df_europe = df[search_df_europe]
formatted_df_europe = df_europe.groupby(['date', 'location', 'iso_code'])['total_cases', 'total_deaths'].max()
formatted_df_europe = formatted_df_europe.reset_index()
print(formatted_df_europe)
with open('europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

#----------------
app.layout = html.Div([
    html.Div(dcc.Graph(id='the_graph'), className='six columns'),
    html.Div([html.Br(), html.Label(['Choose country:'], style={'font-weight': 'bold', "text-align": "left"}),
              dcc.Dropdown(id='country',
                           options=[{'label': x, 'value': x} for x in formatted_df_europe.sort_values('location')
                           ['location'].unique()], value='Austria', multi=False, disabled=False, clearable=True,
                           searchable=True, placeholder='Choose Country...', className='form-dropdown',
                           style={'width': "80%"}, persistence='string', persistence_type='memory'),
              dcc.Graph(id='line_graph'),
              ],
             className='two columns'),
    ])
#----------------


@app.callback(
    Output('line_graph', 'figure'),
    [Input('country', 'value')])

def build_graph(country_input):
    df_per_country = formatted_df_europe[(formatted_df_europe['location'] == country_input)]
    fig = px.line(df_per_country, x="date", y=["total_cases", "total_deaths"], height=600, width=1000)
    return fig


@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input('country', 'value')])

def build_map(some_input):
    fig_map = px.choropleth(data_frame=formatted_df_europe, geojson=europe_geo_json, locations='location',
                            scope="europe", color="total_cases", hover_name='location', featureidkey='properties.name',
                            projection="natural earth", color_continuous_scale=px.colors.sequential.Plasma,
                            title='Total COVID-19 Cases Across Europe',
                            width=1000, height=700)

    fig_map.update_layout(title=dict(font=dict(size=20)))
    return fig_map


if __name__ == '__main__':
    app.run_server(debug=False)

