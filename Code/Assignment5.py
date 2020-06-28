import pandas as pd
import plotly.express as px
import datahandler as dh
import json
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import xlrd


####### Initializing the data files and preparing sanitized dataframe ######

## Data Files
from plotly.validators.layout import _plot_bgcolor

govern_measures_data_file = "datasets/acaps_covid19_government_measures_dataset_0.xlsx"
govern_restrictions_data_file = "datasets/Dataset1.csv"
owid_covid_data_file = "datasets/owid-covid-data.csv"
recoveries_data_file = "datasets/time_series_covid19_recovered_global.csv"

# Reading data for covid statistics and recovery
df_merged, df_europe_cases = dh.read_data_covid_and_recovery(owid_covid_data_file, recoveries_data_file)

## Reading the Data for government restrictions
DataSet1 = dh.read_data_government_restrictions(govern_restrictions_data_file)

## Reading the Data for data table which displays government measures
data_table_visulaization_df = dh.read_data_government_measures(govern_measures_data_file)

#############################################################################

# Intializing the json file which will be used for Geo visualization
with open('europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IDV Mini-Project-COVID"

colors = {
    'background': '#F0FFFF',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.H1("IDV Mini-Project COVID-19",
            style={
                'textAlign': 'center',
                'color': colors['text']
            }),
    html.Div([dcc.Graph(id='the_graph'),
              ], className='nine columns'),
    html.Div([
        html.Label(['Choose cases:'], style={
             'font-weight': 'bold', "text-align": "left"}),
        dcc.Dropdown(id='cases',
                     options=[{'label': 'Confirmed', 'value': 'C'}, {'label': 'Death', 'value': 'D'},
                              {'label': 'Recovered', 'value': 'R'}],
                     value='C', clearable=True, searchable=True,
                     placeholder='Choose Cases...', style={'height': '30px', 'width': '200px'})
    ], className='two columns'),
    html.Div([
        html.Label(['Choose country:'], style={
             'font-weight': 'bold', "text-align": "left"}),
        dcc.Dropdown(id='country',
                     options=[{'label': x, 'value': x} for x in df_europe_cases.sort_values('country')
                              ['country'].unique()], value='Albania', clearable=True, searchable=True,
                     placeholder='Choose Country...', style={'height': '40px', 'width': '1500px'},),
        dcc.Dropdown(id='GovtRestriction',
                               options=[{'label': x, 'value': x} for x in DataSet1.sort_values('GovtRestriction')
                               ['GovtRestriction'].unique()], value='School closing', clearable=True, searchable=True,
                               placeholder='Choose restriction...', style={'height': '40px', 'width': '1500px'}, )
    ], className='ten columns'),
    html.Div([
        dcc.Graph(id='line_graph'),

    ], className='six columns'),
html.Div([
        dcc.Graph(id='bar_graph_cases'),

    ], className='five columns'),
html.Div([
        dcc.Graph(id='bar_graph_deaths'),

    ], className='five columns'),
html.Div([
        dcc.Graph(id='bar_graph_mean'),

    ], className='five columns'),
html.Div([
        dcc.Store(id='memory')]),
html.Div([
        dcc.Graph(id='line_graph_Restriction'),

    ], className='four columns'),

    html.Div([
        dash_table.DataTable(
             id='data_table',
             columns=[{"name": i, "id": i}
                      for i in data_table_visulaization_df.columns],
             # data=data_table_visulaization_df.to_dict('records'),
             page_size=20,  # we have less data in this example, so setting to 20
             #style_table={'height': '300px', 'overflowY': 'auto'},
             style_header={
                 'backgroundColor': 'rgb(230, 230, 230)',
                 'fontWeight': 'bold'
             },
             style_data_conditional=[
                 {
                     'if': {'row_index': 'odd'},
                     'backgroundColor': 'rgb(248, 248, 248)'
                 }
             ],
             style_data={
                 'whiteSpace': 'normal',
                 'height': 'auto',
                 'lineHeight': '15px'
             },

             style_cell={
                 'minWidth': '30px', 'width': '50px', 'maxWidth': '240px',
                 'textAlign': 'left',
                 'whiteSpace': 'normal',
                 'height': 'auto'
             },
             fixed_rows={'headers': True},
             css=[{
                 'selector': '.dash-spreadsheet td div',
                 'rule': '''
                    line-height: 15px;
                    max-height: 30px; min-height: 30px; height: 30px;
                    display: block;
                    overflow-y: hidden;
                '''
             }],
             tooltip_duration=None,
             )
    ], className='eleven columns')
    ])
# ----------------


@app.callback(
    [Output('bar_graph_cases', 'figure'),
     Output('bar_graph_deaths', 'figure')],
    [Input('country', 'value'), ])

def build_bargraph(country_input):
    df_per_country_bar = df_merged[(df_merged['country'] == country_input)]
    df_per_country_bar = df_per_country_bar.rename({'new_cases':'new_cases_'+country_input,'new_deaths':'new_deaths_'+country_input}, axis=1)
    df_germany_bar = df_merged[(df_merged['country'] == "Germany")]
    df_germany_bar = df_germany_bar.rename({'new_cases':'new_cases_Germany','new_deaths':'new_deaths_Germany'},  axis=1)
    df_merge_bar = pd.merge(df_germany_bar, df_per_country_bar, on='date')
    # print(df_merge.to_string())
    df_merge_bar = pd.DataFrame(df_merge_bar)
    # fig = px.line(df_merge1, x='date', y=['new_cases_Germany','new_deaths_Germany','new_cases_'+country_input,'new_deaths_'+country_input],
    #               height=720, width=980, title='Comparing COVID cases of '+country_input+' against Germany',
    #               template='plotly_dark')

    fig = go.Figure(data=[
        go.Bar(name='new_cases_Germany', x=df_merge_bar['date'], y=df_merge_bar['new_cases_Germany']),
        go.Bar(name='new_cases_'+country_input, x=df_merge_bar['date'], y=df_merge_bar['new_cases_'+country_input])


    ])

    fig1 = go.Figure(data=[
        go.Bar(name='new_deaths_Germany', x=df_merge_bar['date'], y=df_merge_bar['new_deaths_Germany']),
        go.Bar(name='new_deaths_' + country_input, x=df_merge_bar['date'], y=df_merge_bar['new_deaths_' + country_input])

    ])

    return fig,fig1

@app.callback(
    Output('line_graph', 'figure'),

    [Input('country', 'value'),])

def build_graph(country_input):
    df_per_country = df_merged[(df_merged['country'] == country_input)]
    df_per_country = df_per_country.rename({'total_cases': 'total_cases_'+country_input,
                                            'total_deaths': 'total_deaths_'+country_input,
                                            'total_recovery': 'total_recovery_'+country_input}, axis=1)
    df_germany = df_merged[(df_merged['country'] == "Germany")]
    df_germany = df_germany.rename({'total_cases': 'total_cases_Germany', 'total_deaths': 'total_deaths_Germany',
                                    'total_recovery': 'total_recovery_Germany'},  axis=1)
    df_merge = pd.merge(df_germany, df_per_country, on='date')
    # print(df_merge.to_string())
    df_merge = pd.DataFrame(df_merge)
    fig = px.line(df_merge, x='date', y=["total_cases_Germany", "total_deaths_Germany", "total_recovery_Germany",
                                         "total_cases_"+country_input, "total_deaths_"+country_input,
                                         "total_recovery_"+country_input],
                  height=720, width=980, title='Comparing COVID cases of '+country_input+' against Germany')
    fig.update_layout(title=dict(font=dict(size=20)))
    return fig

#Items from DataSet1 and DataSet2
@app.callback(
    [Output('line_graph_Restriction', 'figure'),
     Output('bar_graph_mean','figure')],
    [Input('country', 'value'),
     Input('GovtRestriction','value')])

def build_graph_restriction(country_input,govt_rest):
    German_data_Lrestriction = DataSet1[(DataSet1['CountryName'] == "Germany")]
    Country_data_Lrestriction = DataSet1[(DataSet1['CountryName'] == country_input)]
    German_data_Lrestriction = German_data_Lrestriction.rename({'C1_School closing': 'SchoolClosing_Germany', 'C2_Workplace closing': 'WorkPlaceClosing_Germany',
                                   'C6_Stay at home requirements': 'StayHomeRestriction_Germany', 'C4_Restrictions on gatherings': 'GatherRestriction_Germany',
                                   'C5_Close public transport':'TransportRestriction_Germany','C8_International travel controls':'InternationalTravelRestriction_Germany','retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_Germany',
                                        'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_Germany',
                                        'parks_percent_change_from_baseline':'Park_Restriction_Germany'}, axis=1)
    Country_data_Lrestriction = Country_data_Lrestriction.rename({'C1_School closing': 'SchoolClosing_'+country_input, 'C2_Workplace closing': 'WorkPlaceClosing_'+country_input,
                                   'C6_Stay at home requirements': 'StayHomeRestriction_'+country_input, 'C4_Restrictions on gatherings': 'GatherRestriction_'+country_input,
                                   'C5_Close public transport':'TransportRestriction_'+country_input,
                                   'C8_International travel controls':'InternationalTravelRestriction_'+country_input,'retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_'+country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_'+country_input,
                                        'parks_percent_change_from_baseline':'Park_Restriction_'+country_input}, axis=1)
    df_merge_Lrestriction = pd.merge(German_data_Lrestriction, Country_data_Lrestriction, on='date')
    df_merge_Lrestriction['meanGermany'] = df_merge_Lrestriction['SchoolClosing_Germany'].div(9, axis=0) + df_merge_Lrestriction[
        'WorkPlaceClosing_Germany'].div(9, axis=0) + df_merge_Lrestriction['StayHomeRestriction_Germany'].div(9, axis=0) + \
                                   df_merge_Lrestriction[
                                       'GatherRestriction_Germany'].div(9, axis=0) + df_merge_Lrestriction[
                                       'TransportRestriction_Germany'].div(9, axis=0) + df_merge_Lrestriction[
                                       'InternationalTravelRestriction_Germany'].div(9, axis=0) + df_merge_Lrestriction[
                                       'Retail_Restriction_Germany'].div(9, axis=0) + df_merge_Lrestriction[
                                       'Grocery_Pharmacy_Restriction_Germany'].div(9, axis=0) + df_merge_Lrestriction[
                                       'Park_Restriction_Germany'].div(9, axis=0)
    df_merge_Lrestriction['meanCountry'] = df_merge_Lrestriction['SchoolClosing_' + country_input].div(9, axis=0) + df_merge_Lrestriction[
        'WorkPlaceClosing_' + country_input].div(9, axis=0) + df_merge_Lrestriction['StayHomeRestriction_' + country_input].div(
        9, axis=0) + df_merge_Lrestriction[
                                       'GatherRestriction_' + country_input].div(9, axis=0) + df_merge_Lrestriction[
                                       'TransportRestriction_' + country_input].div(9, axis=0) + df_merge_Lrestriction[
                                       'InternationalTravelRestriction_' + country_input].div(9, axis=0) + \
                                   df_merge_Lrestriction[
                                       'Retail_Restriction_' + country_input].div(9, axis=0) + df_merge_Lrestriction[
                                       'Grocery_Pharmacy_Restriction_' + country_input].div(9, axis=0) + df_merge_Lrestriction[
                                       'Park_Restriction_' + country_input].div(9, axis=0)

    df_merge_Lrestriction['meanGermany'] = df_merge_Lrestriction['meanGermany'].fillna(0)
    df_merge_Lrestriction['meanCountry'] = df_merge_Lrestriction['meanCountry'].fillna(0)

    df_merge_Lrestriction = df_merge_Lrestriction.rename(
        {'meanGermany': 'Overall_Restriction_Germany', 'meanCountry': 'Overall_Restriction_' + country_input}, axis=1)

    new_df_Lrestriction = pd.DataFrame(df_merge_Lrestriction)
    # new_df2 = pd.DataFrame(df_merge2)
    df_1_Lrestriction = pd.DataFrame(new_df_Lrestriction)
    # df_2 = pd.DataFrame(new_df2)
    fig1 = px.line(df_1_Lrestriction, x='date', y=['Overall_Restriction_Germany', 'Overall_Restriction_'+country_input])
    if govt_rest == 'School closing':
        fig = drawLinegraph(df_1_Lrestriction,'SchoolClosing_',country_input)


        return fig,fig1
    elif govt_rest == 'Workplace closing' :
        fig = drawLinegraph(df_1_Lrestriction, 'WorkPlaceClosing_', country_input)


        return fig,fig1
    elif govt_rest == 'Stay at home requirements' :
        fig = drawLinegraph(df_1_Lrestriction, 'StayHomeRestriction_', country_input)


        return fig,fig1
    elif govt_rest == 'Restrictions on gatherings':
        fig = drawLinegraph(df_1_Lrestriction, 'GatherRestriction_', country_input)



        return fig,fig1
    elif govt_rest == 'Close public transport':
        fig = drawLinegraph(df_1_Lrestriction, 'TransportRestriction_', country_input)



        return fig,fig1
    elif govt_rest == 'International travel controls':
        fig = drawLinegraph(df_1_Lrestriction, 'InternationalTravelRestriction_', country_input)


        return fig,fig1
    elif govt_rest == 'Restriction on Retail':
        fig = drawLinegraph(df_1_Lrestriction, 'Retail_Restriction_', country_input)


        return fig,fig1
    elif govt_rest == "Restriction on pharmacy":
        fig = drawLinegraph(df_1_Lrestriction, 'Grocery_Pharmacy_Restriction_', country_input)


        return fig,fig1
    elif govt_rest == "Restriction on park":
        fig = drawLinegraph(df_1_Lrestriction, 'Park_Restriction_', country_input)


        return fig,fig1




def drawLinegraph(Dframe,x,country):
    b = x+'Germany'
    c= x+country
    fig = px.line(Dframe, x='date',
                  y=[b,c],
                  height=720, width=980,
                  title='Comparing' + x +'of ' + country + ' against Germany')
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
                            projection="miller", color_continuous_scale='reds',
                            title='Total COVID-19 Cases Across Europe', width=1500, height=720)  # , template='plotly_dark')

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

def main():
    euro_government_measureDF = dh.read_data_government_measures(
        govern_measures_data_file)


if __name__ == '__main__':
    main()
    app.run_server(debug=True)
