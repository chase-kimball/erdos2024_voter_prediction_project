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

#Processing precinct data from csv to GeoDataFrame format, for ease of later use.
def get_raw_precinct_gpd(filename='../project_data/chc/ChicagoPrecincts2012_2022.csv'):
    precs = pd.read_csv(filename)
    
    #Creates a unique identifier for each precinct and ward, formatted first two digits for precinct, second two for ward
    precs['precinct_id'] = precs.PRECINCT*100 + precs.WARD
    
    #Creates shape data for the precinct
    precs['the_geom'] = precs['the_geom'].apply(wkt.loads)
    precs = precs.rename(columns={'the_geom':'geometry'})
    precs = precs.drop(['FULL_TEXT', 'SHAPE_AREA', 'SHAPE_LEN'], axis=1)
    precs['centroid'] = centroid(precs.geometry)

    #crs=epsg:4326 ensures the location data is stored as GPS data for consistency and accuracy.
    precs_gpd = gpd.GeoDataFrame(precs, crs='epsg:4326')

    #Indexes precints by the unique identifier created earlier
    return precs_gpd.set_index('precinct_id')

#Creates a GeoDataFrame for the death simplecies data
def get_raw_simplex_gpd(filename='../project_data/chc/chc_death_simplices_by_death_in_dim_1.npy'):
    dsimps = np.load(filename, allow_pickle=True)

    #Strips the original file down to only the data we are concerned with
    dsimps_dict = dict(zip(['geometry','death_filtration_value','death_filtration_zscore','death_birth_ratio'],dsimps.T))
    dsimps_gpd = gpd.GeoDataFrame(dsimps_dict, crs='epsg:4326')
    dsimps_gpd['dsimp_index']= dsimps_gpd.index.values

    return dsimps_gpd

#Creates another GeoDataFrame, this time for the polling locations in Chicago
def get_raw_polls_gpd(filename = '../project_data/processed_data/Polling_Places_Chicago_2016.csv'):

    polls = pd.read_csv(filename)
    polls_gpd = gpd.GeoDataFrame()

    #Defines and sets data we are concerned with into a cleaner, more readable format
    polls_gpd['precinct_id'] = polls.Precinct.astype(int)
    polls_gpd['polling_name'] = polls['Polling Place Name']
    polls_gpd['polling_address'] = polls['Address Line 1']
    polls_gpd['polling_description'] = polls['Description']
    
    #Converts a Y/N field to a 1/0 value
    polls_gpd['polling_accessible'] = 1 * (polls['Accessible'] == 'Y')
    polls_gpd['polling_zip'] = polls['Zip']
    polls_gpd['polling_lat'] = polls['lat']
    polls_gpd['polling_lon'] = polls['lon']

    return polls_gpd.set_index('precinct_id')

def append_intersecting_simplex_data_to_precinct(precs,dsimps_filename = '../project_data/chc/chc_death_simplices_by_death_in_dim_1.npy'):
    
    dsimps = get_raw_simplex_gpd(dsimps_filename)
    
    #Initialize some lists to store results
    n_intersect = []
    mean_dfv = []
    indices = []

    #Iterates over precints
    for ii, prec in precs.iterrows():
        dfvs_ii = []
        indices_ii = []
        
        for jj, dsimp in dsimps.iterrows():

            #Finds overlap between simplicies and precints
            if not intersection(prec.geometry,dsimp.geometry).area == 0:

                #Creates a list for each precint of when and where simplicies overlap
                indices_ii.append(str(dsimp.dsimp_index))
                dfvs_ii.append(dsimp.death_filtration_value)
                
        #If there are no overlaps, fill with zero, else fill with a string to represent the simplicies
        #Confirm interpretation please
        if len(dfvs_ii) == 0:
            mean_dfv.append(0)
            indices.append('')
        else:
            mean_dfv.append(np.mean(dfvs_ii))
            indices.append('_'.join(indices_ii))
                            
        n_intersect.append(len(indices_ii))

    #Appends data to the already created precint dataframe
    precs['dsimp_n_intersect'] = n_intersect
    precs['dsimp_mean_dfv'] = mean_dfv
    precs['dsimp_indices'] = indices
    
    return precs

#Adds locations of physical polling locations to the precints dataframe
def append_polls_to_precinct(precs, polls_filename = '../project_data/processed_data/Polling_Places_Chicago_2016.csv'):
    
    polls = get_raw_polls_gpd(polls_filename)
    precs = precs.join(polls)
    imputed = []

    #Precints without a polling location have a default lati of -999, an unrealistic position. Using that, filter out precints without a polling location.
    precs_with = precs[precs.polling_lat != -999]
    counter = 0
    
    for ii, prec in precs.iterrows():
        if counter % 100 == 0: print(counter)
        counter += 1
        if prec.polling_lat != -999: 
            imputed.append(0)
            continue

        #If there is no polling location attached to the precints, imputes the nearest polling location by straight line distance
        min_dist = None
        nearest_id = None
        for jj, poll in precs_with.iterrows():
   
            dist = distance.distance(prec.centroid.__geo_interface__['coordinates'][::-1],(poll.polling_lat,poll.polling_lon)).km
            if min_dist is None or dist < min_dist:
                min_dist = dist
                nearest_id = jj
        imputed.append(1)

        #Adds data to the precint dataframe and names it
        precs.loc[ii, 'polling_address'] = precs_with.loc[nearest_id].polling_address
        precs.loc[ii, 'polling_name'] = precs_with.loc[nearest_id].polling_name
        precs.loc[ii, 'polling_description'] = precs_with.loc[nearest_id].polling_description
        precs.loc[ii, 'polling_accessible'] = precs_with.loc[nearest_id].polling_accessible
        precs.loc[ii, 'polling_zip'] = precs_with.loc[nearest_id].polling_zip
        precs.loc[ii, 'polling_lat'] = precs_with.loc[nearest_id].polling_lat
        precs.loc[ii, 'polling_lon'] = precs_with.loc[nearest_id].polling_lon
        
    precs['polling_imputed'] = imputed
    
    return precs

#This function finds and labels the overlap between the precints and the census tracts, allowing for crossreference and data manipulation
def add_census_indices(precs,cen):
    census_indices = []
    for ii, prec in precs.iterrows():

        #Starts each precint with an area scalar of zero, and a 'map' of the location.
        #Indicies will keep track of which census tracts intersect with precint ii.
        total_area = 0
        prec_area = prec.geometry.area
        indices = []
    
        for jj, block in cen.iterrows():

            #Sets a scalar value to determine the size of the intersection of precint ii and census tract jj
            area_int = intersection(prec.geometry,block.geometry).area

            #If the size of intersection is zero, skip the tract, else append the tract identifier to indices
            #and increase 'total_area' by the amount of overlap.
            #'total_area' is being used as a sanity check to ensure each precint is correctly built from census data.
            if area_int == 0: continue
            else:
                indices.append(str(jj))
                total_area += area_int
        
        #Ensures the list on the final dataframe is deliniated, using '_' or is left blank        
        if not len(indices) == 0:
            census_indices.append('_'.join(indices))
        else:
            census_indices.append('')

    #Adds the census overlap data to the main dataframe.
    precs['census_indices'] = census_indices

    return precs

#This function takes the string of census overlaps returned by 'add_census_indices' and turns it into a more useable list datatype
def index_str_to_list(s):
    indices_str = s.split('_')
    if indices_str == ['']:
        return []
    indices = [int(index) for index in indices_str]

    return indices    

#This function looks through the list of census tracts that overlap with a given precint, the area of overlap, and a passed in statistic 'stat_name'
#and calculates the total/average of that statistic in that precint.
#Note: An assumption was made that every statistic has uniform distribution in ever census tract.
    #That is, we assumed that the population densitity of a census tract is perfectly uniform.
    #Thus if 20% of a census lies within the precint, 20% of the people in that tract live within that precint.
def average_census_blocks(indices, prec, census_gpd, stat_name, population_column):
    prec_area = prec.geometry.area
    total_area = 0
    cum_stat = 0
    total_pop = 0

    for ii in indices:
        tract = census_gpd.iloc[ii].fillna(0)

        #Finds the scalar area of the overlap between the current tract and precint, and defines a ratio
        tract_area = tract.geometry.area
        int_area = intersection(prec.geometry,tract.geometry).area
        frac_tract = int_area/tract_area

        #Finds the estimated population relevant to the statistic of interest of the tract living in the precint
        #Since these are estimates, fractional amounts of people may live in the overlap.
        intersection_population = tract[population_column] * frac_tract
        stat = tract[stat_name]

        #Some tracts have NaN values from cleaning. Since Python consideres int + NaN = NaN, this code was introduced to prevent a cascading NaN issue.
        if np.isnan(intersection_population):
            intersection_population = 0
            stat = 0

        #Adds up the fractional populations from each tract in each precint to build a final count.
        #'total_area' is again used as a sanity check.
        total_pop += intersection_population
        total_area += int_area

        #'weighted_stat' is the value from the current working tract, 'cum_stat' is the cumulative total from all tracts
        weighted_stat = tract[stat_name] * intersection_population
        cum_stat += weighted_stat
        
    if total_pop == 0:
        cum_stat = total_pop = np.nan
        
    return cum_stat / total_pop, total_pop, total_area/prec_area
        
# NOTE: The census data is missing 16 tracts where there is no median income data. 
# Check total_area/prec_area to see where these missing tracts show up 

#While 'average_census_blocks' works on a single precint, this function loops over all precints
#calls 'average_census_blocks' and adds the data to the dataframe.
def add_census_stat(precs, census_gpd, stat_name, population_column):
    
    stats = []
    area_fracs = []
    total_populations = []

    #Loops over all precints
    for ii, prec in precs.iterrows():
        indices = index_str_to_list(prec.census_indices)
        stat, total_pop, area_frac = average_census_blocks(indices, prec, census_gpd, stat_name, population_column)
        
        stats.append(stat)
        area_fracs.append(area_frac)
        total_populations.append(total_pop)

    if not 'total_population_cen' in precs.columns and population_column  == 'total_population':
        precs['total_population_cen'] = total_populations
        precs['frac_area_cen'] = area_fracs
    precs['{}_cen'.format(stat_name)] = stats 

#WARNING -- This function makes calls to the google API and as such must be run sparingly.
#This code charges us per 1000 quries
#Purpose of function is to loop over all precints and find the fastest route from their center to their polling location, both by car and walk/transit
def add_transit_duration(precs, transit_mode):
    #This is Chase's key, and should be used only by Chase
    with open('../../../google_maps_api','r') as f:
        my_key = f.read().strip()
    gmaps = googlemaps.Client(key=my_key)

    precs['centroid'] = centroid(precs.geometry)
    durations = []
    count = 0
    for ii, prec in precs.iterrows():
        if count % 100 == 0:
            print(count)
        count += 1
        address = prec.polling_address + ', Chicago, IL'
        lon, lat = prec.centroid.__geo_interface__['coordinates']
        result = gmaps.directions(origin=(lat,lon), destination = address, mode=transit_mode)
        if result == []:
            durations.append(999)
            continue
        duration = result[0]['legs'][0]['duration']['value']
        duration = duration / 60.
        durations.append(duration)
    precs['{}_travel_time'.format(transit_mode)] = durations

    return precs