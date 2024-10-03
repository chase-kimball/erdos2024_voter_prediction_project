# Erdos2024 Voter Prediction Project

## 1. Dataset Identification:
The dataset you will be working with includes the following components:
- **Polling Site Accessibility Data**: This includes geographic information about polling sites and travel times. This data is used to compute persistent homology and generate 1D death values representing coverage gaps.
- **Voter Turnout Data**: Voter turnout rates by precinct, sourced from datasets like the MIT Election Data Science Lab or Harvard Dataverse.
- **Demographic Data**: Data from the American Community Survey (ACS) and State Voter Registration Files, which provides information on the voter-eligible population (VEP), socioeconomic factors, and voter registration details.

## 2. Dataset Description and Problem Statement:

### Dataset Description:
The dataset is composed of three primary components:

1. **Polling Site Accessibility**: This dataset includes polling station locations and travel times (using Google Maps API or other transportation data). Using persistent homology, the accessibility data is transformed into topological features, specifically focusing on 1D homology classes, which represent coverage gaps in polling site accessibility.
   - The dataset includes 1D death values, which indicate how long these coverage gaps persist as the scale of analysis increases.

2. **Voter Turnout Data**: Voter turnout data includes information about how many eligible voters actually cast their votes in elections. The data is aggregated at the precinct level, providing turnout rates as a percentage of registered or eligible voters.

3. **Demographic Data**: Demographic information includes socioeconomic and population data from sources like the American Community Survey (ACS). These details provide context for voter eligibility and participation and include factors like income, race, education, and population density.

### Problem Statement:
The problem being explored is whether gaps in polling site accessibility correlate with voter turnout. Specifically, the goal is to determine if areas with large 1D homology death values, which represent significant and persistent gaps in coverage, also exhibit lower voter turnout. This problem is critical because gaps in polling site coverage could be contributing to voter disenfranchisement, particularly in underserved areas.

By identifying these relationships, this study aims to provide insights into how geographic accessibility issues impact democratic participation. The findings could inform policymakers about how to optimize polling site distribution to improve voter access and increase turnout, potentially reducing civic engagement disparities.

## 3. Key Performance Indicators (KPIs):
- Average Voter Turnout per precinct.
- Distribution of 1D Homology Death Values: The extent and severity of coverage gaps.
- Correlation Coefficient between 1D homology death values and voter turnout.
- Percentage of Underserved Precincts: Areas with high death values and low voter turnout.
- Improvement in Voter Turnout: Potential increase in turnout if gaps are addressed (simulation or predictive modeling).
- Geographic Distribution of Voter Turnout: Visualization of turnout rates relative to polling site coverage.
- Polling Site Access: Measured as average travel time or distance to the nearest polling site.
