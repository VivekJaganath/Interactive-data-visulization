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
import xlrd


####### Initializing the data files and preparing sanitized dataframe ######

## Data Files
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

    ], className='four columns'),
html.Div([dcc.Graph(id='bar_graph'),
              html.Label([''], style={'font-weight': 'bold', "text-align": "left"}),

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
                  height=720, width=980, title='Comparing COVID cases of '+country_input+' against Germany',
                  template='plotly_dark')
    fig.update_layout(title=dict(font=dict(size=20)))
    return fig

#Items from DataSet1 and DataSet2
@app.callback(
    [Output('line_graph1', 'figure'),
     Output('bar_graph', 'figure')],
    [Input('country', 'value'),Input("GovtRestriction","value")],
      )

def build_graph1(country_input,govt_rest):
    German_data = DataSet1[(DataSet1['CountryName'] == "Germany")]
    Country_data = DataSet1[(DataSet1['CountryName'] == country_input)]
    # German_data2 = DataSet2[(DataSet2['country'] == "Germany")]
    # Country_data2 = DataSet2[(DataSet2['country'] == country_input)]
    German_data = German_data.rename({'C1_School closing': 'SchoolClosing_Germany', 'C2_Workplace closing': 'WorkPlaceClosing_Germany',
                                   'C6_Stay at home requirements': 'StayHomeRestriction_Germany', 'C4_Restrictions on gatherings': 'GatherRestriction_Germany',
                                   'C5_Close public transport':'TransportRestriction_Germany','C8_International travel controls':'InternationalTravelRestriction_Germany','retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_Germany',
                                        'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_Germany',
                                        'parks_percent_change_from_baseline':'Park_Restriction_Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'SchoolClosing_'+country_input, 'C2_Workplace closing': 'WorkPlaceClosing_'+country_input,
                                   'C6_Stay at home requirements': 'StayHomeRestriction_'+country_input, 'C4_Restrictions on gatherings': 'GatherRestriction_'+country_input,
                                   'C5_Close public transport':'TransportRestriction_'+country_input,
                                   'C8_International travel controls':'InternationalTravelRestriction_'+country_input,'retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_'+country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_'+country_input,
                                        'parks_percent_change_from_baseline':'Park_Restriction_'+country_input}, axis=1)
    # German_data2 = German_data2.rename({'retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_Germany',
    #                                     'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_Germany',
    #                                     'parks_percent_change_from_baseline':'Park_Restriction_Germany'})
    # Country_data2 = Country_data2.rename({'retail_and_recreation_percent_change_from_baseline':'Retail_Restriction_'+country_input,
    #                                     'grocery_and_pharmacy_percent_change_from_baseline':'Grocery_Pharmacy_Restriction_'+country_input,
    #                                     'parks_percent_change_from_baseline':'Park_Restriction_'+country_input})
    # df_merge2 = pd.merge(German_data2, Country_data2, on='date')
    df_merge = pd.merge(German_data, Country_data, on='date')
    # print(df_merge2['date'])
    new_df = pd.DataFrame(df_merge)
    # new_df2 = pd.DataFrame(df_merge2)
    df_1 = pd.DataFrame(new_df)
    # df_2 = pd.DataFrame(new_df2)
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
    elif govt_rest == 'Restriction on Retail':
        fig = px.line(df_1, x='date',
                      y=['Retail_Restriction_Germany', 'Retail_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['Retail_Restriction_Germany',
                         'Retail_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == "Restriction on pharmacy":
        fig = px.line(df_1, x='date',
                      y=['Grocery_Pharmacy_Restriction_Germany', 'Grocery_Pharmacy_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['Grocery_Pharmacy_Restriction_Germany',
                         'Grocery_Pharmacy_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1
    elif govt_rest == "Restriction on park":
        fig = px.line(df_1, x='date',
                      y=['Grocery_Pharmacy_Restriction_Germany', 'Grocery_Pharmacy_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')

        fig1 = px.bar(df_1, x='date',
                      y=['Park_Restriction_Germany',
                         'Park_Restriction_' + country_input],
                      height=720, width=980,
                      title='Comparing Retail restriction of ' + country_input + ' against Germany',
                      template='plotly_dark')
        return fig, fig1







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
