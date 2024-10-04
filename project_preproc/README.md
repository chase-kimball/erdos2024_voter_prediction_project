# Data Preprocessing

## Organization

The [project_data](../project_data) folder contains a folder for each city in the persistent homology study.
Since we have a lot of data in this repo and we only need some of it, I suggest we 
collect the important bits here

## Death Simplex information

The [preprocessing notebook](preprocessing_notebook.ipynb) creates .csv versions
of the 1-D death simplex data.

The raw .npy's are described below. Instead of storing Shapely Polygon objects,
the .csvs store the longitudes and latitudes needed to recreate them, along with
the coordinates of their centroid.

from the paper data readme:

Death simplex information is stored in files whose names are of the form:

{city}_death_simplices_by_death_in_dim_{dim}.npy


where city is the name of the city (e.g., “atl”) and dim = 0 or 1. 
The first column is the geometry of the death simplex (a Shapely LineString object for dim = 0 or a Shapely Polygon object for dim = 1).
The second column is the death filtration value (in seconds)
The third column is the z-score of the death filtration value, calculated in relation to the other death simplices for that particular city and dimension
The fourth column is the death/birth ratio.

