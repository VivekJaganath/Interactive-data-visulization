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
from plotly.validators.layout import _plot_bgcolor

####### Initializing the data files and preparing sanitized dataframe ######

# Data Files
# Source : https://www.acaps.org/covid19-government-measures-dataset
govern_measures_data_file = "datasets/acaps_covid19_government_measures_dataset_0.xlsx"

govern_restrictions_data_file = "datasets/Dataset1.csv"

# Source : https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv
owid_covid_data_file = "datasets/owid-covid-data.csv"

recoveries_data_file = "datasets/time_series_covid19_recovered_global.csv"

# Reading data for covid statistics and recovery
df_merged, df_merged_raw, df_europe_cases = dh.read_data_covid_and_recovery(
    owid_covid_data_file, recoveries_data_file)

# Reading the Data for government restrictions
DataSet1 = dh.read_data_government_restrictions(govern_restrictions_data_file)

# Reading the Data for data table which displays government measures
data_table_visulaization_df = dh.read_data_government_measures(
    govern_measures_data_file)

# https://community.plotly.com/t/dash-range-slider-with-date/17915/7
# Preparing the date objects for displaying in slider
date_num_encoder = [x for x in range(len(df_merged['date'].unique()))]
date_increamentor = 10
number_date_array = list(
    zip(date_num_encoder, pd.to_datetime(df_merged['date']).dt.date.unique()))
number_date_range = number_date_array[0::date_increamentor]

number_date_range_dict = dict(number_date_range)

#############################################################################

# Intializing the json file which will be used for Geo visualization
with open('europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
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
        html.Label(['Choose Date:'], style={
            'font-weight': 'bold', "text-align": "left"}),
        dcc.RangeSlider(id='slider_date',
                        min=date_num_encoder[0],  # the first date
                        max=date_num_encoder[-1],  # the last date
                        value=[date_num_encoder[0], date_num_encoder[0]],
                        step=date_increamentor,
                        marks={number: date.strftime('%Y-%m-%d') for number, date in number_date_range}
                        )
    ], className='ten columns'),

    html.Div([
        html.Label(['Choose country:'], style={
            'font-weight': 'bold', "text-align": "left"}),
        dcc.Dropdown(id='country',
                     options=[{'label': x, 'value': x} for x in df_europe_cases.sort_values('country')
                     ['country'].unique()], value='Albania', clearable=True, searchable=True,
                     placeholder='Choose Country...', style={'height': '40px', 'width': '1500px'}, ),

        dcc.Dropdown(id='GovtRestriction',
                     options=[{'label': x, 'value': x} for x in DataSet1.sort_values('GovtRestriction')
                     ['GovtRestriction'].unique()], value='School closing', clearable=True, searchable=True,
                     placeholder='Choose restriction...', style={'height': '40px', 'width': '1500px'}, ),
        dcc.Dropdown(id='Type of Graph',
                     options=[{'label': 'LineGraph', 'value': 'Line graph'}, {'label': 'BarGraph', 'value': 'Bar graph'}],
                     value='Line graph', clearable=True, searchable=True,
                     placeholder='Choose Graph Type...', style={'height': '30px', 'width': '200px'})
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
        dcc.Graph(id='line_graph1'),

    ], className='four columns'),

    html.Div([
        dash_table.DataTable(
            id='data_table',
            columns=[{"name": i, "id": i}
                     for i in data_table_visulaization_df.columns],
            # data=data_table_visulaization_df.to_dict('records'),
            page_size=20,  # we have less data in this example, so setting to 20
            # style_table={'height': '300px', 'overflowY': 'auto'},
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
    Output('line_graph', 'figure'),
    [Input('country', 'value'),
     Input('slider_date', 'value')])
def build_graph(country_input, input_date_range):
    # Filtering the results based on input date range
    df_merged_filtered = dh.handle_updated_dates(df_merged, 'date', input_date_range, number_date_range_dict)

    df_per_country = df_merged_filtered[(df_merged_filtered['country'] == country_input)]
    df_per_country = df_per_country.rename({'total_cases': 'total_cases_' + country_input,
                                            'total_deaths': 'total_deaths_' + country_input,
                                            'total_recovery': 'total_recovery_' + country_input}, axis=1)
    df_germany = df_merged_filtered[(df_merged_filtered['country'] == "Germany")]
    df_germany = df_germany.rename({'total_cases': 'total_cases_Germany', 'total_deaths': 'total_deaths_Germany',
                                    'total_recovery': 'total_recovery_Germany'}, axis=1)
    df_merge = pd.merge(df_germany, df_per_country, on='date')
    # print(df_merge.to_string())
    df_merge = pd.DataFrame(df_merge)

    fig = px.line(df_merge, x='date', y=["total_cases_Germany", "total_deaths_Germany", "total_recovery_Germany",
                                         "total_cases_" + country_input, "total_deaths_" + country_input,
                                         "total_recovery_" + country_input],
                  height=720, width=980, title='Comparing COVID cases of ' + country_input + ' against Germany')
    fig.update_layout(title=dict(font=dict(size=20)))
    return fig


@app.callback(
    [Output('bar_graph_cases', 'figure'),
     Output('bar_graph_deaths', 'figure')],
    [Input('country', 'value'),
     Input('slider_date', 'value')])

def build_bargraph(country_input, input_date_range):
    # Filtering the results based on input date range
    df_merged_filtered = dh.handle_updated_dates(df_merged, 'date', input_date_range, number_date_range_dict)

    df_per_country1 = df_merged_filtered[(df_merged_filtered['country'] == country_input)]
    df_per_country1 = df_per_country1.rename(
        {'new_cases': 'new_cases_' + country_input, 'new_deaths': 'new_deaths_' + country_input}, axis=1)
    df_germany1 = df_merged_filtered[(df_merged_filtered['country'] == "Germany")]
    df_germany1 = df_germany1.rename({'new_cases': 'new_cases_Germany', 'new_deaths': 'new_deaths_Germany'}, axis=1)
    df_merge1 = pd.merge(df_germany1, df_per_country1, on='date')
    # print(df_merge1)

    df_merge1 = pd.DataFrame(df_merge1)

    print(df_merge1.info())

    fig = go.Figure(data=[
        go.Bar(name='new_cases_of_Germany', x=df_merge1['date'], y=df_merge1['new_cases_Germany']),
        go.Bar(name='new_cases_' + country_input, x=df_merge1['date'], y=df_merge1['new_cases_' + country_input])
    ])
    fig.update_layout(title='Comparing new COVID cases ' + 'of ' + country_input + ' against Germany')
    fig1 = go.Figure(data=[
        go.Bar(name='new_deaths_Germany', x=df_merge1['date'], y=df_merge1['new_deaths_Germany']),
        go.Bar(name='new_deaths_' + country_input, x=df_merge1['date'], y=df_merge1['new_deaths_' + country_input])

    ])
    fig1.update_layout(title='Comparing new COVID deaths ' + 'of ' + country_input + ' against Germany')

    return fig, fig1


# Items from DataSet1 and DataSet2
@app.callback(
    Output('line_graph1', 'figure')
    ,
    [Input('country', 'value'), Input("GovtRestriction", "value"),Input("Type of Graph","value")],
)
def build_graph1(country_input, govt_rest,gType):
    German_data = DataSet1[(DataSet1['CountryName'] == "Germany")]
    Country_data = DataSet1[(DataSet1['CountryName'] == country_input)]
    German_data = German_data.rename(
        {'C1_School closing': 'SchoolClosing_Germany', 'C2_Workplace closing': 'WorkPlaceClosing_Germany',
         'C6_Stay at home requirements': 'StayHomeRestriction_Germany',
         'C4_Restrictions on gatherings': 'GatherRestriction_Germany',
         'C5_Close public transport': 'TransportRestriction_Germany',
         'C8_International travel controls': 'InternationalTravelRestriction_Germany',
         'retail_and_recreation_percent_change_from_baseline': 'Retail_Restriction_Germany',
         'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery_Pharmacy_Restriction_Germany',
         'parks_percent_change_from_baseline': 'Park_Restriction_Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'SchoolClosing_' + country_input,
                                        'C2_Workplace closing': 'WorkPlaceClosing_' + country_input,
                                        'C6_Stay at home requirements': 'StayHomeRestriction_' + country_input,
                                        'C4_Restrictions on gatherings': 'GatherRestriction_' + country_input,
                                        'C5_Close public transport': 'TransportRestriction_' + country_input,
                                        'C8_International travel controls': 'InternationalTravelRestriction_' + country_input,
                                        'retail_and_recreation_percent_change_from_baseline': 'Retail_Restriction_' + country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery_Pharmacy_Restriction_' + country_input,
                                        'parks_percent_change_from_baseline': 'Park_Restriction_' + country_input},
                                       axis=1)
    df_merge = pd.merge(German_data, Country_data, on='date')
    # print(df_merge2['date'])
    new_df = pd.DataFrame(df_merge)
    # new_df2 = pd.DataFrame(df_merge2)
    df_1 = pd.DataFrame(new_df)
    # df_2 = pd.DataFrame(new_df2)
    if govt_rest == 'School closing':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'SchoolClosing_', country_input)
        else :
            fig = drawBargraph(df_1, 'SchoolClosing_', country_input)

        return fig
    elif govt_rest == 'Workplace closing':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'WorkPlaceClosing_', country_input)
        else:
            fig = drawBargraph(df_1, 'WorkPlaceClosing_', country_input)

        return fig
    elif govt_rest == 'Stay at home requirements':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'StayHomeRestriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'StayHomeRestriction_', country_input)


        return fig
    elif govt_rest == 'Restrictions on gatherings':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'GatherRestriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'GatherRestriction_', country_input)

        return fig
    elif govt_rest == 'Close public transport':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'TransportRestriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'TransportRestriction_', country_input)

        return fig
    elif govt_rest == 'International travel controls':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'InternationalTravelRestriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'InternationalTravelRestriction_', country_input)


        return fig
    elif govt_rest == 'Restriction on Retail':
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'Retail_Restriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'Retail_Restriction_', country_input)


        return fig
    elif govt_rest == "Restriction on pharmacy":
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'Grocery_Pharmacy_Restriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'Grocery_Pharmacy_Restriction_', country_input)

        return fig
    elif govt_rest == "Restriction on park":
        if gType == 'Line graph':
            fig = drawLinegraph(df_1, 'Park_Restriction_', country_input)
        else:
            fig = drawBargraph(df_1, 'Park_Restriction_', country_input)

        return fig


def drawLinegraph(Dframe, x, country):
    b = x + 'Germany'
    c = x + country
    fig = px.line(Dframe, x='date',
                  y=[b, c],
                  height=720, width=980,
                  title='Comparing' + x + 'of ' + country + ' against Germany')
    return fig

def drawBargraph(Dframe, x, country):
    b = x + 'Germany'
    c = x + country
    fig = go.Figure(data=[
        go.Bar(name='new_cases_of_Germany', x=Dframe['date'], y=Dframe[b]),
        go.Bar(name='new_cases_' + country, x=Dframe['date'], y=Dframe[c])
    ])
    return fig


@app.callback(
    Output('bar_graph_mean', 'figure')
    ,
    [Input('country', 'value'), Input("GovtRestriction", "value")],
)
def build_graph_mean(country_input, govt_rest):
    German_data = DataSet1[(DataSet1['CountryName'] == "Germany")]
    Country_data = DataSet1[(DataSet1['CountryName'] == country_input)]
    German_data = German_data.rename(
        {'C1_School closing': 'SchoolClosing_Germany', 'C2_Workplace closing': 'WorkPlaceClosing_Germany',
         'C6_Stay at home requirements': 'StayHomeRestriction_Germany',
         'C4_Restrictions on gatherings': 'GatherRestriction_Germany',
         'C5_Close public transport': 'TransportRestriction_Germany',
         'C8_International travel controls': 'InternationalTravelRestriction_Germany',
         'retail_and_recreation_percent_change_from_baseline': 'Retail_Restriction_Germany',
         'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery_Pharmacy_Restriction_Germany',
         'parks_percent_change_from_baseline': 'Park_Restriction_Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'SchoolClosing_' + country_input,
                                        'C2_Workplace closing': 'WorkPlaceClosing_' + country_input,
                                        'C6_Stay at home requirements': 'StayHomeRestriction_' + country_input,
                                        'C4_Restrictions on gatherings': 'GatherRestriction_' + country_input,
                                        'C5_Close public transport': 'TransportRestriction_' + country_input,
                                        'C8_International travel controls': 'InternationalTravelRestriction_' + country_input,
                                        'retail_and_recreation_percent_change_from_baseline': 'Retail_Restriction_' + country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery_Pharmacy_Restriction_' + country_input,
                                        'parks_percent_change_from_baseline': 'Park_Restriction_' + country_input},
                                       axis=1)
    df_merge_mean = pd.merge(German_data, Country_data, on='date')
    df_merge_mean['meanGermany'] = df_merge_mean['SchoolClosing_Germany'].div(9, axis=0) + df_merge_mean[
        'WorkPlaceClosing_Germany'].div(9, axis=0) + df_merge_mean['StayHomeRestriction_Germany'].div(9, axis=0) + \
                                   df_merge_mean[
                                       'GatherRestriction_Germany'].div(9, axis=0) + df_merge_mean[
                                       'TransportRestriction_Germany'].div(9, axis=0) + df_merge_mean[
                                       'InternationalTravelRestriction_Germany'].div(9, axis=0) + df_merge_mean[
                                       'Retail_Restriction_Germany'].div(9, axis=0) + df_merge_mean[
                                       'Grocery_Pharmacy_Restriction_Germany'].div(9, axis=0) + df_merge_mean[
                                       'Park_Restriction_Germany'].div(9, axis=0)
    df_merge_mean['meanCountry'] = df_merge_mean['SchoolClosing_' + country_input].div(9, axis=0) + df_merge_mean[
        'WorkPlaceClosing_' + country_input].div(9, axis=0) + df_merge_mean['StayHomeRestriction_' + country_input].div(
        9, axis=0) + df_merge_mean[
                                       'GatherRestriction_' + country_input].div(9, axis=0) + df_merge_mean[
                                       'TransportRestriction_' + country_input].div(9, axis=0) + df_merge_mean[
                                       'InternationalTravelRestriction_' + country_input].div(9, axis=0) + \
                                   df_merge_mean[
                                       'Retail_Restriction_' + country_input].div(9, axis=0) + df_merge_mean[
                                       'Grocery_Pharmacy_Restriction_' + country_input].div(9, axis=0) + df_merge_mean[
                                       'Park_Restriction_' + country_input].div(9, axis=0)
    df_merge_mean['meanGermany'] = df_merge_mean['meanGermany'].fillna(0)
    df_merge_mean['meanCountry'] = df_merge_mean['meanCountry'].fillna(0)

    df_merge_mean = df_merge_mean.rename(
        {'meanGermany': 'Overall_Restriction_Germany', 'meanCountry': 'Overall_Restriction_' + country_input}, axis=1)

    new_df_mean = pd.DataFrame(df_merge_mean)
    df_1_mean = pd.DataFrame(new_df_mean)

    fig = px.line(df_1_mean, x='date', y=['Overall_Restriction_Germany', 'Overall_Restriction_'+country_input],title='Comparing overall restriction imposed by ' + country_input + ' against Germany')

    return fig


@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input('cases', 'value'),
     Input('slider_date', 'value')])
def build_map(case, input_date_range):
    df_merged_date_filtered = dh.handle_updated_dates(df_merged_raw, 'date', input_date_range, number_date_range_dict)

    if case == 'R':
        case_chosen = 'total_recovery'
    elif case == 'D':
        case_chosen = 'total_deaths'
    else:
        case_chosen = 'total_cases'

    fig_map = px.choropleth(data_frame=df_merged_date_filtered, geojson=europe_geo_json, locations='country',
                            scope="europe", color=case_chosen, hover_name='country', featureidkey='properties.name',
                            projection="miller", color_continuous_scale='reds',
                            title='Total COVID-19 Cases Across Europe', width=1500,
                            height=720)  # , template='plotly_dark')

    fig_map.update_layout(title=dict(font=dict(size=20)))
    return fig_map


@app.callback(
    [Output('data_table', 'data'),
     Output('data_table', 'tooltip_data')],
    [Input('country', 'value'),
     Input('slider_date', 'value')])
def update_datatable(country_input, input_date_range):
    data_per_country_df = data_table_visulaization_df[(data_table_visulaization_df['COUNTRY'] == country_input)]

    data_per_country_df = dh.handle_updated_dates(data_per_country_df, 'DATE_IMPLEMENTED', input_date_range,
                                                  number_date_range_dict)
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
