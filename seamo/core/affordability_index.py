import init
import index_base_class
import pandas as pd
import constants as cn
import support.trip as tp
import support.data_accessor as daq

class AffordabilityIndex(index_base_class):
    DATADIR = cn.CSV_DIR #db dir?

    def __init__(self, time_of_day, type_of_day, travel_mode,
        db_name=cn.GOOGLE_DIST_MATRIX_OUT, datadir=DATADIR, travel_cost):
        super().__init__(self, time_of_day, type_of_day, travel_mode,
            db_name=cn.GOOGLE_DIST_MATRIX_OUT, datadir=DATADIR)
        self.travel_cost = travel_cost
        self.median_income_data = self.get_csv_data(cn.CENSUS_DATA_FNAME) #replace with actual constant name
        self.trip_data = self.get_sql_data()


    def get_csv_data(self, filename, datadir=DATADIR):
        df = pd.read_csv(str(filename) + '.csv')
        return df

    def get_sql_data(self, filename, datadir=DATADIR):
        df = daq.sql_to_df()
        return df


    def calculate_score(self):
        trips = [] # will be a list of trip objects
        for row in range(len(viable_modes)):
            # this syntax functions like a switch-case statement in java,
            # see: https://simonwillison.net/2004/May/7/switch/
            mode = {0: lambda row: cn.CAR,
                    1: lambda row: cn.TRANSIT,
                    2: lambda row: cn.BIKE,
                    3: lambda row: cn.WALK}[row % 4](row)
            if viable_modes[row] == 1:
                trips.append(self.define_trip(mode, row))

        blkgrp_trip_cost = sum(trip1, trip2) / num_trips
        normalized = normalize(blkgrp_trip_cost)

        income_adjusted = blkgrp_trip_cost / income
        income_normalized = normalize(income_adjusted)

        return normalized, income_normalized


