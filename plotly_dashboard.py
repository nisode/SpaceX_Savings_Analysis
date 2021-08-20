# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# download this in terminal
# wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
                                    html.Div([
                                        html.H2('Launch Location:', style={'margin-right': '2em'})
                                    ]),
                                    dcc.Dropdown(id='site-dropdown',
                                                 options=[
                                                     {'label':'All Sites','value':'all'},
                                                     {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                                                     {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'},
                                                     {'label':'KSC LC-39A','value':'KSC LC-39A'},
                                                     {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'}
                                                 ],
                                                 value='All Sites',
                                                 placeholder='Select a Launch Site Here',
                                                 searchable=True,
                                                 style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align': 'center'})
                                ], style={'display': 'flex'}),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div([
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000, value=[min_payload, max_payload],
                                                marks={k:k for k in range(0,11000,1000)})]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output


@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def pie_plot(value):
    if value == 'all':
        df = spacex_df[spacex_df['class'] == 1].groupby(spacex_df['Launch Site']).sum().reset_index()
        fig = px.pie(df, values='class', names='Launch Site', title='Successful Launches Across All Launch Sites',
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        df = spacex_df[spacex_df['Launch Site'] == value].groupby('class').size().reset_index()
        df = df.rename(columns={0: 'count'})
        fig = px.pie(df, values='count', names='class', title=value + ' Success Rate (blue=success)', color='class',
                     color_discrete_map={0:'darkred',1:'royalblue'})
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='payload-slider', component_property='value'),
               Input(component_id='site-dropdown', component_property='value')])
def scatter_plot(slide, dropdown):
    low, high = slide
    if dropdown == 'all':
        df = spacex_df
    else:
        df = spacex_df[spacex_df['Launch Site'] == dropdown]
    mask = (df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)
    s_df = df[mask].groupby(['Payload Mass (kg)','class','Booster Version Category']).size().reset_index()
    s_df = s_df.rename(columns={0:'count'})
    fig = px.scatter(s_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', size='count',
                     title='Payload Mass vs. Success vs. Booster Version Category')
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
