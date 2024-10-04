# Running notes on data sources

### {city}/{city}_death_simplices_by_death_in_dim_1.npy data

This is the basic data for the paper result: 
Triangles corresponding to the resource holes, given by lon/lat pairs for each vertex, 
and then the death filtration value, zscore of that value, and the ratio of the death to birth filtration value. 
The triangles are stored as Shapely Polygon objects. Have extracted into csv the vertex coords, the centroid coords, 
and resource hole stats

### PRESIDENT_precinct_general.csv

This is the raw # of votes by precinct broken down by party AND voting method (absentee, non-absentee, etc.)
A few things to note:
- Does NOT include total registered voters by precinct
- However, that data can be found elsewhere. For instance, Chicago gives these numbers by precinct [here](https://chicagoelections.gov/elections/results) (however, not by voting method). 
- Does NOT include demographic data
- Does NOT include spatial data, so precincts need to be looked up elsewhere to get their location beyond just what county they're in
- The precinct conventions are different for different cities, counties, etc
- There is no national database of precinct boundaries. But they do seem to be get-able city-by-city. For example, the [2012-2022 Chicago precinct boundaries](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Ward-Precincts-2012-2022-/uvpq-qeeq) are stored as sets of lat/lon pairs for vertices. I think packages like Shapely should allow us to easily check which ones intersect with triangles in the data above
- I've put the Chicago coordinates in the corresponding data folder [here](../project_data/chc/ChicagoPrecincts2012_2022.csv)
  
