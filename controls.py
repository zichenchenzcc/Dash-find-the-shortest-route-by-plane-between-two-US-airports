import pandas as pd
import os
import numpy as np
import math

CITY_DATA = 'largest_cities.csv'
AIRPORT_DATA = 'airport.csv'
AIRLINES_DATA = 'airlines.csv'
ROUTES_DATA = 'routes.csv'

# load dataframe for cities
#
city_df = pd.read_csv(CITY_DATA)
# load dataframe for airports
#
airport_df = pd.read_csv(AIRPORT_DATA, header=None)
airport_df.columns = ['Airport_id', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude',
                      'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone',
                      'type', 'Source']
airport_df['Airport_id'] = pd.to_numeric(airport_df['Airport_id'])
airport_df.drop(airport_df[airport_df['Airport_id'] == r'\N'].index, inplace=True)
airport_df.drop(airport_df[airport_df['Country'] != 'United States'].index, inplace=True)
city_names = list(city_df['City'])
airport_df = airport_df[airport_df['City'].isin(city_names)]

# load dataframe for routes
#
routes_df = pd.read_csv(ROUTES_DATA, header=None)
routes_df.columns = ['Airline', 'Airline_id', 'Source airport', 'Source_airport_id',
                     'Destination airport', 'Destination_airport_id', 'Codeshare', 'Stops',
                     'Equipment']
routes_df.drop(routes_df[routes_df['Airline_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Source_airport_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Destination_airport_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Stops'] != 0].index, inplace=True)
routes_df['Airline_id'] = pd.to_numeric(routes_df['Airline_id'])
routes_df['Source_airport_id'] = pd.to_numeric(routes_df['Source_airport_id'])
routes_df['Destination_airport_id'] = pd.to_numeric(routes_df['Destination_airport_id'])
airport_ids = list(airport_df['Airport_id'])
routes_df = routes_df[routes_df['Source_airport_id'].isin(airport_ids)]
routes_df = routes_df[routes_df['Destination_airport_id'].isin(airport_ids)]

# load dataframe for airlines
#
airlines_df = pd.read_csv(AIRLINES_DATA, header=None)
airlines_df.columns = ['Airline_id', 'Name', 'Alias', 'IATA', 'ICAO', 'Callsign',
                       'Country', 'Active']
airlines_df.drop(airlines_df[airlines_df['Airline_id'] == r'\N'].index, inplace=True)
airlines_df['Airline_id'] = pd.to_numeric(airlines_df['Airline_id'])
airlines_df.drop(airlines_df[airlines_df['Active'] != 'Y'].index, inplace=True)
airlines_df.drop(airlines_df[airlines_df['Country'] != 'United States'].index, inplace=True)
routes_df = routes_df.drop(['Airline','Source airport','Destination airport','Codeshare','Stops','Equipment'],axis = 1)
dict_airport = {list(airport_df['Airport_id'])[i]:list(airport_df['Name'])[i] for i in range(airport_df.shape[0])}
dict_airline = {list(airlines_df['Airline_id'])[i]:list(airlines_df['Name'])[i] for i in range(airlines_df.shape[0])}
airportid_city = {list(airport_df['Airport_id'])[i]:list(airport_df['City'])[i] for i in range(airport_df.shape[0])}
routes_df['Source Airport'] = routes_df['Source_airport_id'].map(dict_airport)
routes_df['Destination Airport'] = routes_df['Destination_airport_id'].map(dict_airport)
routes_df['Source City'] = routes_df['Source_airport_id'].map(airportid_city)
routes_df['Destination City'] = routes_df['Destination_airport_id'].map(airportid_city)
routes_df['Airline'] = routes_df['Airline_id'].map(dict_airline)
airport_df = airport_df.drop(['IATA','ICAO','Altitude','Timezone','DST','Tz database time zone','type','Source'],axis = 1)
city_population = {list(city_df['City'])[i]:list(city_df['Population'])[i] for i in range(city_df.shape[0])}
airport_df['Population'] = airport_df['City'].map(city_population)
cols = list(routes_df)
cols.insert(7,cols.pop(cols.index('Airline_id')))
cols.insert(1,cols.pop(cols.index('Source City')))
cols.insert(1,cols.pop(cols.index('Source Airport')))
routes_df = routes_df.loc[:,cols]
airline_list = list(airlines_df['Airline_id'])
routes_df = routes_df.loc[routes_df['Airline_id'].isin(airline_list)]
available_airport = sorted(list(set(routes_df['Source Airport'])))
airport_df = airport_df.loc[airport_df['Name'].isin(available_airport)]
airlines_df = airlines_df.drop(['Alias','IATA','ICAO','Callsign','Country','Active'],axis = 1)
available_city = sorted(list(set(airport_df['City'])))
city_df = city_df.loc[city_df['City'].isin(available_city)]
city_names = list(city_df['City'])

#Calculate the distance between two given airports
def distance(departure_airport, arrival_airport, df1):
    departure_latitude  = math.radians(list(df1[df1.Name == departure_airport]['Latitude'] )[0])
    departure_longitude = math.radians(list(df1[df1.Name == departure_airport]['Longitude'])[0])
    arrival_latitude    = math.radians(list(df1[df1.Name == arrival_airport  ]['Latitude'] )[0])
    arrival_longitude   = math.radians(list(df1[df1.Name == arrival_airport  ]['Longitude'])[0])
    a = math.sin(np.abs(departure_latitude - arrival_latitude)/2)**2 + math.cos(departure_latitude)*math.cos(arrival_latitude)*math.sin(np.abs(departure_longitude - arrival_longitude)/2)**2
    c = 2 * math.atan2(a**0.5, (1-a)**0.5)
    R = 6399.594
    d = R*c 
    return d

# Find out the shortest path between two airports (can be with/without direct airline)
def dijkstra(cities, distances, start_city, destination_city):
    start_city_index = airport_map[start_city]
    destination_city_index = airport_map[destination_city]
    unvisited_cities = {city: None for city in cities}
    visited_cities = {}
    current_city = start_city_index
    current_distance = 0
    unvisited_cities[current_city] = current_distance
    path = {city: start_city_index for city in cities}
    while True:
        for neighbor, distance in distances[current_city].items():            
            if neighbor not in unvisited_cities:
                continue
            new_distance = current_distance + distance
            if unvisited_cities[neighbor] is None or new_distance < unvisited_cities[neighbor]:
                unvisited_cities[neighbor] = new_distance
                path[neighbor] = np.append(np.array(path[current_city]),neighbor)                
        visited_cities[current_city] = current_distance
        del unvisited_cities[current_city]
        if not unvisited_cities:
            break
        candidates = [city for city in unvisited_cities.items() if city[1]]
        current_city, current_distance = sorted(candidates, key=lambda x: x[1], reverse=False)[0]
    for city_index, Distance in visited_cities.items():
        if city_index == destination_city_index:
            distance = Distance
            path = path[destination_city_index]
    path_airport = []
    path_city = []
    for i in path:
        path_airport.append(airport_mapping[i])
        path_city.append(list(airport_df['City'])[i])        
    path_distance = []
    available_airline = {}
    for i in range(len(path)-1):
        path_distance.append(round(distances[path[i]][path[i + 1]],4))
        available_airline[i] = list(routes_df.loc[routes_df['Source_airport_id'] == path[i]].loc[routes_df['Destination_airport_id'] == path[i + 1]]['Airline'])
    return distance, path, path_airport, path_city, path_distance, available_airline

# Get all the combination of each element in two lists
def comb(list1,list2):
    combine = []
    for i in range(len(list1)):
        for j in range(len(list2)):
            combine.append(str(list1[i])+'---'+str(list2[j]))
    return combine

airport_list = sorted(list(airport_df['Name']))
airport_map = {}
for i in range(len(airport_list)):
    airport_map[airport_list[i]] = i
routes_df['Source_airport_id'] = routes_df['Source Airport'].map(airport_map)
routes_df['Destination_airport_id'] = routes_df['Destination Airport'].map(airport_map)
new_routes_df = routes_df.drop(['Airline','Airline_id'],axis = 1)
new_routes_df = new_routes_df.drop_duplicates()
airport_mapping = {}
for i in range(len(airport_list)):
    airport_mapping[i] = airport_list[i]
airport_df.sort_values(by = 'Name',inplace=True)
airport_df['Airport_id'] = airport_df['Name'].map(airport_map)
matrix = np.zeros([airport_df.shape[0],airport_df.shape[0]])
for i in range(new_routes_df.shape[0]):
    matrix[new_routes_df.iloc[i]['Source_airport_id'],new_routes_df.iloc[i]['Destination_airport_id']] = 1
distances = {}
dictionary_1 = {}
for i in range(matrix.shape[0]):
    for j in np.delete(np.arange(matrix.shape[1]),i):
        if matrix[i,j] == 1:
            dictionary_1[j] = distance(airport_df.iloc[i]['Name'], airport_df.iloc[j]['Name'], airport_df)
    distances[i] = dictionary_1
    dictionary_1 = {}    
del airport_list, dictionary_1, i, j, matrix, new_routes_df
cities = airport_mapping.keys()
airport_df['Latitude'] = round(airport_df['Latitude'],2)
airport_df['Longitude'] = round(airport_df['Longitude'],2)
city_name= sorted(list(city_df['City']))
airport_line = {}
for i in city_df['City']:
    city_name.remove(i)
    airport_line[i] = city_name
    city_name= sorted(list(city_df['City']))
    
airport_dict = {}
for j in city_name:
    airport_list = []
    for i in range(len(airport_df['City'])):
        if list(airport_df['City'])[i] == j:
            airport_list.append(list(airport_df['Name'])[i])
    airport_dict[j] = airport_list
