import sys
import pandas as pd

# Initialize the country list
country_intial_df = pd.read_excel("datasets/acaps_covid19_government_measures_dataset_0.xlsx", sheet_name="Database")
european_country_df = country_intial_df[country_intial_df['REGION'] == "Europe"]
distinct_europe_countries_list = european_country_df["COUNTRY"].unique()

def read_data_government_measures(filename):

    gm_df = pd.read_excel(filename, sheet_name="Database")
    european_gn_df = gm_df[gm_df['REGION'] == "Europe"]
    filtered_european_gn_df = european_gn_df.filter(
        ["COUNTRY", "ISO", "REGION", "CATEGORY", "MEASURE", "COMMENTS", "DATE_IMPLEMENTED", "LINK",  "SOURCE", "SOURCE_TYPE"])
    filtered_columns_df = filtered_european_gn_df.filter(["COUNTRY", "CATEGORY", "MEASURE", "DATE_IMPLEMENTED", "COMMENTS"])

    #category_grouped_df = filtered_columns_df.groupby(['COUNTRY', 'CATEGORY'])
    formatted_data_frame = date_formatter(filtered_columns_df, 'DATE_IMPLEMENTED')
    return (filtered_columns_df)


def read_data_government_restrictions(filename):

    dataSet1 = pd.read_csv(filename)

    # Normalizing the date and countries
    dataSet1 = date_formatter(dataSet1, 'date')
    dataset_country_filtered = country_normalizer(dataSet1,'CountryName')

    return (dataset_country_filtered)

def read_data_covid_and_recovery(owid_covid_data_file, filename2):

    ## Preparing the owid covid dataframe
    df_world = pd.read_csv(owid_covid_data_file)
    search_df_europe = df_world['continent'] == 'Europe'
    df_europe = df_world[search_df_europe]
    df_europe = df_europe.rename({'location': 'country'}, axis=1)
    df_europe_cases = df_europe.groupby(['date', 'country'])[
        'total_cases', 'total_deaths','new_cases','new_deaths'].max()
    df_europe_cases = df_europe_cases.reset_index()

    # Normalizing the date and countries
    df_europe_cases = date_formatter(df_europe_cases, 'date')
    df_europe_cases_normalized = country_normalizer(df_europe_cases, 'country')

    ## Preparing the recovery cases dataframe
    df_recovered = pd.read_csv(filename2)
    del df_recovered['Province/State']
    del df_recovered['Lat']
    del df_recovered['Long']
    df_recovered = df_recovered.rename({'Country/Region': 'country'}, axis=1)
    df_recovered = df_recovered.groupby(['country']).sum()
    df_recovered = df_recovered.reset_index()
    df_recovered = pd.melt(df_recovered, id_vars=[
                        "country"], var_name="date", value_name="total_recovery")
    df_recovered['total_recovery'] = df_recovered['total_recovery'].astype(float)

    # Normalizing the date and countries
    df_recovered = date_formatter(df_recovered, 'date')
    df_recovered_normalized = country_normalizer(df_recovered, 'country')

    # Merging the both the above dataframe on "country" and "date" columns
    df_merged = pd.merge(df_europe_cases_normalized, df_recovered_normalized, on=['country', 'date'])

    return (df_merged, df_europe_cases_normalized)


def date_formatter(input_dataframe, column_name):
    input_dataframe[column_name] = pd.to_datetime(input_dataframe[column_name]).dt.strftime('%Y-%m-%d')
    return (input_dataframe)


def country_normalizer(input_dataframe, column_name):
    normalized_country_df = input_dataframe[input_dataframe[column_name].isin(distinct_europe_countries_list)]
    return(normalized_country_df)