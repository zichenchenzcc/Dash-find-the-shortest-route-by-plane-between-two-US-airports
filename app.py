import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from controls import city_df, airport_df, city_name, airport_dict, dijkstra, cities, distances, comb
import plotly.graph_objects as go
from functools import reduce
from dash.dependencies import Input, Output, State

app = dash.Dash(external_stylesheets=[dbc.themes.SANDSTONE])

mapbox_access_token = \
    "pk." \
    "eyJ1IjoiZmx5aW5nZWxlcGhhbnQiLCJhIjoiY2tobmwyeHNkMG03djJ4bWsybGt1N3Y1bCJ9.Baw5PuQnRAvTtSv7yghPgw"

layout = dict(
    autosize=True,
    height = 600,
    margin=dict(l=10, r=10, b=0, t=40),
    hovermode="closest",
    title={
        'text': "Map",
        'y':0.98,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    title_font_size=30,
    title_font_color="DodgerBlue",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-98.5795, lat=39.8283),
        zoom=3.5,
    ),
)

controls = dbc.Card(
    [
        dbc.FormGroup([
                dbc.Label("Start City"),
                dcc.Dropdown(options=[{"label": col, "value": col} for col in city_name],
                             id="start-city",)
                        ]),
        dbc.FormGroup([
                dbc.Label("Start Airport"),
                dcc.Dropdown(id="start-airport"),
                        ]),
        dbc.FormGroup([
                dbc.Label("Destination City"),
                dcc.Dropdown(id="destination-city"),
                        ]),
        dbc.FormGroup([
                dbc.Label("Destination Airport"),
                dcc.Dropdown(id="destination-airport"),
                        ]),
        html.Div(id="total-distance"),
        html.Br(),
        html.Div(id="path"),
        html.Br(),
        dbc.FormGroup([
                dbc.Label("Available Airline"),
                dcc.Dropdown(id="available-airline"),
                        ]),
        
    ],
    body=True,
)

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.P("Kartemap - An Airport Network Analysis Application",style={'background-color': 'DodgerBlue','color': 'white','text-align':'center','font-size':'260%'}))),
        dbc.Row([dbc.Col(controls, lg=3),
                dbc.Col(dcc.Graph(id="map"), lg=9)],
                align="center")
    ],
    id="main-container",
    style={"display": "flex", "flex-direction": "column"},
    fluid=True
)

# Update map after inputing airport(s) 
# (markers for and traces between start city, all intermediate cities and destination city.)
@app.callback(
                Output(component_id='map',component_property='figure'),
                [Input(component_id='start-airport', component_property='value'),
                 Input(component_id='destination-airport', component_property='value')],
                 State('map','relayoutData')
            )   
def update_map(start_airport,destination_airport,l):
    if start_airport == None and destination_airport == None:
        traces = dict(type='scattermapbox',lon=airport_df['Longitude'],
                             lat=airport_df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=10,opacity=0.5))
        figure = go.Figure(data=traces,layout =layout)
    elif start_airport != None and destination_airport == None:
        traces = []
        for name,df in airport_df.groupby('Name'):
            if name == start_airport:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=25,opacity=0.95,symbol='airport'))
            else:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=10,opacity=0.5))
            traces.append(trace)
        figure = go.Figure(data=traces,layout =layout)
    elif start_airport == None and destination_airport != None:
        traces = []
        for name,df in airport_df.groupby('Name'):
            if name == destination_airport:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=25,opacity=0.95,symbol='embassy'))
            else:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=10,opacity=0.5))
            traces.append(trace) 
        figure = go.Figure(data=traces,layout =layout)
    else: 
        Distance, path, path_airport, path_city, path_distance, available_airline = dijkstra(cities, distances, start_airport, destination_airport)
        traces = []
        for name,df in airport_df.groupby('Name'):
            if name == start_airport:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=20,opacity=0.95,symbol='airport'))
            elif name == destination_airport:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=25,opacity=0.95,symbol='embassy'))
            elif name in path_airport[1:-1]:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             )
            else:
                trace = dict(type='scattermapbox',lon=df['Longitude'],
                             lat=df['Latitude'],text='City: '+str(list(airport_df['City'])[0]) + '<br>' +
                                                     'Airport: '+str(list(airport_df['Name'])[0]) + '<br>' +
                                                     'Population: '+str(list(airport_df['Population'])[0]),
                                                     showlegend=False,
                             marker=dict(size=10,opacity=0.5))
            traces.append(trace) 
        figure = go.Figure(data=traces,layout =layout)
        long=[]
        lati=[]
        text=[]
        symbol=['airport']
        for i in range(len(path_airport)):
            long.append(list(airport_df.loc[airport_df['Name']==path_airport[i],['Longitude']]['Longitude'])[0])
            lati.append(list(airport_df.loc[airport_df['Name']==path_airport[i],['Latitude']]['Latitude'])[0])
            text.append('Airport: '+str((path_airport[i])) + '<br>' +
                         'City: ' +str((list(airport_df.loc[airport_df['Name']==(path_airport[i]),['City']]['City'])[0])) + '<br>' +
                         'population: '+str((list(airport_df.loc[airport_df['Name']==(path_airport[i]),['Population']]['Population'])[0])))
            symbol.append('marker')
        symbol.remove('marker')
        symbol.remove('marker')
        symbol.append('embassy')
        figure.add_trace(go.Scattermapbox(
                         mode = "markers+lines",
                         lon = long, lat = lati,
                         text = text,
                         hoverinfo='text',
                         marker=dict(size=25,opacity=0.95,symbol=symbol),
                         line=dict(color="black"),
                         showlegend=False))
    return figure

# Return a list of available destination cities. Cannot choose the same as start city.
@app.callback(Output('destination-city','options'),Input('start-city','value'))
def except_original_city(start_city):
    city_name = sorted(list(city_df['City']))
    options=[{"label": col, "value": col} for col in city_name]
    for i in options:
        if i['label'] == start_city:
            i['disabled'] = True
    return options

# Return a list of available start cities. Cannot choose the same as destination city.
@app.callback(Output('start-city','options'),Input('destination-city','value'))
def except_destination_city(destination_city):
    city_name = sorted(list(city_df['City']))
    options=[{"label": col, "value": col} for col in city_name]
    for i in options:
        if i['label'] == destination_city:
            i['disabled'] = True
    return options

# Show all available airports for the chosen start city
@app.callback(Output('start-airport', 'options'),Input('start-city','value'))
def start_airport_options(selected_city):
    if selected_city !=None:
        options = [{'label': i, 'value': i} for i in airport_dict[selected_city]]
    else:
        options =[]
    return options

# Show all available airports for the chosen destination city
@app.callback(Output('destination-airport', 'options'),Input('destination-city','value'))
def destination_airport_options(selected_city):
    if selected_city !=None:
        options = [{'label': i, 'value': i} for i in airport_dict[selected_city]]
    else:
        options =[]
    return options

# Show the total distance, path and available airline combinations.
@app.callback([Output('total-distance', 'children'),
              Output('path', 'children'),
              Output('available-airline', 'options')],
              [Input('start-airport','value'),
               Input('destination-airport','value')])
def distance_path_airline_output(start_airport,destination_airport):
    if start_airport != None and destination_airport != None:
        Distance, path, path_airport, path_city, path_distance, available_airline = dijkstra(cities, distances, start_airport, destination_airport)
        path_comb = []
        for i in range(len(path_city)):
            path_comb.append([path_city[i]])
        path_combine = reduce(comb,path_comb)
        airline_comb = []
        for i in range(len(available_airline)):
            airline_comb.append(available_airline[i])
        airline_combine = reduce(comb,airline_comb)
        options=[{"label": col, "value": col} for col in airline_combine]
        return ('Distance:  '+str(round(Distance,3))+'km.'),('Path:  ',list(path_combine)[0]),options
    else:
        return 'Distance:  ','Path:  ',[]
# Main
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)