
# ## Convert the census tract data to a geopandas dataframe

# We've downloaded the 2010 census tract shapefiles data. Here is a link to what the columns mean: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2010.html#list-tab-790442341



from census import Census
from us import states
import pandas as pd
import zipfile
import os, shutil
from shapely import MultiPolygon, Polygon, wkt, intersection
import geopandas as gpd
import matplotlib.pyplot as plt



def load_tiger_shapefile(zip_path):
    # Unzip the TIGER/Line Shapefile if it's in a .zip format
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extract_dir = zip_path.rstrip('.zip')
        zip_ref.extractall(extract_dir)

    # Find the main shapefile (the one with .shp extension)
    shp_file = next((f for f in os.listdir(extract_dir) if f.endswith('.shp')), None)
    if not shp_file:
        raise FileNotFoundError("No .shp file found in the extracted contents")

    # Load shapefile into a GeoDataFrame
    gdf = gpd.read_file(os.path.join(extract_dir, shp_file))
    
    # Clean up extracted files if desired
    shutil.rmtree(extract_dir)

    return gdf

zip_path = '../project_data/chc/tl_2010_17_tract10.zip' # path to the TIGER/Line Shapefile ZIP file
gdf = load_tiger_shapefile(zip_path)
gdf = gdf.loc[gdf['COUNTYFP10'] == '031'] # 031 is the 2010 FIPS code for Cook County
gdf = gdf[['TRACTCE10', 'geometry']] # only keep the relevant columns


# ## Set up the census data

# Following the instructions on https://pypi.org/project/census/, we obtained a Census API key.


c = Census(PUT YOUR API KEY HERE)


def get_census_data(census_fields={'NAME': 'name'}):
    tract_data = c.acs5.get(tuple(census_fields.keys()), {'for': 'tract:*', 'in': 'state:17 county:031'})
    
    # convert the tract data to a pandas DataFrame
    df = pd.DataFrame(tract_data)

    # rename the columns of df for readability
    df.rename(columns=census_fields, inplace=True)

    return df


# The ACS codes can be found here: https://api.census.gov/data/2010/acs/acs5/variables.html


census_fields = {'NAME': 'name',
                'B01003_001E': 'total_population',
                'B19013_001E': 'median_household_income',

                'B02001_002E': 'white_alone',
                'B02001_003E': 'black_alone',
                'B02001_004E': 'indigenous_alone',
                'B02001_005E': 'asian_alone',
                'B02001_006E': 'pacific_islander_alone',
                'B02001_007E': 'other_alone',
                'B02001_008E': 'multiracial',
                 'B08141_031E': 'work_from_home',
                 'B08301_001E': 'automobile_to_work',
                 'B08301_010E': 'public_transit_to_work',
                 'B08301_016E': 'taxi_to_work',
                 'B08301_017E': 'motorcycle_to_work',
                 'B08301_018E': 'bike_to_work',
                 'B08301_019E': 'walk_to_work',
                 'B08301_020E': 'other_to_work',
                 'B01002_001E': 'median_age',
                 'B17001_002E': 'below_poverty_line',
                 'B17001_001E': 'poverty_total',
                 'B15001_001E': 'total_population_18_up'
    
                 
                 
                 
                 
                }
census_fields = census_fields #| sex_by_age_fields
census_data = get_census_data(census_fields)


# Here's a utility function that will be useful when we need to add a bunch of columns.


def get_census_data_then_sum(acs_codes=[], total_column_name='total'):
    df = get_census_data({'NAME': 'name'} | {x:x for x in acs_codes})
    
    # Create the total column. Note that the last three columns are state, county, and tract.
    df[total_column_name] = df.iloc[:, 1:-3].sum(axis=1)

    # Keep only the necessary columns
    return df[['name', total_column_name, 'tract']]


# ### Employment


employment_data = get_census_data({'NAME': 'name'})


acs_prefix_employment = 'B23001'

total_start = 10
total_end = 66
labor_start = 11
labor_end = 67
unempl_start = 15
unempl_end = 71
nolabor_start = 16
nolabor_end = 72
male_female_offset = 86

acs_total_male_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(total_start, 
                                                                                        total_end + 1,
                                                                                        7)] #Male 20-64 
acs_total_female_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(total_start + male_female_offset,
                                                                                          total_end + male_female_offset + 1,
                                                                                          7)] #Female 20-64

acs_in_labor_force_male_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(labor_start,
                                                                                                 labor_end + 1,
                                                                                                 7)] #Male 20-64 
acs_in_labor_force_female_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(labor_start + male_female_offset,
                                                                                          labor_end + male_female_offset + 1,
                                                                                                   7)] #Female 20-64

acs_unemployed_male_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(unempl_start,
                                                                                                 unempl_end + 1,
                                                                                                 7)] #Male 20-64 
acs_unemployed_female_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(unempl_start + male_female_offset,
                                                                                          unempl_end + male_female_offset + 1,
                                                                                                   7)] #Female 20-64

acs_not_in_labor_force_male_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(nolabor_start,
                                                                                                 nolabor_end + 1,
                                                                                                 7)] #Male 20-64 
acs_not_in_labor_force_female_20_64 = ['{}_{}E'.format(acs_prefix_employment,f'{i:03}') for i in range(nolabor_start + male_female_offset,
                                                                                          nolabor_end + male_female_offset + 1,
                                                                                                   7)] #Female 20-64

total_20_64_data = get_census_data_then_sum(acs_total_male_20_64 + acs_total_female_20_64,
                                            total_column_name='total_pop_20_64_for_employment')
in_labor_force_20_64_data = get_census_data_then_sum(acs_in_labor_force_male_20_64 + acs_in_labor_force_female_20_64,
                                            total_column_name='in_labor_force_20_64')
not_in_labor_force_20_64_data = get_census_data_then_sum(acs_not_in_labor_force_male_20_64 + acs_not_in_labor_force_female_20_64,
                                            total_column_name='not_in_labor_force_20_64')
unemployed_20_64_data = get_census_data_then_sum(acs_unemployed_male_20_64 + acs_unemployed_female_20_64,
                                            total_column_name='unemployed_20_64')

for dataset in [total_20_64_data, in_labor_force_20_64_data, not_in_labor_force_20_64_data, unemployed_20_64_data]:
    employment_data = employment_data.merge(dataset, on=['name', 'tract'])


# We now merge employment data into `census_data`.

census_data = census_data.merge(employment_data, on=['name', 'state', 'county', 'tract'])



census_data


# ### Educational attainment


educational_attainment_data = get_census_data({'NAME': 'name'})



educational_attainment_lt_9th_data = get_census_data_then_sum(['B15001_004E', # male 18-24
                                                               'B15001_012E', # male 25-34
                                                               'B15001_020E', # male 35-44
                                                               'B15001_028E', # male 45-64
                                                               'B15001_036E', # male >=65
                                                               'B15001_045E', # female 18-24
                                                               'B15001_053E', # female 25-34
                                                               'B15001_061E', # female 35-44
                                                               'B15001_069E', # female 45-64
                                                               'B15001_077E' # female >=65
                                                               ],
                                                               total_column_name='<9th')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_lt_9th_data, 
                                                               on=['name', 'tract'])

# 9th to 12th grade, no diploma
educational_attainment_no_diploma = get_census_data_then_sum(['B15001_005E', # male 18-24
                                                               'B15001_013E', # male 25-34
                                                               'B15001_021E', # male 35-44
                                                               'B15001_029E', # male 45-64
                                                               'B15001_037E', # male >=65
                                                               'B15001_046E', # female 18-24
                                                               'B15001_054E', # female 25-34
                                                               'B15001_062E', # female 35-44
                                                               'B15001_070E', # female 45-64
                                                               'B15001_078E' # female >=65
                                                               ],
                                                               total_column_name='no_diploma')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_no_diploma, 
                                                               on=['name', 'tract'])

# High school graduate, GED, or alternative
educational_attainment_high_school = get_census_data_then_sum(['B15001_006E', # male 18-24
                                                               'B15001_014E', # male 25-34
                                                               'B15001_022E', # male 35-44
                                                               'B15001_030E', # male 45-64
                                                               'B15001_038E', # male >=65
                                                               'B15001_047E', # female 18-24
                                                               'B15001_055E', # female 25-34
                                                               'B15001_063E', # female 35-44
                                                               'B15001_071E', # female 45-64
                                                               'B15001_079E' # female >=65
                                                               ],
                                                               total_column_name='high_school')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_high_school,
                                                               on=['name', 'tract'])

# Some college, no degree
educational_attainment_some_college = get_census_data_then_sum(['B15001_007E', # male 18-24
                                                               'B15001_015E', # male 25-34
                                                               'B15001_023E', # male 35-44
                                                               'B15001_031E', # male 45-64
                                                               'B15001_039E', # male >=65
                                                               'B15001_048E', # female 18-24
                                                               'B15001_056E', # female 25-34
                                                               'B15001_064E', # female 35-44
                                                               'B15001_072E', # female 45-64
                                                               'B15001_080E' # female >=65
                                                               ],
                                                               total_column_name='some_college')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_some_college,
                                                               on=['name', 'tract'])

# Associate's degree
educational_attainment_associates = get_census_data_then_sum(['B15001_008E', # male 18-24
                                                               'B15001_016E', # male 25-34
                                                               'B15001_024E', # male 35-44
                                                               'B15001_032E', # male 45-64
                                                               'B15001_040E', # male >=65
                                                               'B15001_049E', # female 18-24
                                                               'B15001_057E', # female 25-34
                                                               'B15001_065E', # female 35-44
                                                               'B15001_073E', # female 45-64
                                                               'B15001_081E' # female >=65
                                                               ],
                                                               total_column_name='associates')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_associates,
                                                               on=['name', 'tract'])

# Bachelor's degree
educational_attainment_bachelors = get_census_data_then_sum(['B15001_009E', # male 18-24
                                                               'B15001_017E', # male 25-34
                                                               'B15001_025E', # male 35-44
                                                               'B15001_033E', # male 45-64
                                                               'B15001_041E', # male >=65
                                                               'B15001_050E', # female 18-24
                                                               'B15001_058E', # female 25-34
                                                               'B15001_066E', # female 35-44
                                                               'B15001_074E', # female 45-64
                                                               'B15001_082E' # female >=65
                                                               ],
                                                               total_column_name='bachelors')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_bachelors,
                                                               on=['name', 'tract'])

# Graduate or professional degree
educational_attainment_graduate = get_census_data_then_sum(['B15001_010E', # male 18-24
                                                               'B15001_018E', # male 25-34
                                                               'B15001_026E', # male 35-44
                                                               'B15001_034E', # male 45-64
                                                               'B15001_042E', # male >=65
                                                               'B15001_051E', # female 18-24
                                                               'B15001_059E', # female 25-34
                                                               'B15001_067E', # female 35-44
                                                               'B15001_075E', # female 45-64
                                                               'B15001_083E' # female >=65
                                                               ],
                                                               total_column_name='graduate_degree')
educational_attainment_data = educational_attainment_data.merge(educational_attainment_graduate,
                                                               on=['name', 'tract'])



# We now merge the educational attainment data into `census_data`.


census_data = census_data.merge(educational_attainment_data, on=['name', 'state', 'county', 'tract'])


# ## Cleaning
# We need to remove census tracts with 0 population. Also, a number of rows have negative median household income and therefore need to be removed. This is because for a 5-year median estimate, the margin of error associated with a median was larger than the median itself.


def clean_census_data(census_data):
    # Remove census tracts with 0 population
    census_data = census_data[census_data['total_population'] > 0.0]

    # A number of rows have negative median household income and therefore need to be removed. 
    # This is because for a 5-year median estimate, the margin of error associated with a median 
    # was larger than the median itself.
    census_data = census_data.loc[census_data['median_household_income'] >= 0]
    
    return census_data

cleaned_census_data = clean_census_data(census_data)


# We now combine `gdf` with `cleaned_census_data`.

geo_census_data = gdf.join(cleaned_census_data.set_index('tract'), on='TRACTCE10', how='inner')


# Export the data to a geojson.


geo_census_data.to_file('../project_data/processed_data/Chicago_geocensus_data.geojson')






