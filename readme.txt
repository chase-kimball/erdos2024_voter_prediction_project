d_matrix_building.ipynb is a notebook containing code on constructing the distance matrices given travel-time matrices (by car, public transport, and walk).

distance_matrix_completer.ipynb is a notebook containing code that completes distances by shortest path (as descrbed in subsection 3.1)

ph_computations.ipynb contains code for computing the persistence diagrams and death-simplices plots given distance matrices.

walk_matrix_computations.ipynb contains code for how we computed walking times. 

As this, this repository will not run as intended, since we had to remove all matrices constructed from the travel times obtained by Google. 

One can use the walk matrices to in place of the distance matrices we computed if desired. 

Distance matrices are stored in files whose names are of the form:

{city}_d_matrix.npy

Stored within {city} folder.

Death simplex information is stored in files whose names are of the form:

{city}_death_simplices_by_death_in_dim_{dim}.npy


where city is the name of the city (e.g., “atl”) and dim = 0 or 1. 
The first column is the geometry of the death simplex (a Shapely LineString object for dim = 0 or a Shapely Polygon object for dim = 1).
The second column is the death filtration value (in seconds)
The third column is the z-score of the death filtration value, calculated in relation to the other death simplices for that particular city and dimension
The fourth column is the death/birth ratio.

Stored within {city} folder.

Also note that the boundaries of each city used are not generally the legal boundaries of that city. In the cases of Jacksonville and Salt Lake City, the borders used are the true legal borders of those cities. For other cities, there is further discussion below. The boundary files we used for each city in our analysis can be found in their corresponding {city} folder.

Atlanta: The city of Atlanta does not contain its suburbs. In order to include these in the analysis, we used the entire area that is served by the Atlanta Regional Commission. This commission is responsible for many projects in the Atlanta metropolitan area including the transportation system.

Chicago: The northwest region of Chicago's border contains significant nonconvexity which affects the capabilities of our method. To handle this, we chose to include the entirety of every zip code that is partially contained in Chicago. This includes some zip codes in which only a very small proportion of the zip code lies in the legal boundary of Chicago.

Los Angeles: For Los Angeles, we faced similar nonconvexity issues as we did in the case of Chicago. In order to handle this, we chose instead to use the entirety of Los Angeles County.

New York City: New York City is disconnected, which creates significant issues for our method. This includes the identification of regions of poor coverage which are in reality almost entirely bodies of water. To resolve this, we subdivided New York City into three regions (Queens and Brooklyn, Manhattan and the Bronx, and Staten Island). We performed the analysis on each of these three regions individually and combined those results into single figures.

----- 

We have also uploaded a copy of our referee response letter, for curious and interested readers to peruse.