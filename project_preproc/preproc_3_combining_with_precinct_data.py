import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import centroid
import os
import shutil
from shapely import MultiPolygon, Polygon, wkt, intersection
import matplotlib.pyplot as plt
from geopy import distance
import pandas_geojson as pdg
import shapely
import googlemaps
from sklearn.model_selection import train_test_split


# We import various functions which we will need later to process our data. 
import reading_data
######## Only run this once! Adding coordinates to the polling center addresses

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

polls.to_csv('../project_data/processed_data/Polling_Places_Chicago_2016.csv')
###########################################################################


# Import the census data.




cen = gpd.read_file('../project_data/processed_data/Chicago_geocensus_data.geojson')


##################### Import the precinct data and combine with our other data sets ########################
precincts = reading_data.get_raw_precinct_gpd('../project_data/chc/ChicagoPrecincts2012_2022.csv')
precincts = reading_data.append_intersecting_simplex_data_to_precinct(precincts, '../project_data/chc/chc_death_simplices_by_death_in_dim_1.npy')
precincts = reading_data.append_polls_to_precinct(precincts, '../project_data/processed_data/Polling_Places_Chicago_2016.csv')
precincts = reading_data.add_census_indices(precincts,cen)



# We now append each census stat (scaled by things like total population) to `precincts`.
# This is done by finding the intersection of each precinct with each census tract, assuming 
# each census tract is of constant population density, and then getting a population-weighted
# average of each statistic across the tract intersections that make up each precinct

# These stats are scaled by total population
for stat in ['white_alone', 'black_alone', 'indigenous_alone', 'asian_alone',
       'pacific_islander_alone', 'other_alone', 'multiracial',
       'work_from_home', 'automobile_to_work', 'public_transit_to_work',
       'taxi_to_work', 'motorcycle_to_work', 'bike_to_work', 'walk_to_work',
       'other_to_work']:
    cen['{}_percent'.format(stat)] = cen[stat]/cen['total_population']
    reading_data.add_census_stat(precincts, cen, '{}_percent'.format(stat), population_column = 'total_population')

# These are scaled by total population 18 up
for stat in ['<9th', 'no_diploma', 'high_school', 'some_college', 'associates', 'bachelors', 'graduate_degree']:
    cen['{}_percent'.format(stat)] = cen[stat]/cen['total_population_18_up']
    reading_data.add_census_stat(precincts, cen, '{}_percent'.format(stat), population_column = 'total_population_18_up')

# These are scaled by total_pop_20_64_for_employment
for stat in ['in_labor_force_20_64', 'not_in_labor_force_20_64', 'unemployed_20_64']:
    cen['{}_percent'.format(stat)] = cen[stat]/cen['total_pop_20_64_for_employment']
    reading_data.add_census_stat(precincts, cen, '{}_percent'.format(stat), population_column = 'total_pop_20_64_for_employment')


cen['below_poverty_line_percent'] = cen['below_poverty_line']/cen['poverty_total']
reading_data.add_census_stat(precincts, cen, 'below_poverty_line_percent', population_column = 'poverty_total')

reading_data.add_census_stat(precincts, cen, 'median_household_income', population_column = 'total_population')
reading_data.add_census_stat(precincts, cen, 'median_age',population_column = 'total_population')


turnout = pd.read_csv('../project_data/processed_data/precinct_turnout.csv')


# Add the precinct_id column to `turnout`, set it as the index, and only keep the relevant columns.

turnout['precinct_id'] = turnout['Precinct']*100 + turnout['Ward']
turnout = turnout[['precinct_id', 'VoterTurnoutPercentage']]
turnout = turnout.set_index('precinct_id')


# Join `precincts` and `turnout`.



precincts_with_turnout = precincts.join(turnout, on='precinct_id')



# ## Add travel times from precinct center to assigned polling location

for mode in ['transit','driving','walking']:
    print(mode)
    precincts_with_turnout = reading_data.add_transit_duration(precincts_with_turnout, mode)

# Get minimum of walking and transit time, since sometimes the transit directions are just walking
precincts_with_turnout['walking_transit_travel_time'] = precincts_with_turnout[['walking_travel_time','transit_travel_time']].min(axis=1)



# Can only save data if there's one geometry column. Converting centroid column to string. Don't worry about error message. Centroids are approximately correct anyway. Chicago is locally flat



precincts_with_turnout['centroid'] = precincts_with_turnout.centroid.astype(str)



# ## Drop NA rows and save to file


precincts_with_turnout = precincts_with_turnout.dropna()


# The '<' character causes errors when using models, renaming

precincts_with_turnout = precincts_with_turnout.rename(columns={ '<9th_percent_cen':'lt_9th_percent_cen'})

precincts_with_turnout.to_file('../project_data/final_dataset/final_dataset_Chicago.geojson')


# # Train Test Split
# 
# NOTE: The O'hare airport and industrial zone don't have walking directions. These are our outliers that we've discussed anyway. Can be identified with walking_travel_tile == 999. Saving "no_outlier" version with these removed. These are precincts 434 and 1824. Inference done with travel times should be done with the no_outlier version of the data set 

#A random seed is being set so multiple participants can run the same Train Test Split without breaking the data.
X_train, X_test = train_test_split(precincts_with_turnout, test_size=0.20, random_state=190521)

X_train.to_file('../project_data/final_dataset/train_final_dataset_Chicago.geojson')
X_test.to_file('../project_data/final_dataset/test_final_dataset_Chicago.geojson')

X_train_no_outlier = X_train[~(X_train.walking_travel_time==999)]
X_test_no_outlier = X_test[~(X_test.walking_travel_time==999)]

X_train_no_outlier.to_file('../project_data/final_dataset/train_final_dataset_Chicago_no_outlier.geojson')
X_test_no_outlier.to_file('../project_data/final_dataset/test_final_dataset_Chicago_no_outlier.geojson')





