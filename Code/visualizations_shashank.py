import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Shashank Visualizations"

dfSchools = pd.read_csv('Policy.csv')
dfCountry = dfSchools[['CountryName','Date','C1_School_closing']]

colors = {
    'background': '#F0FFFF',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.H1("Shashank Visualizations",
            style = {
                'textAlign' : 'center',
                'color' : colors['text']
            }),
            html.Div([dcc.Graph(id='schoolLineGraph'),
              html.Label(['Choose country:'], style={'font-weight': 'bold', "text-align": "left"}),
              dcc.Dropdown(id='countrySchools',
                           options=[{'label': x, 'value': x} for x in dfCountry.sort_values('CountryName')['CountryName'].unique()],
                           placeholder='Choose Country...', style={'height': '30px', 'width': '200px'},)
              ], className='six columns')])

@app.callback(
    Output('schoolLineGraph', 'figure'),
    [Input('countrySchools', 'value')])
def schoolReopen(countrySchools):
    dfSchoolsForCountry = dfCountry[dfCountry.CountryName == countrySchools]
    figSchool = px.line(dfSchoolsForCountry, x="Date", y="C1_School_closing")
    return figSchool

if __name__ == '__main__':
    app.run_server(debug=True)