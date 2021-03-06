import geopandas as gpd
import numpy as np
from shapely.geometry import shape, Point
import shapely.wkt
import pandas as pd
import csv
from dateutil.relativedelta import relativedelta
from datetime import datetime


def process_census(acs_csv='acs_13.csv'):
    '''
    Reads in the ACS census data from csv, creating bins for specified features
    and finds percentages for these features

    Inputs: 
        acs_csv: a csv of American Community Survey data

    Output: a pandas dataframe of desired ACS columns
    '''
    df = pd.read_csv(acs_csv)

    agg_dict = {'male_children': ['Estimate!!Total!!Male!!Under 5 years', 'Estimate!!Total!!Male!!5 to 9 years',
                                  'Estimate!!Total!!Male!!10 to 14 years', 'Estimate!!Total!!Male!!15 to 17 years'],
                'male_working': ['Estimate!!Total!!Male!!18 and 19 years', 'Estimate!!Total!!Male!!20 years',
                                 'Estimate!!Total!!Male!!21 years', 'Estimate!!Total!!Male!!22 to 24 years',
                                 'Estimate!!Total!!Male!!25 to 29 years', 'Estimate!!Total!!Male!!30 to 34 years',
                                 'Estimate!!Total!!Male!!35 to 39 years', 'Estimate!!Total!!Male!!40 to 44 years',
                                 'Estimate!!Total!!Male!!45 to 49 years', 'Estimate!!Total!!Male!!50 to 54 years',
                                 'Estimate!!Total!!Male!!55 to 59 years', 'Estimate!!Total!!Male!!60 and 61 years',
                                 'Estimate!!Total!!Male!!62 to 64 years'], 
                'male_elderly': ['Estimate!!Total!!Male!!65 and 66 years', 'Estimate!!Total!!Male!!67 to 69 years', 
                                 'Estimate!!Total!!Male!!70 to 74 years', 'Estimate!!Total!!Male!!75 to 79 years', 
                                 'Estimate!!Total!!Male!!80 to 84 years', 'Estimate!!Total!!Male!!85 years and over'],
                'female_children': ['Estimate!!Total!!Female!!Under 5 years', 'Estimate!!Total!!Female!!5 to 9 years',
                                   'Estimate!!Total!!Female!!10 to 14 years', 'Estimate!!Total!!Female!!15 to 17 years'],
                'female_working': ['Estimate!!Total!!Female!!18 and 19 years', 'Estimate!!Total!!Female!!20 years',
                                   'Estimate!!Total!!Female!!21 years', 'Estimate!!Total!!Female!!22 to 24 years', 
                                   'Estimate!!Total!!Female!!25 to 29 years', 'Estimate!!Total!!Female!!30 to 34 years', 
                                   'Estimate!!Total!!Female!!35 to 39 years', 'Estimate!!Total!!Female!!40 to 44 years', 
                                   'Estimate!!Total!!Female!!45 to 49 years', 'Estimate!!Total!!Female!!50 to 54 years',
                                   'Estimate!!Total!!Female!!55 to 59 years', 'Estimate!!Total!!Female!!60 and 61 years', 
                                   'Estimate!!Total!!Female!!62 to 64 years'],
                'female_elderly': ['Estimate!!Total!!Female!!65 and 66 years', 'Estimate!!Total!!Female!!67 to 69 years', 
                                   'Estimate!!Total!!Female!!70 to 74 years', 'Estimate!!Total!!Female!!75 to 79 years', 
                                   'Estimate!!Total!!Female!!80 to 84 years', 'Estimate!!Total!!Female!!85 years and over'],
                'low_travel_time': ['Estimate!!Total!!Less than 5 minutes', 'Estimate!!Total!!5 to 9 minutes', 
                                      'Estimate!!Total!!10 to 14 minutes', 'Estimate!!Total!!15 to 19 minutes', 
                                      'Estimate!!Total!!20 to 24 minutes'],
                'med_travel_time': ['Estimate!!Total!!25 to 29 minutes', 'Estimate!!Total!!30 to 34 minutes', 
                                    'Estimate!!Total!!35 to 39 minutes', 'Estimate!!Total!!40 to 44 minutes', 
                                    'Estimate!!Total!!45 to 59 minutes'],
                'high_travel_time': ['Estimate!!Total!!60 to 89 minutes', 'Estimate!!Total!!90 or more minutes'],
                'below_pov': ['hhinc_00_10K', 'hhinc_10_15K', 'hhinc_15_20K', 'hhinc_20_25K'],
                'below_med': ['hhinc_25_30K', 'hhinc_30_35K', 'hhinc_35_40K', 'hhinc_40_45K', 'hhinc_45_50K', 'hhinc_50_60K'],
                'above_med': ['hhinc_60_75K', 'hhinc_75_100K'],
                'high_inc': ['hhinc_100_125K', 'hhinc_125_150K', 'hhinc_150_200K']}

    denoms = {'total_male': 'Estimate!!Total!!Male',
              'total_female': 'Estimate!!Total!!Female',
              'total_travel_time': 'Estimate!!Total_x',
              'total_inc': 'hhinc_respondents'}

    desired_cols = ['block_group']
    for col_name, col_list in agg_dict.items():
        if col_name in ['male_children', 'male_working', 'male_children']:
            denom = denoms['total_male']
        if col_name in ['female_children', 'female_working', 'female_children']:
            denom = denoms['total_female']
        if col_name in ['low_travel_time', 'med_travel_time', 'high_travel_time']:
            denom = denoms['total_travel_time']
        if col_name in ['below_pov', 'below_med', 'above_med', 'high_inc']:
            denom = denoms['total_inc']
        new_col = 'pct_' + col_name
        df[new_col] = df[col_list].agg('sum', axis=1) / df[denom] * 100
        desired_cols.append(new_col)
    for col in ['race_white', 'race_black', 'race_asian']:
        new_col = 'pct_' + col
        df[new_col] = df[col] / df['race_respondents'] * 100
        desired_cols.append(new_col)
    df['total_pop'] = df[denoms['total_male']] + df[denoms['total_female']]
    desired_cols.append('total_pop')
    df['block_group'] = df['block_group'].astype(str)
    return df[desired_cols]


DATE_LST =['earliest_issue', 'latest_issue']
def clean_types(dataframe, date_cols=DATE_LST):
    '''
    Used to clean the business data when imported from csv
    '''
    
    dataframe['block_group'] = dataframe['block_group'].astype(str)
    for d_col in date_cols:
        dataframe[d_col] = pd.to_datetime(dataframe[d_col], infer_datetime_format=True, errors='coerce')
    drop_lst = []
    for column in dataframe.columns: 
        if 'crime' in column: 
            drop_lst.append(column)
        if 'license' in column:
            drop_lst.append(column)
    dataframe.fillna(0, inplace=True)
    dataframe = dataframe.drop(drop_lst, axis=1)
    dataframe['census_tract'] = dataframe['block_group'].str[:11]
    return dataframe



CRIMES_LS = ['HOMICIDE', 'OTHER OFFENSE', 'ROBBERY', 'THEFT', 'NARCOTICS',
       'BATTERY', 'ASSAULT', 'CRIMINAL DAMAGE', 'CRIMINAL TRESPASS',
       'PUBLIC PEACE VIOLATION', 'MOTOR VEHICLE THEFT',
       'DECEPTIVE PRACTICE', 'WEAPONS VIOLATION',
       'INTERFERENCE WITH PUBLIC OFFICER', 'BURGLARY',
       'CRIM SEXUAL ASSAULT', 'OFFENSE INVOLVING CHILDREN',
       'PUBLIC INDECENCY', 'SEX OFFENSE', 'KIDNAPPING', 'PROSTITUTION',
       'INTIMIDATION', 'ARSON', 'LIQUOR LAW VIOLATION',
       'CONCEALED CARRY LICENSE VIOLATION', 'GAMBLING',
       'OTHER NARCOTIC VIOLATION', 'STALKING', 'OBSCENITY',
       'HUMAN TRAFFICKING', 'NON-CRIMINAL',
       'NON-CRIMINAL (SUBJECT SPECIFIED)', 'NON - CRIMINAL']

def crime_stats_for_date_range(crimes, start, end):
    small = crimes[(crimes['Date'] >= start) & (crimes['Date'] <= end)]
    grouped = small.groupby('block_group')
    dic = {}
    length = (pd.to_datetime(end) - pd.to_datetime(start)).days

    for block, df in grouped:
        tmp = []
        size = df.shape[0] / length
        arrests = df[df['Arrest'] == True].shape[0] / length
        domestic = df[df['Domestic'] == True].shape[0] / length
        for crime_type in CRIMES_LS:
            tmp = tmp + [df[df['Primary Type'] == crime_type].shape[0] / length]
        tmp = tmp + [size, arrests, domestic]
        dic[str(block).replace('.0', '')] = tmp  
    cols = CRIMES_LS + ['Total_Crimes', 'Total_Arrests', 'Total_Domestic']
    return pd.DataFrame.from_dict(dic, orient='index', columns=cols)


KEEP_COLS = ['Date', 'Primary Type', 'Latitude', 'Longitude', 'Domestic', 'Arrest']
def process_crime(blocks_df, date_col, col_lst=KEEP_COLS):
    '''
    '''
    crime_df = pd.read_csv('crimes.csv', parse_dates=['Date'], infer_datetime_format=True, keep_date_col=True)
    crime_df = crime_df[col_lst]
    #start_time = business_df['earliest_issue'].min()
    #end_time = business_df['earliest_issue'].max()
    #crime_df = crime_df[(crime_df['Date'] >= start_time) \
    #                        & (crime_df['Date'] <= end_time)]
    crime_df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    blocks_df = gpd.GeoDataFrame(blocks_df, geometry='the_geom')
    crime_df["the_geom"] = crime_df.apply(lambda row: Point(float(row["Longitude"]), float(row["Latitude"])), axis=1)
    crime_gdf = gpd.GeoDataFrame(crime_df).set_geometry("the_geom")
    joined = gpd.sjoin(crime_gdf, blocks_df, how="left", op='intersects').drop(columns="index_right")
    #Finds percentage of each type of crime and total number of crimes per block group
    type_grouped = joined.groupby('block_group')['Primary Type'].value_counts().unstack(fill_value=0)
    type_pct = type_grouped.div(type_grouped.sum(axis=1), axis=0)  
    type_pct['total'] = type_grouped.sum(axis=1)
    # Finds the percentage of Domestic & Arrests (via mean)
    means = joined.groupby('block_group').mean()
    # Combines 3 grouped dataframes
    combined = pd.merge(type_pct, means, on='block_group')
    combined = combined.loc[:, ~combined.columns.isin(['Latitude', 'Longitude', 'Date'])]

    total_df.drop(columns='block', inplace=True)
    return total_df


def add_crimes(train_df, test_df, train_name, test_name):
    trainsplt = train_name.split('_')[1:]
    testsplt = test_name.split('_')[1:]
    crimes = pd.read_csv('data/reduced_crimes.csv', parse_dates=['Date'], infer_datetime_format=True, keep_date_col=True)
    train_crimes = crime_stats_for_date_range(crimes, pd.to_datetime(trainsplt[0]) - pd.Timedelta('365 d'), pd.to_datetime(trainsplt[1][:-4]))
    test_crimes = crime_stats_for_date_range(crimes, pd.to_datetime(testsplt[0]) - pd.Timedelta('365 d'), pd.to_datetime(testsplt[1][:-4]))

    return train_df.merge(train_crimes, left_on='block_group', right_index=True), test_df.merge(test_crimes, left_on='block_group', right_index=True)



col_types = {'ACCOUNT NUMBER': str, 'SITE NUMBER': int, 'LICENSE CODE': str,
             'ADDRESS': str, 'APPLICATION TYPE': str, 
             'APPLICATION REQUIREMENTS COMPLETE': str,
             'LICENSE TERM START DATE': str , 'LICENSE STATUS' : str,
             'LICENSE TERM EXPIRATION DATE': str, 'DATE ISSUED': str,
             'LONGITUDE': str, 'LATITUDE': str}

def process_business():
    '''
    Reads in business license csv and specifies necessary columns and their
    types

    Inputs: None

    Outputs: a pandas dataframe
    '''
    df = pd.read_csv('business.csv', usecols=list(col_types.keys()), dtype=col_types,
                     parse_dates=['APPLICATION REQUIREMENTS COMPLETE',
                     'LICENSE TERM START DATE', 'LICENSE STATUS',
                     'LICENSE TERM EXPIRATION DATE', 'DATE ISSUED'], infer_datetime_format=True)
    df['unique_id'] = df['ACCOUNT NUMBER'].astype('str') + '-' + df['SITE NUMBER'].astype('str')
    #find_duration(df, 'DATE ISSUED', 'APPLICATION REQUIREMENTS COMPLETE')
    return df


# will take forever to run: I uploaded to CSV to our repo so just download that
def make_bus(bus_df, filename='cleanedbus.csv'):
    to_write = {new: [] for new in ['unique_id', 'latitude', 'longitude', 'earliest_date_issued', 'latest_date_issued', 'latest_exp_date']}  
    with open(filename, 'w') as csvfile:
        outputwriter = csv.writer(csvfile, delimiter=',')
        top_codes = bus_df.groupby('LICENSE CODE').size().sort_values(ascending=False)[:20]
        header = ['unique_id', 'latitude', 'longitude', 'earliest_date_issued', 'latest_date_issued', 'latest_exp_date'] + list(top_codes.index)
        outputwriter.writerow(header)
        for bus_id in bus_df['unique_id'].unique():
            relevant = bus_df[bus_df['unique_id'] == bus_id]
            earliest_issued = relevant['LICENSE TERM START DATE'].min()
            latest_issued = relevant['LICENSE TERM START DATE'].max()
            latest_exp = relevant['LICENSE TERM EXPIRATION DATE'].max()
            lat = relevant['LATITUDE'].iloc[-1]
            lon = relevant['LONGITUDE'].iloc[-1]
            row = [bus_id, lat, lon, earliest_issued, latest_issued, latest_exp]
            for code in list(top_codes.index):
                if code in list(relevant['LICENSE CODE']):
                    row.append(1)
                else:
                    row.append(0)
            outputwriter.writerow(row)
    csvfile.close()



def find_duration(df, col1, col2):
    '''
    Calculates the amount of days that have passed between two columns

    Inputs: 
        df: a pandas dataframe
        col1: column name of dataframe
        col2: column name of dataframe

    '''
    diff = df[col2] - df[col1]
    df['days_between_' + col1 + "_" + col2] = diff.dt.days


def check_alive(df, date):
    '''
    Checks to see if business still open after given date and gives the
    following encoding for a new column in the dataframe ('status'):
        0: closed
        1: open
    
    Inputs:
        df: a pandas dataframe
        date: a datetime object

    Outputs: None
    '''
    df["status"] = df['latest_exp_date'] > date
    df['status'] = df['status'].astype(int)


def process_blocks():
    '''
    '''
    df = pd.read_csv('blocks.csv')
    df['GEOID10'] = df['GEOID10'].astype(str)
    df["block_group"] = df["GEOID10"].apply(lambda block: block[:12])
    df["the_geom"] = df["the_geom"].apply(shapely.wkt.loads)
    gdf = gpd.GeoDataFrame(df).set_geometry("the_geom").drop(columns=df.columns.difference(["block_group", "the_geom"]))
    gdf = gpd.GeoDataFrame(gdf).set_geometry('the_geom')
    return gdf


# Join blocks and census first so we can impute the zeros for census data prior to join w/ business_df

def join_chiblocks_census(census_df, blocks_df):
    '''
    Joins the ACS data with the Chicago block groups data and fills any nulls with zeros.
    (nulls are due to no population)
    '''
    joined = pd.merge(census_df, blocks_df, on='block_group', how="outer")
    return joined.fillna(value=0)


def join_with_block_groups(business_df, blocks_df):
    '''
    '''
    blocks_df = gpd.GeoDataFrame(blocks_df, geometry='the_geom')
    business_df = business_df.dropna(subset=["longitude", "latitude"])
    business_df["the_geom"] = business_df.apply(lambda row: Point(float(row["longitude"]), float(row["latitude"])), axis=1)
    business_gdf = gpd.GeoDataFrame(business_df).set_geometry("the_geom")
    joined_data = gpd.sjoin(business_gdf, blocks_df, how="left", op='intersects').drop(columns="index_right")
    return joined_data


def find_alive_neighbors(df):
    '''
    Finds current number of businesses within a block group
    '''
    df["num_open_bus"] = df.groupby('block_group')['status'].transform('sum')


def length_alive(df):
    df['days_alive'] = (df['latest_exp_date'] - df['earliest_date_issued']).dt.days

# # COLUMN_NAMES = ['APPLICATION TYPE',  'LICENSE DESCRIPTION']
# def breakdown_by_blck_grp(df, col):
#     '''
#     Finds percentage breakdown for each type of a given column for each block group 
#     e.g. what's the percentage of renewals in this blk group?
#     '''
#     val_lst = list(df[col].unique())
#     grouped = df.groupby('block_group')[col].value_counts().unstack(fill_value=0)
#     pct = grouped[val_lst].div(grouped.sum(axis=1), axis=0)*100
#     return pct.reset_index()


# do we want to include anything not issue/renew?
# we could also do axis=0 for the .sum to get a comparison across block groups
