import pandas as pd
from shapely import MultiPolygon, Polygon, wkt, intersection
import geopandas as gpd
import matplotlib.pyplot as plt 
#From the [Illinois State Board of Elections](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsPrecinct.aspx?ID=bt7bri46n7I%3d),
#we obtain voting results by precinct for the 2016 Presidential Election. 
df = pd.read_csv('../project_data/chc/51-120-PRESIDENT AND VICE PRESIDENT-2016GE.csv')


# We only care about the city of chicago
filtered_df = df[df['JurisName']=='CITY OF CHICAGO']

# After filtering, no longer need this feature
filtered_df = filtered_df.drop('JurisName', axis=1)

# Group the 'VoteCount' by 'PrecinctName' and calculate the sum (TotalVotesPerPrecinct) for each precinct
grouped_df = filtered_df.groupby('PrecinctName')['VoteCount'].sum().reset_index()

# Rename the column to 'TotalVotesPerPrecinct'
grouped_df.rename(columns={'VoteCount': 'votes'}, inplace=True)

# Add the 'Registration' column to the grouped DataFrame
grouped_df = pd.merge(grouped_df, filtered_df[['PrecinctName', 'Registration']].drop_duplicates(), on='PrecinctName', how='left')

# Compute Voter Turnout Percentage 
grouped_df['VoterTurnoutPercentage'] = (grouped_df['votes']/grouped_df['Registration']).round(4)*100

# Split 'PrecinctName' into 'Ward' and 'Precinct'features, to better match shape files
grouped_df[['Ward', 'Precinct']] = grouped_df['PrecinctName'].str.extract(r'Ward (\d+) Precinct (\d+)')

# Convert the Ward and Precinct values into ints
grouped_df[['Ward', 'Precinct']] = grouped_df[['Ward', 'Precinct']].astype(int)

# No longer need the 'PrecinctName' feature after the splitting
grouped_df.drop('PrecinctName',axis=1)


# From Chase's previous searching, we'll use 
#[this map](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Ward-Precincts-2012-2022-/uvpq-qeeq) of Chicago's voting precincts for 2012-2022.
precs = pd.read_csv('../project_data/chc/ChicagoPrecincts2012_2022.csv')
precs['the_geom'] = precs['the_geom'].apply(wkt.loads) 
precs = precs.rename(columns={'the_geom':'geometry','WARD':'Ward','PRECINCT':'Precinct'})
precs[['Ward', 'Precinct']] = precs[['Ward', 'Precinct']].astype(int)
precs = gpd.GeoDataFrame(precs, crs='epsg:4326')
merged_df = pd.merge(precs, grouped_df[['Ward', 'Precinct', 'VoterTurnoutPercentage']], on=['Ward', 'Precinct'], how='left')

merged_df.to_csv('../project_data/processed_data/precinct_turnout.csv')