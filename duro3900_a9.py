#!/usr/bin/env python
# coding: utf-8

# In[27]:


import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Dataset
def create_worldcup_dataset():
    data = {
        'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
                 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
        'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 
                   'Brazil', 'England', 'Brazil', 'West Germany', 'Argentina', 
                   'Italy', 'Argentina', 'West Germany', 'Brazil', 'France', 
                   'Brazil', 'Italy', 'Spain', 'Germany', 'France', 'Argentina'],
        'Runner-up': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 
                      'Sweden', 'Czechoslovakia', 'West Germany', 'Italy', 'Netherlands', 
                      'Netherlands', 'West Germany', 'West Germany', 'Argentina', 
                      'Italy', 'Brazil', 'Germany', 'France', 'Netherlands', 
                      'Argentina', 'Croatia', 'France'],
        'Score': ['4-2', '2-1 (OT)', '4-2', '2-1', '3-2', '5-2', '3-1', '4-2 (OT)', 
                  '4-1', '2-1', '3-1 (OT)', '3-1', '3-2', '1-0', '0-0 (OT) (3-2 p)', 
                  '3-0', '2-0', '1-1 (OT) (5-3 p)', '1-0 (OT)', '1-0 (OT)', 
                  '4-2', '3-3 (OT) (4-2 p)'],
        'Venue': ['Montevideo', 'Rome', 'Paris', 'Rio de Janeiro', 'Bern', 'Solna', 
                  'Santiago', 'London', 'Mexico City', 'Munich', 'Buenos Aires', 
                  'Madrid', 'Mexico City', 'Rome', 'Pasadena', 'Saint-Denis', 
                  'Yokohama', 'Berlin', 'Johannesburg', 'Rio de Janeiro', 'Moscow', 'Lusail']
    }
    return pd.DataFrame(data)

# Create DataFrame
world_cup_df = create_worldcup_dataset()

# Country names, combine West Germany and Germany
world_cup_df['Winner'] = world_cup_df['Winner'].replace({'West Germany': 'Germany'})
world_cup_df['Runner-up'] = world_cup_df['Runner-up'].replace({'West Germany': 'Germany'})

# country-code mapping
country_codes = {
    'Argentina': 'ARG',
    'Brazil': 'BRA',
    'England': 'GBR',
    'France': 'FRA',
    'Germany': 'DEU',
    'Italy': 'ITA',
    'Netherlands': 'NLD',
    'Spain': 'ESP',
    'Uruguay': 'URY',
    'Czechoslovakia': 'CZE', 
    'Hungary': 'HUN',
    'Sweden': 'SWE',
    'Croatia': 'HRV'
}

# Prep data for map
def prepare_choropleth_data(df):
    # Count wins
    winners = df['Winner'].value_counts().reset_index()
    winners.columns = ['Country', 'Wins']
    winners['ISO'] = winners['Country'].map(country_codes)
    # Count runner-up
    runners_up = df['Runner-up'].value_counts().reset_index()
    runners_up.columns = ['Country', 'Runner-ups']
    runners_up['ISO'] = runners_up['Country'].map(country_codes)
    
    # Merge data
    merged = pd.merge(winners, runners_up, on=['Country', 'ISO'], how='outer').fillna(0)
    merged['Total Finals'] = merged['Wins'] + merged['Runner-ups']
    
    return merged

choropleth_data = prepare_choropleth_data(world_cup_df)
# Initialize Dash
app = dash.Dash(__name__)
server = app.server
# Define layout
app.layout = html.Div([
    html.H1("FIFA World Cup Winners and Runner-up", style={'textAlign': 'center'}),
    html.P("Note: West Germany and Germany are combined as 'Germany'", style={'textAlign': 'center', 'color': 'gray'}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='map-type-dropdown',
                options=[
                    {'label': 'World Cup Wins', 'value': 'Wins'},
                    {'label': 'Runner-up Appearances', 'value': 'Runner-ups'},
                    {'label': 'Total Finals Appearances', 'value': 'Total Finals'}
                ],
                value='Wins',
                clearable=False,
                style={'width': '100%'}
            ),
            dcc.Graph(id='world-map')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in world_cup_df['Year']],
                value=world_cup_df['Year'].max(),
                clearable=False,
                style={'width': '100%'}
            ),
            html.Div(id='year-details', style={'marginTop': '20px', 'padding': '10px', 'border': '1px solid #ddd'})
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in choropleth_data['Country']],
                value='Brazil',
                clearable=False,
                style={'width': '100%'}
            ),
            html.Div(id='country-stats', style={'marginTop': '20px', 'padding': '10px', 'border': '1px solid #ddd'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            html.H3("All World Cup Winners"),
            html.Ul([html.Li(country) for country in choropleth_data['Country']])
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'padding': '10px'})
    ], style={'marginTop': '20px'})
])

# choropleth map callback
@app.callback(
    Output('world-map', 'figure'),
    Input('map-type-dropdown', 'value')
)
def update_map(selected_stat):
    fig = px.choropleth(
        choropleth_data,
        locations="ISO",
        color=selected_stat,
        hover_name="Country",
        hover_data=["Wins", "Runner-ups"],
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"World Cup {selected_stat} by Country"
    )
    
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        coloraxis_colorbar=dict(title=selected_stat),
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
    )
    
    return fig

# callback for year
@app.callback(
    Output('year-details', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_details(selected_year):
    year_data = world_cup_df[world_cup_df['Year'] == selected_year].iloc[0]
    
    # original names in year details
    original_winner = 'West Germany' if (selected_year in [1954, 1974, 1990]) and (year_data['Winner'] == 'Germany') else year_data['Winner']
    original_runner = 'West Germany' if (selected_year in [1966, 1982, 1986]) and (year_data['Runner-up'] == 'Germany') else year_data['Runner-up']
    
    return [
        html.H3(f"World Cup {selected_year}"),
        html.P(f"Winner: {original_winner}"),
        html.P(f"Runner-up: {original_runner}"),
        html.P(f"Score: {year_data['Score']}"),
        html.P(f"Venue: {year_data['Venue']}")
    ]

# Callback for country
@app.callback(
    Output('country-stats', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_stats(selected_country):
    country_data = choropleth_data[choropleth_data['Country'] == selected_country].iloc[0]
    
    # Get all years the country won
    if selected_country == 'Germany':
        wins = world_cup_df[(world_cup_df['Winner'] == 'Germany') | 
                          (world_cup_df['Winner'] == 'West Germany')]['Year'].unique().tolist()
    else:
        wins = world_cup_df[world_cup_df['Winner'] == selected_country]['Year'].tolist()
    
    # Get all years the country was runner-up
    if selected_country == 'Germany':
        runners_up = world_cup_df[(world_cup_df['Runner-up'] == 'Germany') | 
                                (world_cup_df['Runner-up'] == 'West Germany')]['Year'].unique().tolist()
    else:
        runners_up = world_cup_df[world_cup_df['Runner-up'] == selected_country]['Year'].tolist()
    
    return [
        html.H3(f"{selected_country} World Cup History"),
        html.P(f"Total Wins: {int(country_data['Wins'])}"),
        html.P("Won in: " + ", ".join(map(str, sorted(wins))) if wins else "No wins"),
        html.P(f"Runner-up Appearances: {int(country_data['Runner-ups'])}"),
        html.P("Runner-up in: " + ", ".join(map(str, sorted(runners_up))) if runners_up else "No runner-up appearances")
    ]

if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:




