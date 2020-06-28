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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Data Files
# Source : https://www.acaps.org/covid19-government-measures-dataset
govern_measures_data_file = "Code/datasets/acaps_covid19_government_measures_dataset_0.xlsx"

govern_restrictions_data_file = "Code/datasets/Dataset1.csv"

# Source : https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv
owid_covid_data_file = "Code/datasets/owid-covid-data.csv"

recoveries_data_file = "Code/datasets/time_series_covid19_recovered_global.csv"

# Reading data for covid statistics and recovery
df_merged, df_merged_raw, df_europe_cases = dh.read_data_covid_and_recovery(
    owid_covid_data_file, recoveries_data_file)

# Reading the Data for government restrictions
DataSet1 = dh.read_data_government_restrictions(govern_restrictions_data_file)

# Reading the Data for data table which displays government measures
data_table_visulaization_df = dh.read_data_government_measures(
    govern_measures_data_file)

# Preparing the date objects for displaying in slider
date_increamentor = 10
date_num_encoder, number_date_range_dict, slider_marks_dict  = dh.generate_slider_data(df_merged, 'date', date_increamentor)

#############################################################################

# Intializing the json file which will be used for Geo visualization
with open('Code/europe_geo.json') as json_file:
    europe_geo_json = json.load(json_file)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IDV Mini-Project-COVID"

colors = {
    'background': '#F0FFFF',
    'text': '#7FDBFF',
    'black':'#3b3a30',
    'white':'#FFFFFF'
}

app.layout = html.Div([
    html.H1("IDV Mini-Project COVID-19",
            style={
                #'background': 'linear-gradient(#bccef7, 5%, #3e71bd, 90%, #bccef7)',
                'background-color':'#3e71bd',
                'textAlign': 'center',
                'color': colors['white'],
                'height':'75px',
                'width':'100%',
                'max-width': '100%',
                'font-size':'50px',
                'font-weight':'bold',
                'font-family':'Courier New',
                'margin-bottom':'20px'
    }),

    ##Slider##
    html.Div([
            
        html.Div([
            html.Label(['Date Slider limits the data for chosen dates and is applicable to all the shown graphs. Please choose a date:'], style={
             "text-align": "left"}),
            dcc.RangeSlider(id='slider_date',
                        min=date_num_encoder[0],  # the first date
                        max=date_num_encoder[-4],  # the last date
                        value=[date_num_encoder[0],date_num_encoder[-4]],
                        #step=date_increamentor,
                        marks=slider_marks_dict
                        )
        ], style={'float':'left','background-color':'white','width':'92%',
    'max-width':'92%','height':'60px',
    'margin-left':'2%'})
    ], style={'float':'left','background-color':'white','width':'92%',
    'max-width':'92%','height':'80px',
    'margin-left':'4%',
    'box-shadow':'5px 5px 5px #888888'
    }),
    ##Slider##

    ##Space Div##    
    html.Div(className='twelve columns', style={'height':'50px'}),

    html.Div([
        html.Div([dcc.Graph(id='the_graph', style={'width':'1000 px'}),
              ], className='twelve columns', style={'float':'left',
              'max-width':'80%',
              'height':'400px',
              'max-height':'400px',
              'display' : 'inline-block'}),
    html.Div([
        html.Label(['Choose cases:'], style={'float':'left',
            'background-color':'white', 'margin-top':'10px',
            'font-weight': 'bold','font-size':'15px'}),
        dcc.RadioItems(id='cases',
                     options=[{'label': 'Confirmed', 'value': 'C'}, {'label': 'Death', 'value': 'D'},
                              {'label': 'Recovered', 'value': 'R'}],
                     value='C', style={'float':'left', 'margin-left':'10px',
                     'background-color':'white',
                     'height': '150px',
                     'width':'100px',
                     #'max-width':'30%','font-size':'25px'
                     }),
        dcc.Textarea(
        id='textarea-example',
        value='This map helps to visualize statistical data through shading patterns and it represents data concerning Confirmed cases, Deaths and Recovery rates, across European nations. The shading patterns (intensity of color) represents the occurence intensity of corresponding cases.',
        readOnly='readOnly',
        draggable='false',
        disabled='true',
        style={'background-color':'white','float':'left','border-color':'white', 'height':'250px', 'width':'250px'
        },
    )
    ], className='two columns', style={'height':'400px','float':'left','display' : 'inline-block',
    'margin-left':'10px','background-color':'white','max-width':'20%'}),
    #############################
    
    ],style={'float':'left','display':'inline-block','background-color':'white','max-width':'92%','height':'520px', 'margin-left':'4%','margin-right':'4%',
    'box-shadow':'5px 5px 5px #888888'    
    }),

    ##Space Div##    
    html.Div(className='twelve columns', style={'height':'50px'}),

    #########Selection of country###########
    html.Div([
        html.H6("Select the country to generate trends in comparison with Germany",style={'float':'left',
        'margin-top':'10px','margin-bottom':'10px',
        'width':'92%', 'text-align':'center',
        'color':'#ffffff',
        'font-size':'30px',
        'font-weight':'bold',
        'max-width':'92%', 'font-family':'Comic Sans MS',
        'margin-left':'4%','height': '30px'}),
        
        dcc.Dropdown(id='country',
                     options=[{'label': x, 'value': x} for x in df_europe_cases.sort_values('country')
                              ['country'].unique()], value='United Kingdom', clearable=True, searchable=True,
                     placeholder='Choose Country...', style={'float':'left',
                     'height': '30px',
                     'width':'52%',
                     'max-width':'92%',
                     'margin-top':'4px',
                     'margin-left':'24%'})
    ],style={'float':'left','display':'inline-block','background-color':'#3e71bd', 'width':'92%',
    'max-width':'92%','height':'120px', 'margin-left':'4%','margin-right':'4%',
    'box-shadow':'5px 5px 5px #888888'}),

    #########Selection of country###########

    ##Space Div##    
    html.Div(className='twelve columns', style={'height':'1px'}),

    ##Trend Graphs##
    html.Div(
        [html.Div([
        html.H1("",style={'textAlign': 'center',
                'height':'10px',
                'background-color':'white',
                }),
        
    html.Div([
        html.H1("Comparing general trends", className='twelve columns', style={'textAlign': 'center',
                'height':'30px',
                'font-size':'30px',
                'margin-left':'4%',
                'background-color':'white',
                'margin-bottom':'0px',
                'font-family':'Comic Sans MS'}),
                ], 
                style={'float':'left','margin-left':'4%',
                'margin-right':'4%','margin-bottom':'0px',
                'width':'82%',
                'max-width':'82%'
                }),
            ], style={'background-color':'white', 'float':'left', 'margin-left':'4%','margin-right':'4%',
            'height':'70px', 'width':'92%',
                'max-width':'92%'}),
            
    html.Hr(style={'margin-top':'20px','margin-left':'4%','float':'left',
    'border-top':'3px solid #bbb',
    'width':'92%',
    'max-width':'92%'
    }),
    html.Div([
        dcc.Graph(id='line_graph'),
    ],
        style={'float':'left','background-color':'white','height':'470px', 'width':'49%',
              'margin-bottom':'2%'}),
    html.Div([
        dcc.Graph(id='bar_graph')
    ],
        style={'float':'left','background-color':'white','height':'470px', 'width':'49%',
              'margin-bottom':'2%'}),
    ],
    style={'float':'left','box-shadow':'9px 9px 5px #888888','background-color':'white','height':'650px',
    'margin-left':'5%','margin-right':'5%','width':'90%','max-width':'90%'}),          
    ##Trend Graphs##

    html.Div(className='twelve columns', style={'float':'left','width':'92%',
                'max-width':'92%','height':'10px'}),
    
    ##Comparison Graphs##
    html.Div(
        [html.Div([
        html.H1("",style={'textAlign': 'center',
                'height':'10px',
                'background-color':'white',
                }),
        
    html.Div([
        html.H1("Comparison of Policy Measures with Germany", className='twelve columns', style={'textAlign': 'center',
                'height':'30px',
                'font-size':'30px',
                'background-color':'white',
                'margin-bottom':'0px',
                'font-family':'Comic Sans MS'})], 
                style={'margin-left':'4%','margin-right':'4%','margin-bottom':'0px',
                }),
        #html.Hr(style={'float':'left','width':'1900px','border-top':'3px solid #bbb'}),
        
        html.H6("Select the Policy Measure : ",style={'float':'left','margin-top':'15px','margin-bottom':'10px',
                    'margin-left':'10%',
                    'height': '30px', 'width': '40%','text-align':'right',
                    'font-family':'Comic Sans MS'}),
        dcc.Dropdown(id='GovtRestriction',
                               options=[{'label': x, 'value': x} for x in DataSet1.sort_values('GovtRestriction')
                               ['GovtRestriction'].unique()], value='School closing', clearable=True, searchable=True,
                               placeholder='Choose restriction...', style={'float':'left',
                               'margin-top':'10px','margin-bottom':'10px',
                               'margin-left':'1%',
                               'height': '40px', 'width': '40%'})
            ], style={'background-color':'white', 'float':'left', 'margin-left':'4%','margin-right':'4%', 'width':'92%',
            'height':'150px'}),
    html.Hr(style={'float':'left','margin-top':'5px','margin-left':'4%','width':'92%','border-top':'3px solid #bbb'}),
    html.H1("Policy Measures", className='twelve columns', style={'textAlign': 'center',
                'height':'50px',
                'color':'white',
                'font-size':'30px',
                'margin-left':'5%',
                'width':'90%',
                'background-color':'#609af0',
                'margin-bottom':'0px',
                'font-family':'Comic Sans MS'}),
    html.Div([
        dcc.Graph(id='line_graph1'),
    ],
        style={'float':'left','background-color':'white','height':'400px', 'width':'50%',
              'margin-bottom':'2%'}),
    html.Div([dcc.Graph(id='bar_graph_mean'),
              #html.Label([''], style={'font-weight': 'bold', "text-align": "left"}),
              ],
        style={'float':'left','background-color':'white','height':'400px', 'width':'50%',
              'margin-bottom':'2%'}),
    ###############
    #html.Hr(style={'float':'left','margin-top':'30px','margin-left':'4%','width':'92%','border-top':'3px solid #bbb'}),
    html.H1("Impact of Policy Measures", className='twelve columns', style={'textAlign': 'center',
                'margin-top':'30px',
                'height':'50px',
                'margin-left':'5%',
                'color':'white',
                'width':'90%',
                'font-size':'30px',
                'background-color':'#609af0',
                'margin-bottom':'0px',
                'font-family':'Comic Sans MS'}),
    dcc.RadioItems(id='graphType',
                     options=[{'label': 'Bar Graph', 'value': 'B'},
                              {'label': 'Line Graph', 'value': 'L'}],
                     value='L', labelStyle={'display': 'inline-block'},
                     style={'float':'left', 'margin-left':'550px',
                     'margin-top':'10px',
                     'background-color':'#dbe9ff',
                     'height': '30px',
                     'width':'190px'
                     }),
    ###############
    html.Div([
        dcc.Graph(id='bar_graph_deaths'),
    ],
        style={'float':'left','background-color':'white','height':'300px', 'width':'50%',
              'margin-bottom':'2%'}),
    html.Div([dcc.Graph(id='bar_graph_cases'),
              #html.Label([''], style={'font-weight': 'bold', "text-align": "left"}),
              ],
        style={'float':'left','background-color':'white','height':'300px', 'width':'50%',
              'margin-bottom':'2%'})
    ],
    style={'float':'left','box-shadow':'9px 9px 5px #888888','background-color':'white','height':'1300px',
    'margin-left':'5%','margin-right':'5%','width':'90%',
                'max-width':'90%'}),          
    ##Comparison Graphs##
    html.Div(className='twelve columns', style={'height':'10px'}),
    ##Milestone Comparison##
     html.Div([
        html.Div([
        html.H1("",style={'textAlign': 'center',
                'height':'10px',
                'background-color':'white',
                }),  
    html.Div([
        html.H1("Comparison of Important Policy Milestones with Germany", className='twelve columns', style={'textAlign': 'center',
                'height':'30px',
                'font-size':'30px',
                'background-color':'white',
                'margin-bottom':'0px',
                'font-family':'Comic Sans MS'})], 
                style={'margin-left':'4%','margin-right':'4%','margin-bottom':'0px',
                }),
        #html.Hr(style={'float':'left','width':'1900px','border-top':'3px solid #bbb'}),
            ], style={'background-color':'white', 'float':'left', 'margin-left':'4%','margin-right':'4%', 'width':'92%',
            'height':'80px'}),
    html.Hr(style={'margin-top':'10px','margin-left':'4%','float':'left','width':'92%','border-top':'3px solid #bbb'}),
    html.Div([
        dcc.Tabs(id='data_table_tab', value='tab-1', children=[
            dcc.Tab(id='tab-1', value='tab-1', children=[
            dash_table.DataTable(
                id='other_countries_data_table',
                columns=[{"name": i, "id": i}
                        for i in data_table_visulaization_df.columns],
                # data=data_table_visulaization_df.to_dict('records'),
                page_size=10,  # we have less data in this example, so setting to 20
                # style_table={'height': '300px', 'overflowY': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(78, 149, 230)',
                    'fontWeight': 'bold',
                    'color': '#FFFFFF',
                    'border': '1px solid black'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(206, 220, 245)'
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
            ]),
            dcc.Tab(id='tab-2', value='tab-2', children=[
            dash_table.DataTable(
                id='germany_data_table',
                columns=[{"name": i, "id": i}
                        for i in data_table_visulaization_df.columns],
                # data=data_table_visulaization_df.to_dict('records'),
                page_size=10,  # we have less data in this example, so setting to 20
                # style_table={'height': '300px', 'overflowY': 'auto'},
                style_header={
                    'backgroundColor': 'rgb(255, 79, 70)',
                    'fontWeight': 'bold',
                    'color': '#FFFFFF',
                    'border': '1px solid black'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(255, 185, 180)'
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
            ])            
        ])

    ],style={'height':'500px','margin-left':'4%','float':'left','width':'92%','max-width':'92%','background-color':'white'}),     
    ], className='eleven columns', style={'float':'left','box-shadow':'9px 9px 5px #888888','background-color':'white','height':'650px',
    'margin-left':'5%','margin-right':'5%','width':'90%',
    'max-width':'90%'}),  

    html.Div(className='twelve columns', style={'height':'100px'})

    ])
    ##Milestone Comparison##
# ----------------


@app.callback(
    [Output('line_graph', 'figure'),
     Output('bar_graph', 'figure')],
    [Input('country', 'value'),
     Input('slider_date', 'value')])
def build_graph(country_input, input_date_range):
    # Filtering the results based on input date range
    df_merged_filtered = dh.handle_updated_dates(df_merged, 'date', input_date_range, number_date_range_dict)

    df_per_country = df_merged_filtered[(df_merged_filtered['country'] == country_input)]
    df_per_country = df_per_country.rename({'total_cases': 'total_cases_' + country_input,
                                            'total_deaths': 'total_deaths_' + country_input,
                                            'total_recovery': 'total_recovery_' + country_input,
                                            'total_tests': 'total_tests_' + country_input}, axis=1)
    df_germany = df_merged_filtered[(df_merged_filtered['country'] == "Germany")]
    df_germany = df_germany.rename({'total_cases': 'total_cases_Germany',
                                    'total_deaths': 'total_deaths_Germany',
                                    'total_recovery': 'total_recovery_Germany',
                                    'total_tests': 'total_tests_Germany'}, axis=1)
    df_merge = pd.merge(df_germany, df_per_country, on='date')
    # print(df_merge.to_string())
    df_merge = pd.DataFrame(df_merge)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_cases_Germany"], name="Total affected Germany"))
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_deaths_Germany"], name="Total death Germany"))
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_recovery_Germany"], name="Total recovered Germany"))
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_deaths_" + country_input],
                             name="Total affected " + country_input))
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_deaths_" + country_input],
                             name="Total death " + country_input))
    fig.add_trace(go.Scatter(x=df_merge['date'], y=df_merge["total_deaths_" + country_input],
                             name="Total recovered " + country_input))

    fig.update_layout(title_text='Comparing COVID cases of ' + country_input + ' against Germany',
                      title=dict(font=dict(size=20)), xaxis_title='Date', yaxis_title='Cases')

    fig_bar_graph = go.Figure(data=[
        go.Bar(name='Total tests in Germany', x=df_merge['date'], y=df_merge['total_tests_Germany'],
               marker_color='crimson'),
        go.Bar(name='Total tests in ' + country_input, x=df_merge['date'], y=df_merge['total_tests_' + country_input],
               marker_color='rgb(26, 118, 255)')
    ])
    fig_bar_graph.update_layout(title_text='Comparing COVID tests of ' + country_input + ' against Germany',
                                title=dict(font=dict(size=20)), xaxis_title='Date', yaxis_title='Cases')
    return fig, fig_bar_graph

@app.callback(
    [Output('bar_graph_cases', 'figure'),
     Output('bar_graph_deaths', 'figure')],
    [Input('country', 'value'),
     Input('slider_date', 'value'),Input('graphType','value')])
def build_bargraph(country_input, input_date_range,gtype):
    # Filtering the results based on input date range
    df_merged_filtered = dh.handle_updated_dates(df_merged, 'date', input_date_range, number_date_range_dict)

    df_per_country1 = df_merged_filtered[(df_merged_filtered['country'] == country_input)]
    df_per_country1 = df_per_country1.rename(
        {'new_cases': 'New cases ' + country_input, 'new_deaths': 'New deaths ' + country_input}, axis=1)
    df_germany1 = df_merged_filtered[(df_merged_filtered['country'] == "Germany")]
    df_germany1 = df_germany1.rename({'new_cases': 'New cases Germany', 'new_deaths': 'New deaths Germany'}, axis=1)
    df_merge1 = pd.merge(df_germany1, df_per_country1, on='date')
    # print(df_merge1)

    df_merge1 = pd.DataFrame(df_merge1)

    #print(df_merge1.info())
    if gtype == "B":
        fig = go.Figure(data=[
        go.Bar(name='New cases in Germany', x=df_merge1['date'], y=df_merge1['New cases Germany']),
        go.Bar(name='New cases in ' + country_input, x=df_merge1['date'], y=df_merge1['New cases ' + country_input])
    ])
        fig.update_layout(title_text='Comparing new cases in ' + country_input + ' against Germany',
                      xaxis_title='Date', yaxis_title='Cases')
        fig1 = go.Figure(data=[
        go.Bar(name='New deaths in Germany', x=df_merge1['date'], y=df_merge1['New deaths Germany']),
        go.Bar(name='New deaths in ' + country_input, x=df_merge1['date'], y=df_merge1['New deaths ' + country_input])
    ])
        fig1.update_layout(title_text='Comparing new deaths in ' + country_input + ' against Germany',
                       xaxis_title='Date', yaxis_title='Cases')

        return fig, fig1
    else:
        fig = px.line(df_merge1,x=df_merge1['date'],y=['New cases Germany','New cases ' + country_input],title='Comparing new cases of '+country_input+' against Germany')
        fig1 = px.line(df_merge1, x=df_merge1['date'], y=['New deaths Germany', 'New deaths ' + country_input],
                      title='Comparing  new deaths of ' + country_input + ' against Germany')
        return fig,fig1


# Items from DataSet1 and DataSet2
@app.callback(
    Output('line_graph1', 'figure'),
    [Input('country', 'value'),
    Input("GovtRestriction", "value"),
    Input('slider_date', 'value')])
def build_graph1(country_input, govt_rest, input_date_range):

    filtered_Dataset1 = dh.handle_updated_dates(DataSet1, 'date', input_date_range, number_date_range_dict)
    German_data = filtered_Dataset1[(filtered_Dataset1['CountryName'] == "Germany")]
    Country_data = filtered_Dataset1[(filtered_Dataset1['CountryName'] == country_input)]
    German_data = German_data.rename(
        {'C1_School closing': 'School Closing Germany', 'C2_Workplace closing': 'WorkPlace Closing Germany',
         'C6_Stay at home requirements': 'StayHome Restriction Germany',
         'C4_Restrictions on gatherings': 'Gather Restriction Germany',
         'C5_Close public transport': 'Transport Restriction Germany',
         'C8_International travel controls': 'International Travel Restriction Germany',
         'retail_and_recreation_percent_change_from_baseline': 'Retail Restriction Germany',
         'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery Pharmacy Restriction Germany',
         'parks_percent_change_from_baseline': 'Park Restriction Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'School Closing ' + country_input,
                                        'C2_Workplace closing': 'WorkPlace Closing ' + country_input,
                                        'C6_Stay at home requirements': 'StayHome Restriction ' + country_input,
                                        'C4_Restrictions on gatherings': 'Gather Restriction ' + country_input,
                                        'C5_Close public transport': 'Transport Restriction ' + country_input,
                                        'C8_International travel controls': 'International Travel Restriction ' + country_input,
                                        'retail_and_recreation_percent_change_from_baseline': 'Retail Restriction ' + country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery Pharmacy Restriction ' + country_input,
                                        'parks_percent_change_from_baseline': 'Park Restriction ' + country_input},
                                       axis=1)
    df_merge = pd.merge(German_data, Country_data, on='date')
    # print(df_merge2['date'])
    new_df = pd.DataFrame(df_merge)
    # new_df2 = pd.DataFrame(df_merge2)
    df_1 = pd.DataFrame(new_df)
    # df_2 = pd.DataFrame(new_df2)
    if govt_rest == 'School closing':
        fig = drawLinegraph(df_1, 'School Closing ', country_input)
    elif govt_rest == 'Workplace closing':
        fig = drawLinegraph(df_1, 'WorkPlace Closing ', country_input)
    elif govt_rest == 'Stay at home requirements':
        fig = drawLinegraph(df_1, 'StayHome Restriction ', country_input)
    elif govt_rest == 'Restrictions on gatherings':
        fig = drawLinegraph(df_1, 'Gather Restriction ', country_input)
    elif govt_rest == 'Close public transport':
        fig = drawLinegraph(df_1, 'Transport Restriction ', country_input)
    elif govt_rest == 'International travel controls':
        fig = drawLinegraph(df_1, 'International Travel Restriction ', country_input)
    elif govt_rest == 'Restriction on Retail':
        fig = drawLinegraph(df_1, 'Retail Restriction ', country_input)
    elif govt_rest == "Restriction on pharmacy":
        fig = drawLinegraph(df_1, 'Grocery Pharmacy Restriction ', country_input)
    elif govt_rest == "Restriction on park":
        fig = drawLinegraph(df_1, 'Park Restriction ', country_input)
    return fig


def drawLinegraph(Dframe, x, country):
    b = x + 'Germany'
    c = x + country
    fig = px.line(Dframe, x='date',
                  y=[b, c],
                  #height=450, width=600
                  )
    fig.update_layout(title_text='Comparing ' + x + ' of ' + country + ' against Germany')
    return fig


@app.callback(
    Output('bar_graph_mean', 'figure'),
    [Input('country', 'value'),
    Input("GovtRestriction", "value"),
    Input('slider_date', 'value')],
)
def build_graph_mean(country_input, govt_rest, input_date_range):

    filtered_Dataset1 = dh.handle_updated_dates(DataSet1, 'date', input_date_range, number_date_range_dict)
    German_data = filtered_Dataset1[(filtered_Dataset1['CountryName'] == "Germany")]
    Country_data = filtered_Dataset1[(filtered_Dataset1['CountryName'] == country_input)]
    German_data = German_data.rename(
        {'C1_School closing': 'School Closing Germany', 'C2_Workplace closing': 'WorkPlace Closing Germany',
         'C6_Stay at home requirements': 'StayHome Restriction Germany',
         'C4_Restrictions on gatherings': 'Gather Restriction Germany',
         'C5_Close public transport': 'Transport Restriction Germany',
         'C8_International travel controls': 'International Travel Restriction Germany',
         'retail_and_recreation_percent_change_from_baseline': 'Retail Restriction Germany',
         'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery Pharmacy Restriction Germany',
         'parks_percent_change_from_baseline': 'Park Restriction Germany'}, axis=1)
    Country_data = Country_data.rename({'C1_School closing': 'School Closing ' + country_input,
                                        'C2_Workplace closing': 'WorkPlace Closing ' + country_input,
                                        'C6_Stay at home requirements': 'StayHome Restriction ' + country_input,
                                        'C4_Restrictions on gatherings': 'Gather Restriction ' + country_input,
                                        'C5_Close public transport': 'Transport Restriction ' + country_input,
                                        'C8_International travel controls': 'International Travel Restriction ' + country_input,
                                        'retail_and_recreation_percent_change_from_baseline': 'Retail Restriction ' + country_input,
                                        'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery Pharmacy Restriction ' + country_input,
                                        'parks_percent_change_from_baseline': 'Park Restriction ' + country_input},
                                       axis=1)
    df_merge_mean = pd.merge(German_data, Country_data, on='date')
    df_merge_mean['meanGermany'] = df_merge_mean['School Closing Germany'].div(9, axis=0) + df_merge_mean[
        'WorkPlace Closing Germany'].div(9, axis=0) + df_merge_mean['StayHome Restriction Germany'].div(9, axis=0) + \
                                   df_merge_mean[
                                       'Gather Restriction Germany'].div(9, axis=0) + df_merge_mean[
                                       'Transport Restriction Germany'].div(9, axis=0) + df_merge_mean[
                                       'International Travel Restriction Germany'].div(9, axis=0) + df_merge_mean[
                                       'Retail Restriction Germany'].div(9, axis=0) + df_merge_mean[
                                       'Grocery Pharmacy Restriction Germany'].div(9, axis=0) + df_merge_mean[
                                       'Park Restriction Germany'].div(9, axis=0)
    df_merge_mean['meanCountry'] = df_merge_mean['School Closing ' + country_input].div(9, axis=0) + df_merge_mean[
        'WorkPlace Closing ' + country_input].div(9, axis=0) + df_merge_mean['StayHome Restriction ' + country_input].div(
        9, axis=0) + df_merge_mean[
                                       'Gather Restriction ' + country_input].div(9, axis=0) + df_merge_mean[
                                       'Transport Restriction ' + country_input].div(9, axis=0) + df_merge_mean[
                                       'International Travel Restriction ' + country_input].div(9, axis=0) + \
                                   df_merge_mean[
                                       'Retail Restriction ' + country_input].div(9, axis=0) + df_merge_mean[
                                       'Grocery Pharmacy Restriction ' + country_input].div(9, axis=0) + df_merge_mean[
                                       'Park Restriction ' + country_input].div(9, axis=0)
    df_merge_mean['meanGermany'] = df_merge_mean['meanGermany'].fillna(0)
    df_merge_mean['meanCountry'] = df_merge_mean['meanCountry'].fillna(0)

    df_merge_mean = df_merge_mean.rename(
        {'meanGermany': 'Overall Restriction Germany', 'meanCountry': 'Overall Restriction ' + country_input}, axis=1)

    new_df_mean = pd.DataFrame(df_merge_mean)
    df_1_mean = pd.DataFrame(new_df_mean)

    fig = px.line(df_1_mean, x='date', y=['Overall Restriction Germany', 'Overall Restriction '+country_input])
    fig.update_layout(title_text='MEAN of all Policy Measures')
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
                            projection="equirectangular", color_continuous_scale="Blues",
                            title='Total COVID-19 Cases Across Europe')  # , template='plotly_dark')

    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig_map


@app.callback(
    [Output('other_countries_data_table', 'data'),
     Output('other_countries_data_table', 'tooltip_data'),
     Output('tab-1', 'label')],
    [Input('country', 'value'),
     Input('slider_date', 'value'),
     Input('data_table_tab', 'value')])
def generate_datatable_countries(country_input, input_date_range, tab_id):

    label = country_input

    data_per_country_df = data_table_visulaization_df[(data_table_visulaization_df['COUNTRY'] == country_input)]

    data_per_country_df = dh.handle_updated_dates(data_per_country_df, 'DATE_IMPLEMENTED', input_date_range,
                                                  number_date_range_dict)
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in data_per_country_df.to_dict('rows')
    ]
    return (data_per_country_df.to_dict('records'), tooltip_data, label)

@app.callback(
    [Output('germany_data_table', 'data'),
     Output('germany_data_table', 'tooltip_data'),
     Output('tab-2', 'label')],
    [Input('slider_date', 'value'),
     Input('data_table_tab', 'value')])
def generate_datatable_germany(input_date_range, tab_id):
    
    country_input = "Germany"
    label = country_input

    data_table_germany = data_table_visulaization_df[(data_table_visulaization_df['COUNTRY'] == country_input)]
    tooltip_data = []

    # Displaying only Germany data in Tab2 
    if tab_id == 'tab-2':
    
        data_table_germany = dh.handle_updated_dates(data_table_germany, 'DATE_IMPLEMENTED', input_date_range,
                                                    number_date_range_dict)
        tooltip_data = [
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in data_table_germany.to_dict('rows')
        ]
    return (data_table_germany.to_dict('records'), tooltip_data, label)


if __name__ == '__main__':
    app.run_server(debug=True)