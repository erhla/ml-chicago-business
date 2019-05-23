'''
Promoting Sustained Entrepreneurship in Chicago
Machine Learning for Public Policy
University of Chicago, CS & Harris School of Public Policy
May 2019

Rayid Ghani (@rayidghani)
Katy Koenig (@katykoenig)
Eric Langowski (@erhla)
Patrick Lavallee Delgado (@lavalleedelgado)

'''

import os
import pandas as pd
import requests
import sqlite3

PWD = os.path.dirname(__file__)
CHICAGO_STOREFRONTS_DB = os.path.join(PWD, "chicago_storefronts_db.sqlite3")
CHICAGO_LICENSES_API = "https://data.cityofchicago.org/resource/xqx5-8hwx.json"
CHICAGO_LICENSES_COLUMNS = (
    "account_number,"
    "site_number,"
    "license_code,"
    "date_issued,"
    "expiration_date,"
    "latitude,"
    "longitude"
)


class Storefronts:

    def __init__(self):

        self.dbname = "Chicago Storefronts"


    def open(self):

        self.connection = sqlite3.connect(CHICAGO_STOREFRONTS_DB)
        self.cursor = self.connection.cursor()
    

    def close(self):

        assert self.connection
        self.connection.close()
    

    def create_licences_table(self):

        create_licences_table = '''
        DROP TABLE IF EXISTS licenses;
        CREATE TABLE licenses (
            account_number      INTEGER,
            site_number         INTEGER,
            license_code        VARCHAR(255),
            issue_date          TIMESTAMP,
            expiry_date         TIMESTAMP,
            latitude            FLOAT,
            longitude           FLOAT
        );
        '''
        self.cursor.executescript(create_licences_table)
        self.connection.commit()
    

    def populate_licenses_table(self):

        record_count = 0
        record_queue = 1000
        while record_count % record_queue == 0:
            request = requests.get(
                CHICAGO_LICENSES_API,
                params={
                    "$select": CHICAGO_LICENSES_COLUMNS,
                    "$offset": record_count,
                    "$limit": record_queue
                }
            )
            new_licenses = request.json()
            record_count += len(new_licenses)
            for new_license in new_licenses:
                new_values = (
                    new_license.get("account_number"),
                    new_license.get("site_number"),
                    new_license.get("license_code"),
                    new_license.get("date_issued"),
                    new_license.get("expiration_date"),
                    new_license.get("latitude"),
                    new_license.get("longitude")
                )
                populate_licenses_table = '''
                INSERT INTO licenses VALUES (?, ?, ?, ?, ?, ?, ?);
                '''
                self.cursor.execute(populate_licenses_table, new_values)
            self.connection.commit()


    def create_storefronts_table(self):

        create_storefronts_table = '''
        DROP TABLE IF EXISTS storefronts;
        CREATE TABLE storefronts (
            sf_id               VARCHAR,
            earliest_issue      TIMESTAMP,
            latest_issue        TIMESTAMP,
            latitude            NUMERIC,
            longitude           NUMERIC
        );
        '''
        self.cursor.executescript(create_storefronts_table)
        self.connection.commit()


    def populate_storefronts_table(self):

        populate_storefronts_table = '''
        WITH
            sf_ids_aggs AS (
                SELECT 
                    account_number,
                    site_number, 
                    MIN(issue_date) AS earliest_issue, 
                    MAX(expiry_date) AS latest_issue
                FROM licenses 
                GROUP BY account_number, site_number
            ), 
            sf_ids_locs AS (
                SELECT
                    account_number, 
                    site_number, 
                    latitude, 
                    longitude, 
                    RANK() OVER (
                        PARTITION BY account_number, site_number 
                        ORDER BY issue_date DESC
                    ) AS last_location 
                FROM licenses 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL 
            ), 
            sf_ids_complete AS (
                SELECT 
                    account_number || '-' || site_number AS sf_id, 
                    earliest_issue, 
                    latest_issue, 
                    latitude, 
                    longitude 
                FROM sf_ids_aggs 
                JOIN sf_ids_locs USING (account_number, site_number) 
                WHERE last_location = 1 
            ) 
        INSERT INTO storefronts SELECT * FROM sf_ids_complete;
        '''
        self.cursor.executescript(populate_storefronts_table)
        self.connection.commit()

