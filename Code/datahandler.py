import sys
import pandas as pd
import datetime

# Initialize the country list
country_intial_df = pd.read_excel("Code/datasets/acaps_covid19_government_measures_dataset_0.xlsx", sheet_name="Database")
european_country_df = country_intial_df[country_intial_df['REGION'] == "Europe"]
distinct_europe_countries_list = european_country_df["COUNTRY"].unique()
govern_restrictions_start_date = "2020-02-20"
data_available_visualization_start_date = "2020-03-10"


def read_data_government_measures(filename):
    gm_df = pd.read_excel(filename, sheet_name="Database")
    european_gn_df = gm_df[gm_df['REGION'] == "Europe"]
    filtered_european_gn_df = european_gn_df.filter(
        ["COUNTRY", "ISO", "REGION", "CATEGORY", "MEASURE", "COMMENTS", "DATE_IMPLEMENTED", "LINK", "SOURCE",
         "SOURCE_TYPE"])
    filtered_columns_df = filtered_european_gn_df.filter(
        ["COUNTRY", "CATEGORY", "MEASURE", "DATE_IMPLEMENTED", "COMMENTS"])

    # category_grouped_df = filtered_columns_df.groupby(['COUNTRY', 'CATEGORY'])
    formatted_data_frame = date_formatter(filtered_columns_df, 'DATE_IMPLEMENTED')
    return (filtered_columns_df)

def read_data_government_restrictions(filename):
    dataSet1 = pd.read_csv(filename)

    # Normalizing the date and countries
    dataSet1 = date_formatter(dataSet1, 'date')
    dataset_country_filtered = country_normalizer(dataSet1, 'CountryName')

    return (dataset_country_filtered)

def read_data_covid_and_recovery(owid_covid_data_file, filename2):
    ## Preparing the owid covid dataframe
    df_world = pd.read_csv(owid_covid_data_file)
    search_df_europe = df_world['continent'] == 'Europe'
    df_europe = df_world[search_df_europe]
    df_europe = df_europe.rename({'location': 'country'}, axis=1)
    df_europe_cases = df_europe.groupby(['date', 'country'])[
        'total_cases', 'total_deaths', 'new_cases', 'new_deaths', 'total_tests'].max()
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
    df_merged_raw = pd.merge(df_europe_cases, df_recovered, on=['country', 'date'])
    df_merged = pd.merge(df_europe_cases_normalized, df_recovered_normalized, on=['country', 'date'])

    return (df_merged, df_merged_raw, df_europe_cases_normalized)


def date_formatter(input_dataframe, column_name):
    
    # Convert the datatype of the column to TimeStamp and format it
    input_dataframe[column_name] = pd.to_datetime(input_dataframe[column_name]).dt.strftime('%Y-%m-%d')

    input_dataframe[column_name] = pd.to_datetime(input_dataframe[column_name])
    # Preparing for filtering the records starting from "consider_records_from_date" variable
    start_date = pd.Timestamp(govern_restrictions_start_date)
    
    #start_date = datetime.datetime.strptime(consider_records_from_date,'%Y-%m-%d') 
    from_start_date = (input_dataframe[column_name] >= start_date)

    # Get the records which are greater than "consider_records_from_date" value
    date_filtered_records = input_dataframe.loc[from_start_date]
    
    return (date_filtered_records)

def country_normalizer(input_dataframe, column_name):
    normalized_country_df = input_dataframe[input_dataframe[column_name].isin(distinct_europe_countries_list)]
    return (normalized_country_df)


def handle_updated_dates(input_dataframe, column_name, slider_input_date_list, number_date_range_dict):
    start_index = slider_input_date_list[0]
    end_index = slider_input_date_list[-1]

    if (start_index == 0) & (end_index == 0):   
        end_index = max(number_date_range_dict, key=number_date_range_dict.get)

    # Fetch the start and end dates from the number_date_range_dict
    start_date = pd.Timestamp(number_date_range_dict.get(start_index))
    end_date = pd.Timestamp(number_date_range_dict.get(end_index))

    # Encode the Date timestamp
    input_dataframe[column_name] = pd.to_datetime(input_dataframe[column_name])
    # .loc[,column_name]

    # Filter the records between Start and End Dates
    # Ref : https://kite.com/python/answers/how-to-filter-pandas-dataframe-rows-by-date-in-python
    from_start_date = input_dataframe[column_name] >= start_date
    until_end_date = input_dataframe[column_name] <= end_date
    between_start_and_end_dates = from_start_date & until_end_date

    # Filtering the dataframe records
    date_filtered_records = input_dataframe.loc[between_start_and_end_dates]

    return (date_filtered_records)


# https://community.plotly.com/t/dash-range-slider-with-date/17915/7
# Preparing the date objects for displaying in slider

def generate_slider_data(input_dataframe, date_column, date_increamentor):

    date_num_encoder = [x for x in range(len(input_dataframe[date_column].unique()))]

    number_date_array = list(
        zip(date_num_encoder, pd.to_datetime(input_dataframe[date_column]).dt.date.unique()))
        
    number_date_range_dict = dict(number_date_array)

    goven_restrict_date = pd.Timestamp(govern_restrictions_start_date)
    data_visualization_date = pd.Timestamp(data_available_visualization_start_date)

    filtered_date_dict = {}
    date_num_filtered_list = []

    for number, date in number_date_range_dict.items():
        if (date == goven_restrict_date) or ((date >= data_visualization_date) and (number % 10 == 9)):
            filtered_date_dict[number] = date.strftime('%b %d, %Y')
            date_num_filtered_list.append(number)
    
    return (date_num_encoder, number_date_range_dict,  filtered_date_dict)

    