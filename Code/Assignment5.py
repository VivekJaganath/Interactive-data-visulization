import pandas as pd
import plotly.express as px

import json
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

govern_measures_data_file = "datasets/acaps_covid19_government_measures_dataset_0.xlsx"

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IDV Mini-Project-COVID"


def prepare_data_government_measures(filename):

    gm_df = pd.read_excel(filename, sheet_name="Database")
    european_gn_df = gm_df[gm_df['REGION'] == "Europe"]
    filtered_european_gn_df = european_gn_df.filter(
        ["COUNTRY", "ISO", "REGION", "CATEGORY", "MEASURE", "COMMENTS", "DATE_IMPLEMENTED", "LINK",  "SOURCE", "SOURCE_TYPE"])
    # data_table_visualization = european_gn_df.filter(["COUNTRY", "ISO", "REGION", "CATEGORY", "MEASURE", "COMMENTS", "DATE_IMPLEMENTED", "LINK",  "SOURCE", "SOURCE_TYPE"]
    # print(filtered_european_gn_df.shape)
    # print(filtered_european_gn_df.head())
    # print(filtered_european_gn_df.dtypes)

    return (filtered_european_gn_df)

#json_file = "europe_geo.json"


with open('europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

df_world = pd.read_csv("owid-covid-data.csv")
search_df_europe = df_world['continent'] == 'Europe'
df_europe = df_world[search_df_europe]
df_europe = df_europe.rename({'location': 'country'}, axis=1)
df_europe_cases = df_europe.groupby(['date', 'country'])[
    'total_cases', 'total_deaths'].max()
df_europe_cases = df_europe_cases.reset_index()
df_europe_cases['date'] = pd.to_datetime(df_europe_cases['date'])
df_europe_cases['date'] = df_europe_cases['date'].dt.strftime('%B %d, %Y')
# print(df_europe_cases)

df_recovered = pd.read_csv("time_series_covid19_recovered_global.csv")
del df_recovered['Province/State']
del df_recovered['Lat']
del df_recovered['Long']
df_recovered = df_recovered.rename({'Country/Region': 'country'}, axis=1)
df_recovered = df_recovered.groupby(['country']).sum()
df_recovered = df_recovered.reset_index()
df_recovered = pd.melt(df_recovered, id_vars=[
                       "country"], var_name="date", value_name="total_recovery")
df_recovered['total_recovery'] = df_recovered['total_recovery'].astype(float)
df_recovered['date'] = pd.to_datetime(df_recovered['date'])
df_recovered['date'] = df_recovered['date'].dt.strftime('%B %d, %Y')

df_merged = pd.merge(df_europe_cases, df_recovered, on=['country', 'date'])

euro_government_measureDF = prepare_data_government_measures(
    govern_measures_data_file)
data_table_visulaization_df = euro_government_measureDF.filter(
    ["COUNTRY", "CATEGORY", "MEASURE", "DATE_IMPLEMENTED", "COMMENTS"])

xl = pd.read_csv('datasets/Dataset1.csv')
xl['date'] = pd.to_datetime(DataSet1['date'])
xl['date'] = DataSet1['date'].dt.strftime('%B %d, %Y')

app.layout = html.Div(
    children=[
        html.H6("IDV Mini-Project COVID-19", style={'textAlign': 'center'}),
        html.P('In the month of January 2020, most of the European countries were affected with COVID-19. '
                                         'As there was not much information about COVID-19, for example how it was transmitted, '
                                         'what measures needed to be taken to stop it‘s spread etc., it was very hard for the European governments '
                                         'to formalise an approach to prevent the spread of COVID-19. In such a situation the German government'
                                         'came up with many measures to counter COVID-19. In this project, we are'
                                         'comparing the response of Germany with its European counterparts in aspects'
                                         'such as closure of schools, home quarantine, tests etc through visualisation.',
               style={'textAlign': 'center'}),
        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2("ADD title for first graph visulization here"),
                                  html.P("Add description for first graph visulization here"),
                                  html.Div(className='div-for-dropdown',
                                           children=[

                                               html.Label(['Choose cases - add some more description HERE:'],
                                                          style={'font-weight': 'bold', "text-align": "left"}),

                                               dcc.Dropdown(id='cases',
                                                            options=[{'label': 'Confirmed', 'value': 'C'},
                                                                     {'label': 'Death', 'value': 'D'},
                                                                     {'label': 'Recovered', 'value': 'R'}],
                                                            value='C', clearable=True, searchable=True,
                                                            style={'backgroundColor': '#1E1E1E'}
                                                            )
                                           ])

                              ]),

                     html.Div(className='eight columns div-for-charts bg-grey',
                              children=[
                                  html.Div(
                                      children = [
                                          dcc.Graph(id='the_graph', config={'displayModeBar': False},
                                                    animate=True,  style={'height': '620px'})])
                              ])
                 ]),

        html.Div(className='row',
                 children=[
                     html.Div(className='four columns div-user-controls',
                              children=[
                                  html.H2("ADD title for Second graph visulization here"),
                                  html.P("Add description for Second graph visulization here"),
                                  html.Div(className='div-for-dropdown',
                                           children=[
                                               html.Div(
                                                   children= [
                                                       html.Label(['Choose country:'],
                                                                  style={'font-weight': 'bold', "text-align": "left"}),
                                                       dcc.Dropdown(id='country',
                                                            options=[{'label': x, 'value': x} for x in
                                                                     df_europe_cases.sort_values('country')
                                                                     ['country'].unique()], value='Albania',
                                                            clearable=True, searchable=True,
                                                            style={'backgroundColor': '#1E1E1E'}
                                                            )
                                                   ]),
                                               html.Div(
                                                   children=[
                                                       html.Label(['Choose Measure:'],
                                                          style={'font-weight': 'bold', "text-align": "left"}),
                                                       dcc.Dropdown(id = 'measure',
                                                            options = [{'label': x, 'value': x} for x in DataSet1.sort_values('GovtRestriction')
															['GovtRestriction'].unique()],
															value='School closing',
                                                            clearable = True, searchable=True,
                                                            style = {'backgroundColor': '#1E1E1E'}
                                                            )
                                                   ])
                                           ])
                              ]),
                     html.Div(className='eight columns div-for-charts',
                              children=[
                                  html.Div(
                                      children=[
                                          dcc.Graph(id='scatter_plot', config={'displayModeBar': False},
                                                    animate=True,  style={'height': '620px'})
                                      ])
                              ])
                 ]),

        html.Div(className='row',
                 children=[
                     html.Div(
                              children=[
                                  html.Label(['Add a suitable title HERE for german table:'], style={'font-weight': 'bold', "text-align": "left"}),
                                  dash_table.DataTable(
                                      id='data_table_german',
                                      columns=[{"name": i, "id": i}for i in data_table_visulaization_df.columns],
                                      # data=data_table_visulaization_df.to_dict('records'),
                                      page_size=20,
                                      style_header={
                                          'backgroundColor': 'rgb(230, 230, 230)',
                                          'fontWeight': 'bold'},
                                      style_data_conditional=[{
                                          'if': {'row_index': 'odd'},
                                          'backgroundColor': 'rgb(248, 248, 248)'}],
                                      style_data={
                                          'whiteSpace': 'normal',
                                          'height': 'auto',
                                          'lineHeight': '15px'},
                                      style_cell={
                                          'minWidth': '30px', 'width': '50px', 'maxWidth': '240px',
                                          'textAlign': 'left',
                                          'whiteSpace': 'normal',
                                          'height': 'auto'},
                                      fixed_rows={'headers': True},
                                      css=[{
                                          'selector': '.dash-spreadsheet td div',
                                          'rule': '''
                                          line-height: 15px;
                                          max-height: 30px; min-height: 30px; height: 30px;
                                          display: block;
                                          overflow-y: hidden;'''}],
                                      tooltip_duration=None
                                  )], className='six columns'),
                     html.Div(
                              children=[
                                  html.Label(['Add a suitable title HERE for other table:'], style={'font-weight': 'bold', "text-align": "left"}),
                                  dash_table.DataTable(
                                      id='data_table',
                                      columns=[{"name": i, "id": i} for i in data_table_visulaization_df.columns],
                                                      # data=data_table_visulaization_df.to_dict('records'),
                                      page_size=20,
                                      style_header={
                                          'backgroundColor': 'rgb(230, 230, 230)',
                                          'fontWeight': 'bold'},
                                      style_data_conditional=[{
                                          'if': {'row_index': 'odd'},
                                          'backgroundColor': 'rgb(248, 248, 248)'}],
                                      style_data={
                                          'whiteSpace': 'normal',
                                          'height': 'auto',
                                          'lineHeight': '15px'},
                                      style_cell={
                                          'minWidth': '30px', 'width': '50px', 'maxWidth': '240px',
                                          'textAlign': 'left',
                                          'whiteSpace': 'normal',
                                          'height': 'auto'},
                                      fixed_rows={'headers': True},
                                      css=[{
                                          'selector': '.dash-spreadsheet td div',
                                          'rule': '''
                                          line-height: 15px;
                                          max-height: 30px; min-height: 30px; height: 30px;
                                          display: block;
                                          overflow-y: hidden;'''}],
                                      tooltip_duration=None
                                  )],className='six columns')
                 ])
    ])
# ----------------


@app.callback(
             [Output('line_graph1', 'figure'),
			Output('bar_graph', 'figure')],
            [Input('country', 'value'),
			Input("GovtRestriction","value")])

def build_graph(country_input, measure_input):
    def build_graph1(country_input,govt_rest):
    German_data = DataSet1[(DataSet1['CountryName'] == "Germany")]
    Country_data = DataSet1[(DataSet1['CountryName'] == country_input)]
    # German_data2 = DataSet2[(DataSet2['country'] == "Germany")]
    # Country_data2 = DataSet2[(DataSet2['country'] == country_input)]
    German_data = German_data.rename({'C1_School closing': 'SchoolClosing_Germany', 'C2_Workplace closing': 'WorkPlaceClosing_Germany',
                                   'C6_Stay at home requirements': 'StayHomeRestriction_Germany', 'C4_Restrictions on gatherings': 'GatherRestriction_Germany',
                                   'C5_Close public transport':'TransportRestriction_Germany','C8_International travel controls':'InternationalTravelRestriction_Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'SchoolClosing_'+country_input, 'C2_Workplace closing': 'WorkPlaceClosing_'+country_input,
                                   'C6_Stay at home requirements': 'StayHomeRestriction_'+country_input, 'C4_Restrictions on gatherings': 'GatherRestriction_'+country_input,
                                   'C5_Close public transport':'TransportRestriction_'+country_input,
                                   'C8_International travel controls':'InternationalTravelRestriction_'+country_input}, axis=1)
    # German_data2 = German_data2.rename({'retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_Germany',
    #                                     'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction'})
    df_merge = pd.merge(German_data, Country_data, on='date')
    new_df = pd.DataFrame(df_merge)
    df_1 = pd.DataFrame(new_df)
    if govt_rest == 'School closing':
        fig = px.line(df_1, x='date',
                      y=['SchoolClosing_Germany','SchoolClosing_' + country_input],
                      height=720, width=980, title='Comparing school closure of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['SchoolClosing_Germany',
                         'SchoolClosing_' + country_input],
                      height=720, width=980, title='Comparing school closure of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig,fig1
    elif govt_rest == 'Workplace closing' :
        fig = px.line(df_1, x='date',
                      y=['WorkPlaceClosing_Germany', 'WorkPlaceClosing_' + country_input],
                      height=720, width=980, title='Comparing work place closure of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['WorkPlaceClosing_Germany',
                         'WorkPlaceClosing_' + country_input],
                      height=720, width=980, title='Comparing work place closure of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == 'Stay at home requirements' :
        fig = px.line(df_1, x='Date',
                      y=['StayHomeRestriction_Germany', 'StayHomeRestriction_' + country_input],
                      height=720, width=980, title='Comparing stay at home restrictions of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['StayHomeRestriction_Germany',
                         'StayHomeRestriction_' + country_input],
                      height=720, width=980, title='Comparing stay at home restrictions of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == 'Restrictions on gatherings':
        fig = px.line(df_1, x='date',
                      y=['GatherRestriction_Germany', 'GatherRestriction_' + country_input],
                      height=720, width=980, title='Comparing public gathering restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['GatherRestriction_Germany',
                         'GatherRestriction_' + country_input],
                      height=720, width=980, title='Comparing public gathering restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == 'Close public transport':
        fig = px.line(df_1, x='date',
                      y=['TransportRestriction_Germany', 'TransportRestriction_' + country_input],
                      height=720, width=980, title='Comparing Internal transport restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['TransportRestriction_Germany',
                         'TransportRestriction_' + country_input],
                      height=720, width=980, title='Comparing Internal transport restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == 'International travel controls':
        fig = px.line(df_1, x='date',
                      y=['InternationalTravelRestriction_Germany', 'InternationalTravelRestriction_' + country_input],
                      height=720, width=980, title='Comparing International travel restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['InternationalTravelRestriction_Germany',
                         'InternationalTravelRestriction_' + country_input],
                      height=720, width=980, title='Comparing International travel restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig,fig1

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
                            title='Total COVID-19 Cases Across Europe'),

    fig_map.update_layout(title=dict(font=dict(size=20)))
    return fig_map


@app.callback(
    [Output('data_table', 'data'),
    Output('data_table', 'tooltip_data')],
    [Input('country', 'value')])
def update_datatable(country_input):
    data_per_country_df = data_table_visulaization_df[(
        data_table_visulaization_df['COUNTRY'] == country_input)]
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in data_per_country_df.to_dict('rows')
    ]
    return (data_per_country_df.to_dict('records'), tooltip_data)

@app.callback(
    [Output('data_table_german', 'data'),
    Output('data_table_german', 'tooltip_data')],
    [Input('country', 'value')])
def update_datatable_germany(country_input):
    data_per_country_df = data_table_visulaization_df[(
        data_table_visulaization_df['COUNTRY'] == "Germany")]
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in data_per_country_df.to_dict('rows')
    ]
    return (data_per_country_df.to_dict('records'), tooltip_data)

def main():
    euro_government_measureDF = prepare_data_government_measures(
        govern_measures_data_file)

if __name__ == '__main__':
    main()
    app.run_server(debug=True)
