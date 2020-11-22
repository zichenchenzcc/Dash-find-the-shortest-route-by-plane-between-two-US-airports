import pandas as pd
import os
os.chdir("C:\\Users\\czc\\Desktop\\Python2")
CITY_DATA = '50_largest_cities.csv'
AIRPORT_DATA = 'airport.csv'
AIRLINES_DATA = 'airlines.csv'
ROUTES_DATA = 'routes.csv'

TRACE = False

# load dataframe for cities
#
if TRACE:
    print('CITIES')
city_df = pd.read_csv(CITY_DATA)
if TRACE:
    print(city_df.shape)
    print(city_df)

# load dataframe for airports
#
if TRACE:
    print('AIRPORTS')
airport_df = pd.read_csv(AIRPORT_DATA, header=None)
airport_df.columns = ['Airport_id', 'Name', 'City', 'Country', 'IATA', 'ICAO', 'Latitude',
                      'Longitude', 'Altitude', 'Timezone', 'DST', 'Tz database time zone',
                      'type', 'Source']
if TRACE:
    print(1, airport_df.shape)

airport_df['Airport_id'] = pd.to_numeric(airport_df['Airport_id'])
airport_df.drop(airport_df[airport_df['Airport_id'] == r'\N'].index, inplace=True)
airport_df.drop(airport_df[airport_df['Country'] != 'United States'].index, inplace=True)
if TRACE:
    print(2, airport_df.shape)

city_names = list(city_df['City'])
airport_df = airport_df[airport_df['City'].isin(city_names)]
if TRACE:
    print(3, airport_df.shape)
    print(airport_df)

# load dataframe for routes
#
if TRACE:
    print('ROUTES')
routes_df = pd.read_csv(ROUTES_DATA, header=None)
routes_df.columns = ['Airline', 'Airline_id', 'Source airport', 'Source_airport_id',
                     'Destination airport', 'Destination_airport_id', 'Codeshare', 'Stops',
                     'Equipment']
if TRACE:
    print(1, routes_df.shape)

routes_df.drop(routes_df[routes_df['Airline_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Source_airport_id'] == r'\N'].index, inplace=True)
routes_df.drop(routes_df[routes_df['Destination_airport_id'] == r'\N'].index, inplace=True)
if TRACE:
    print(2, routes_df.shape)

routes_df.drop(routes_df[routes_df['Stops'] != 0].index, inplace=True)
if TRACE:
    print(3, routes_df.shape)

routes_df['Airline_id'] = pd.to_numeric(routes_df['Airline_id'])
routes_df['Source_airport_id'] = pd.to_numeric(routes_df['Source_airport_id'])
routes_df['Destination_airport_id'] = pd.to_numeric(routes_df['Destination_airport_id'])

airport_ids = list(airport_df['Airport_id'])
routes_df = routes_df[routes_df['Source_airport_id'].isin(airport_ids)]
routes_df = routes_df[routes_df['Destination_airport_id'].isin(airport_ids)]

if TRACE:
    print(4, routes_df.shape)
    print(routes_df)

# load dataframe for airlines
#
if TRACE:
    print('AIRLINES')
airlines_df = pd.read_csv(AIRLINES_DATA, header=None)
airlines_df.columns = ['Airline_id', 'Name', 'Alias', 'IATA', 'ICAO', 'Callsign',
                       'Country', 'Active']
if TRACE:
    print(1, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Airline_id'] == r'\N'].index, inplace=True)
airlines_df['Airline_id'] = pd.to_numeric(airlines_df['Airline_id'])
if TRACE:
    print(2, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Active'] != 'Y'].index, inplace=True)
if TRACE:
    print(3, airlines_df.shape)
airlines_df.drop(airlines_df[airlines_df['Country'] != 'United States'].index, inplace=True)
if TRACE:
    print(3, airlines_df.shape)
    print(airlines_df)

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
if __name__ == '__main__':
    pass

