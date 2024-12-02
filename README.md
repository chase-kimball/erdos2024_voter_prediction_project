# Erdos2024 Voter Prediction Project
Voting Time vs. Voter Turnout

By: Avi Steiner, Chase Kimball, Davis Stagliano
## Summary
We restricted our analysis to just the city of Chicago, and pulled demographic data from the US Census Bureau. Our baseline model was a simple average of voter turnout. Against that, we compared linear and logistic regressions, as well as an XGBoost tree. The regressions performed better than the tree, by about 3%. Since the data is not purely linear, we believe the logistic model is best. Our results indicate low correlation between voting time and voter turnout.

## Problem Statement:
The problem being explored is whether gaps in polling site accessibility correlate with voter turnout. Specifically, the goal is to determine if areas with longer times to vote also exhibit lower voter turnout. This problem is critical because gaps in polling site coverage could be contributing to voter disenfranchisement, particularly in underserved areas.
By identifying these relationships, this study aims to provide insights into how geographic accessibility issues impact democratic participation. The findings could inform policymakers about how to optimize polling site distribution to improve voter access and increase turnout, potentially reducing civic engagement disparities.

## 1. Potential Stakeholders
- **Election Authorities and Government Agencies**: Local election boards, state/federal commissions, and voter outreach offices interested in optimizing polling site distribution for fairer access.
- **Policymakers and Legislators**: City officials and state legislators focused on shaping policies to improve voter access and turnout.
- **Civil Rights and Advocacy Organizations**: Groups like the ACLU and NGOs advocating for voting rights, aiming to address disparities in voter access.
- **Community Leaders and Activists**: Grassroots activists and civic organizations focused on voter mobilization in underserved areas.
- **Academic and Research Institutions**: Researchers and think tanks studying voting behavior and policy solutions related to voter access.
- **Technology and Data Providers**: Geospatial analytics firms and election technology providers interested in leveraging data to improve voter accessibility.
- **Voters and Communities**: Underserved communities and voters who face challenges accessing polling sites and would benefit directly from improved access.

## 2. Key Performance Indicators (KPIs):
- Average Voter Turnout per precinct.
- Correlation Coefficient between travel time to voting locations and voter turnout.
- Correlation Coefficient between known demographic indicators and voter turnout.
- Geographic Distribution of Voter Turnout: Visualization of turnout rates relative to polling site coverage.
- Polling Site Access: Measured as average travel time or distance to the nearest polling site.

## 3. Dataset Identification:
The dataset we will be working with includes the following components:
- **Polling Site Accessibility Data**: This includes geographic information about polling sites and travel times. This data is used to calculate the expected time cost of voting.
- **Voter Turnout Data**: Voter turnout rates by precinct, sourced from datasets like the MIT Election Data Science Lab or State Boards of Elections.
- **Demographic Data**: Data from the US Census Bureau, which provides information on the population, including socioeconomic factors.

## 4. Dataset Description and Problem Statement:
### Dataset Description:
The dataset is composed of three primary components:
1. **Polling Site Accessibility**: This dataset includes polling station locations and travel times (using Google Maps API or other transportation data).
2. **Voter Turnout Data**: Voter turnout data includes information about how many eligible voters actually cast their votes in elections. The data is aggregated at the precinct level, providing turnout rates as a percentage of registered or eligible voters.
3. **Demographic Data**: Demographic information includes socioeconomic and population data from the US Census Bureau. These details provide context for voter eligibility and participation and include factors like income, race, education, and population density.

### Discussion of Dataset Issues:
1. The data from the Census had multiple missing or invalid fields.
   - For average household income, if the variance of the data for the tract was larger than the average of the tract, roughly -$6,000,000 was entered instead. We resolved this by treating the field as empty, and skipped over it during our anlysis.
   - Missing data in the census was entered as NaN into the dataframe. When we attempted to sum over large numbers of tracts, a single NaN field for any tract in a precinct resulted in a NaN for the whole precinct. We solved this by treating NaNs as 0.
   - Treating NaN fields as zero reduced the number of precincts with invalid results down to two. To avoid any issues resulting from their inclusion, we opted to wholly remove the two precincts from the analysis.
2. The formatting of the Census was far too granular.
   - While a few, important, data fields were collated into a total number, most were left in extremely granular forms. For example, there is no topline result for the number of people in a tract with a bachelor’s degree. That data is only available broken down first by sex and then by age. Finding the total number of bachelor’s degrees in a tract required summing over ten non-consecutive fields. This had to be repeated for every education level reported in the census.
3. There is no information on the population distribution within a tract.
   - Because census tracts are based on geographic features, and voting precincts are based on population, most tracts overlapped more than one precinct. We thus needed to split the populations of each tract between their overlapping precincts.
   - Without more detailed data on the population spread within a tract, we made the assumption that, for every metric, every census tract is evenly distributed. This allowed us to split data from the tracts into their respective precincts by percentage of overlap. That is, if 20% of a tract lies within a precinct, 20% of every data field for that tract lies within that precinct.
4. Finding exact data on the eligible voting population, especially broken down enough to be of use, was not feasible in our timeframe.
   - As such, we did our models based on total population. While this will certainly have an impact on our data, our hope is that the impact is roughly equal across all precints, and that in comparing them, the effect will be nullified. The only precint where this assumption likely does not hold is home to the Cook County Correctional Facilities, which has an exceptionally large inmate population. We left it in our analysis, but better voter eligible data would likely have an impact on that precinct.

## 5. Analysis
- Average voter turnout for Chicago was roughly %71. This was used as our baseline model. The baseline model had an RMSE of about 10%
- Linear Regression
- Logistic Regression
- XGBoost

## 6. Conclusion and Next Steps
Comparing to our baseline, we found the linear and logistic regressions improved the RMSE by about 45%. The XGBoost tree only improved the RMSE by 42%. Given that the data is clearly not of a purely linear nature, the logistic model is the best fit.
While the regressions were better models, all agreed on which factors were the most important, namely education, followed by income. While racial identity had some correlation, it was varied, and travel time to vote had small coefficients all around.
To answer our initial question, it appears that, for our data, voting time does not have a significant impact on voter turnout.

The next step would be to expand the model into other major cities for the 2016 election, and then to compare with the 2024 election, once that data is available. Other cities, such as LA and NYC, with know and serious traffic problems, might yield different results. It is entirely possible the relationship between voting time and turnout depends on the city. Additionally, since the pandemic changed how people can and do vote, it is possible that travel time is even less important now in 2024, correlating with the rise in mail in voting options.
