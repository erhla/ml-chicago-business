'''
Promoting Sustained Entrepreneurship in Chicago
Machine Learning for Public Policy
University of Chicago, CS & Harris School of Public Policy
June 2019

Rayid Ghani (@rayidghani)
Katy Koenig (@katykoenig)
Eric Langowski (@erhla)
Patrick Lavallee Delgado (@lavalleedelgado)

'''

import os
import ast
import geopandas as gpd
import requests
import shapely
import sqlite3


PWD = os.path.dirname(__file__)
CHICAGO_DB = os.path.join(PWD, "chicago_entrepreneurship_db.sqlite3")
BLOCKS_API = "https://data.cityofchicago.org/resource/bt9m-d2mf.json"
BLOCKS_COLUMNS = (
    "the_geom",
    "geoid10"
)
CRIMES_API = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
CRIMES_COLUMNS = (
    "date",
    "primary_type",
    "arrest",
    "domestic",
    "latitude",
    "longitude"
)
LICENSES_API = "https://data.cityofchicago.org/resource/xqx5-8hwx.json"
LICENSES_COLUMNS = (
    "account_number",
    "site_number",
    "license_code",
    "date_issued",
    "expiration_date",
    "latitude",
    "longitude"
)
CENSUS_API = ("https://api.census.gov/data/", "/acs/acs5?")
CENSUS_COLUMNS = {
    "B01001_002E": "total_male",
    "B01001_003E": "total_male_<5",
    "B01001_004E": "total_male_5-9",
    "B01001_005E": "total_male_10-14",
    "B01001_006E": "total_male_15-17",
    "B01001_007E": "total_male_18-19",
    "B01001_008E": "total_male_20",
    "B01001_009E": "total_male_21",
    "B01001_010E": "total_male_22-24",
    "B01001_011E": "total_male_25-29",
    "B01001_012E": "total_male_30-34",
    "B01001_013E": "total_male_35-39",
    "B01001_014E": "total_male_40-44",
    "B01001_015E": "total_male_45-49",
    "B01001_016E": "total_male_50-54",
    "B01001_017E": "total_male_55-59",
    "B01001_018E": "total_male_60-61",
    "B01001_019E": "total_male_62-64",
    "B01001_020E": "total_male_65-66",
    "B01001_021E": "total_male_67-69",
    "B01001_022E": "total_male_70-74",
    "B01001_023E": "total_male_75-79",
    "B01001_024E": "total_male_80-84",
    "B01001_025E": "total_male_>=85",
    "B01001_026E": "total_female",
    "B01001_027E": "total_female_<5",
    "B01001_028E": "total_female_5-9",
    "B01001_029E": "total_female_10-14",
    "B01001_030E": "total_female_15-17",
    "B01001_031E": "total_female_18-19",
    "B01001_032E": "total_female_20",
    "B01001_033E": "total_female_21",
    "B01001_034E": "total_female_22-24",
    "B01001_035E": "total_female_25-29",
    "B01001_036E": "total_female_30-34",
    "B01001_037E": "total_female_35-39",
    "B01001_038E": "total_female_40-44",
    "B01001_039E": "total_female_45-49",
    "B01001_040E": "total_female_50-54",
    "B01001_041E": "total_female_55-59",
    "B01001_042E": "total_female_60-61",
    "B01001_043E": "total_female_62-64",
    "B01001_044E": "total_female_65-66",
    "B01001_045E": "total_female_67-69",
    "B01001_046E": "total_female_70-74",
    "B01001_047E": "total_female_75-79",
    "B01001_048E": "total_female_80-84",
    "B01001_049E": "total_female_>=85",
    "B08303_001E": "total_commute_time",
    "B08303_002E": "total_commute_<5",
    "B08303_003E": "total_commute_5-9",
    "B08303_004E": "total_commute_10-14",
    "B08303_005E": "total_commute_15-19",
    "B08303_006E": "total_commute_20-24",
    "B08303_007E": "total_commute_25-29",
    "B08303_008E": "total_commute_30-34",
    "B08303_009E": "total_commute_35-39",
    "B08303_010E": "total_commute_40-44",
    "B08303_011E": "total_commute_45-59",
    "B08303_012E": "total_commute_60-89",
    "B08303_013E": "total_commute_>=90",
    "B15012_001E": "total_bachelors_degrees",
    "B03002_001E": "race_respondents",
    "B03002_003E": "race_white",
    "B03002_004E": "race_black",
    "B03002_006E": "race_asian",
    "B03002_012E": "race_hispanic",
    "B19001_001E": "hhinc_respondents",
    "B19001_002E": "hhinc_00_10K",
    "B19001_003E": "hhinc_10_15K",
    "B19001_004E": "hhinc_15_20K",
    "B19001_005E": "hhinc_20_25K",
    "B19001_006E": "hhinc_25_30K",
    "B19001_007E": "hhinc_30_35K",
    "B19001_008E": "hhinc_35_40K",
    "B19001_009E": "hhinc_40_45K",
    "B19001_010E": "hhinc_45_50K",
    "B19001_011E": "hhinc_50_60K",
    "B19001_012E": "hhinc_60_75K",
    "B19001_013E": "hhinc_75_100K",
    "B19001_014E": "hhinc_100_125K",
    "B19001_015E": "hhinc_125_150K",
    "B19001_016E": "hhinc_150_200K"
}

class Entrepreneurship:

    def __init__(self):

        self.dbname = "Chicago Entrepreneurship"


    def open(self):

        self.connection = sqlite3.connect(CHICAGO_DB)
        self.cursor = self.connection.cursor()
    

    def close(self):

        self.connection.close()
    

    def create_blocks_table(self):

        create_blocks_table = '''
        DROP TABLE IF EXISTS blocks;
        CREATE TABLE blocks (
            the_geom            VARCHAR,
            block               NUMERIC
        );
        '''
        self.cursor.executescript(create_blocks_table)
        self.connection.commit()
        self.download_chicago_data(BLOCKS_API, BLOCKS_COLUMNS, "blocks")
    

    def create_crimes_table(self):

        create_crimes_table = '''
        DROP TABLE IF EXISTS crimes;
        CREATE TABLE crimes (
            date                NUMERIC,
            crime               VARCHAR,
            arrest              INTEGER,
            domestic            INTEGER,
            latitude            NUMERIC,
            longitude           NUMERIC
        );
        '''
        self.cursor.executescript(create_crimes_table)
        self.connection.commit()
        self.download_chicago_data(CRIMES_API, CRIMES_COLUMNS, "crimes")
        self.spatial_join_on_blocks("crimes")
    

    def create_licenses_table(self):

        create_licenses_table = '''
        DROP TABLE IF EXISTS licenses;
        CREATE TABLE licenses (
            account_number      INTEGER,
            site_number         INTEGER,
            license_code        VARCHAR,
            issue_date          NUMERIC,
            expiry_date         NUMERIC,
            latitude            NUMERIC,
            longitude           NUMERIC
        );
        '''
        self.cursor.executescript(create_licenses_table)
        self.connection.commit()
        self.download_chicago_data(LICENSES_API, LICENSES_COLUMNS, "licenses")
        self.spatial_join_on_blocks("licenses")


    def download_chicago_data(self, api, columns, table):

        record_count = 0
        record_queue = 1000
        # Request data from Chicago Data Portal.
        while record_count % record_queue == 0:
            request = requests.get(
                api,
                params={
                    "$select": ", ".join(columns),
                    "$offset": record_count,
                    "$limit": record_queue
                }
            )
            new_records = request.json()
            record_count += len(new_records)
            for record in new_records:
                # Read record values into a tuple.
                values = tuple(
                    str(record.get(column))
                    for column in columns
                )
                # Load record values into the table.
                populate_table = f'''
                INSERT INTO {table} 
                VALUES ({", ".join(["?"] * len(values))});
                '''
                self.cursor.execute(populate_table, values)
            self.connection.commit()


    def spatial_join_on_blocks(self, table, commit_interval=100):

        # Alter table to include a block column.
        alter_table = f"ALTER TABLE {table} ADD block NUMERIC;"
        self.cursor.execute(alter_table)
        # Collect census blocks.
        get_blocks = "SELECT * FROM blocks;"
        blocks = gpd.GeoDataFrame(
            self.cursor.execute(get_blocks).fetchall(),
            columns=["the_geom", "block"]
        )
        blocks["the_geom"] = blocks["the_geom"].apply(ast.literal_eval)
        blocks["the_geom"] = blocks["the_geom"].apply(shapely.geometry.shape)
        blocks = blocks.set_geometry("the_geom")
        # Collect record coordinates.
        get_coordinates = f'''
        SELECT DISTINCT latitude, longitude 
        FROM {table} 
        WHERE (latitude IS NOT NULL OR longitude IS NOT NULL)
        AND (latitude IS NOT 'None' OR longitude IS NOT 'None');
        '''
        coordinates = gpd.GeoDataFrame(
            self.cursor.execute(get_coordinates).fetchall(),
            columns=["latitude", "longitude"]
        )
        coordinates["the_geom"] = coordinates.apply(
            lambda x: shapely.geometry.Point(x["longitude"], x["latitude"]),
            axis=1
        )
        coordinates = coordinates.set_geometry("the_geom")
        # Join coordinates and blocks on intersection of their geometry.
        coordinates_blocks = gpd.sjoin(coordinates, blocks)
        for i, row in coordinates_blocks.iterrows():
            # Associate records with these coordiantes to this block.
            update_with_block = f'''
            UPDATE {table} 
            SET block = ? 
            WHERE latitude = ? AND longitude = ?;
            '''
            parameters = (row["block"], row["latitude"], row["longitude"])
            self.cursor.execute(update_with_block, parameters)
            if i % commit_interval == 0:
                self.connection.commit()
        self.connection.commit()


    def create_census_table(self, year):

        create_census_table = f'''
        DROP TABLE IF EXISTS census;
        CREATE TABLE census (
            start_year              NUMERIC,
            end_year                NUMERIC,
            total_male              NUMERIC, 
            total_male_<5           NUMERIC, 
            total_male_5-9          NUMERIC, 
            total_male_10-14        NUMERIC, 
            total_male_15-17        NUMERIC, 
            total_male_18-19        NUMERIC, 
            total_male_20           NUMERIC, 
            total_male_21           NUMERIC, 
            total_male_22-24        NUMERIC, 
            total_male_25-29        NUMERIC, 
            total_male_30-34        NUMERIC, 
            total_male_35-39        NUMERIC, 
            total_male_40-44        NUMERIC, 
            total_male_45-49        NUMERIC, 
            total_male_50-54        NUMERIC, 
            total_male_55-59        NUMERIC, 
            total_male_60-61        NUMERIC, 
            total_male_62-64        NUMERIC, 
            total_male_65-66        NUMERIC, 
            total_male_67-69        NUMERIC, 
            total_male_70-74        NUMERIC, 
            total_male_75-79        NUMERIC, 
            total_male_80-84        NUMERIC, 
            total_male_>=85         NUMERIC, 
            total_female            NUMERIC, 
            total_female_<5         NUMERIC, 
            total_female_5-9        NUMERIC, 
            total_female_10-14      NUMERIC, 
            total_female_15-17      NUMERIC, 
            total_female_18-19      NUMERIC, 
            total_female_20         NUMERIC, 
            total_female_21         NUMERIC, 
            total_female_22-24      NUMERIC, 
            total_female_25-29      NUMERIC, 
            total_female_30-34      NUMERIC, 
            total_female_35-39      NUMERIC, 
            total_female_40-44      NUMERIC, 
            total_female_45-49      NUMERIC, 
            total_female_50-54      NUMERIC, 
            total_female_55-59      NUMERIC, 
            total_female_60-61      NUMERIC, 
            total_female_62-64      NUMERIC, 
            total_female_65-66      NUMERIC, 
            total_female_67-69      NUMERIC, 
            total_female_70-74      NUMERIC, 
            total_female_80-84      NUMERIC, 
            total_female_75-79      NUMERIC, 
            total_female_>=85       NUMERIC, 
            total_commute_time      NUMERIC, 
            total_commute_<5        NUMERIC, 
            total_commute_5-9       NUMERIC, 
            total_commute_10-14     NUMERIC, 
            total_commute_15-19     NUMERIC, 
            total_commute_20-24     NUMERIC, 
            total_commute_25-29     NUMERIC, 
            total_commute_30-34     NUMERIC, 
            total_commute_35-39     NUMERIC, 
            total_commute_40-44     NUMERIC, 
            total_commute_45-59     NUMERIC, 
            total_commute_60-89     NUMERIC, 
            total_commute_>=90      NUMERIC, 
            total_bachelors_degrees NUMERIC, 
            race_respondents        NUMERIC, 
            race_white              NUMERIC, 
            race_black              NUMERIC, 
            race_asian              NUMERIC, 
            race_hispanic           NUMERIC, 
            hhinc_respondents       NUMERIC, 
            hhinc_00_10K            NUMERIC, 
            hhinc_10_15K            NUMERIC, 
            hhinc_15_20K            NUMERIC, 
            hhinc_20_25K            NUMERIC, 
            hhinc_25_30K            NUMERIC, 
            hhinc_30_35K            NUMERIC, 
            hhinc_35_40K            NUMERIC, 
            hhinc_40_45K            NUMERIC, 
            hhinc_45_50K            NUMERIC, 
            hhinc_50_60K            NUMERIC, 
            hhinc_60_75K            NUMERIC, 
            hhinc_75_100K           NUMERIC, 
            hhinc_100_125K          NUMERIC, 
            hhinc_125_150K          NUMERIC, 
            hhinc_150_200K          NUMERIC, 
            block                   NUMERIC
        );
        '''
        print(create_census_table)
        # self.cursor.executescript(create_census_table)
        # self.connection.commit()
        # self.download_chicago_data(CENSUS_API, year, CENSUS_API, "census")

    
    def download_census_data(self, api, year, columns, table):

        request = requests.get(
            api[0] + str(year) + api[1],
            params={
                "get": ",".join(columns.keys()),
                "for": "block group:*",
                "in": "state:17 county:031"
            }
        )
        new_records = request.json()
        for i, record in enumerate(new_records):
            # Skip header row.
            if i == 0:
                continue
            # Infer block and period from data.
            block = ["".join(record[len(record) - 4:])]
            period = [year, year - 4]
            # Read record values into a tuple.
            values = tuple(period + record[:len(record) - 4] + block)
            # Load record values into the table.
            populate_table = f'''
            INSERT INTO {table} 
            VALUES ({", ".join(["?"] * len(values))});
            '''
            self.cursor.execute(populate_table, values)
        self.connection.commit()
