import pandas as pd
import plotly.express as px

df_policy = pd.read_csv("Policy.csv")

dfCountry = df_policy[df_policy.CountryName == 'Afghanistan']
dfGermany = df_policy[df_policy.CountryName == 'Germany']
#dfCountry = df_policy[(df_policy['CountryName'] == countrySchools)],
#dfGermany = df_policy[(df_policy['CountryName'] == "Germany")],
dfMergedSchool = pd.merge(dfCountry, dfGermany, on='Date'),
dfMergedSchool = pd.DataFrame(dfMergedSchool)
print(dfMergedSchool.info(verbose=True))
#figSchool = px.line(dfMergedSchool,x='Date',y="C1_School_closing")
#figSchool.show()