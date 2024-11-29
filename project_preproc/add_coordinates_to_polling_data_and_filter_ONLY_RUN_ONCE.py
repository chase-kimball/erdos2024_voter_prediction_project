import googlemaps
import pandas as pd
import geopandas as gpd
import numpy as np

polls = pd.read_csv('../project_data/chc/Polling_Places_IL_2016.csv')

polls =  polls[polls.Jurisdiction =='City of Chicago'].fillna(-1)

with open('../google_maps_api','r') as f:
    my_key = f.read().strip()
gmaps = googlemaps.Client(key=my_key)

lon = []
lat = []
for ii, row in polls.iterrows():
    if row['Address Line 1'] == -1:
        lon.append(-999)
        lat.append(-999)
        continue
        
        
    address = row['Address Line 1'] + ', Chicago, IL'
    geocode_result = gmaps.geocode(address)
    lon.append(geocode_result[0]['geometry']['location']['lng'])
    lat.append(geocode_result[0]['geometry']['location']['lat'])

polls['lon'] = lon
polls['lat'] = lat

polls.to_csv('../project_data/chc/Polling_Places_Chicago_2016.csv')