import init
import constants as cn
from index_base_class import IndexBase
from trip import Trip

import pandas as pd

from collections import defaultdict


class ModeChoiceCalculator(IndexBase):
    """
    
    """
    def __init__(self, car_time_threshold=cn.CAR_TIME_THRESHOLD, bike_time_threshold=cn.BIKE_TIME_THRESHOLD, 
        transit_time_threshold=cn.TRANSIT_TIME_THRESHOLD, walk_time_threshold=cn.WALK_TIME_THRESHOLD):

        self.car_time_threshold = car_time_threshold
        self.bike_time_threshold = bike_time_threshold
        self.transit_time_threshold = transit_time_threshold
        self.walk_time_threshold = walk_time_threshold

        pass

    def is_viable(self, trip):
        """
        This function takes in a Trip and returns a value indicating whether a trip is viable (1) or
        not viable (0) as a fuction of trip.mode and trip.duration.
        """


        # We might need to adjust this such that it operates on DF rows,
        # not Trip objects.
        viable = 0
        if trip.mode == cn.CAR and trip.duration < self.car_time_threshold:
            viable = 1
        elif trip.mode == cn.BIKE and trip.duration < self.bike_time_threshold:
            viable = 1
        elif trip.mode == cn.TRANSIT and trip.duration < self.transit_time_threshold:
            viable = 1
        elif trip.mode == cn.WALK and trip.duration < self.walk_time_threshold:
            viable = 1

            #can we take into account proximity? thinking of nearby locations with bad connections
            # or disnant locations with good connections. Most relevant for bus.

        
        return viable

    
    def trip_from_row(self, row):
        """
        Given a dataframe with the available variables, create a trip class 
        with these variables. Returns trip.
        """

        origin = row[cn.BLOCK_GROUP] 
        destination = row[cn.DESTINATION] 
        mode = row[cn.MODE]
        distance = row[cn.DISTANCE]
        duration = row[cn.DURATION]
        # the attributes initiated to None is because we currently don't have 
        # them. We might need to revise the trip class to eliminate them or the data to have
        # the necesary data.
        basket_category = None
        pair = None
        #convert departure time to date-time object
        departure_time = row[cn.DEPARTURE_TIME]
        rank = None

        # This is going to change. 
        trip = Trip(trip_id, origin, destination, mode, distance, duration, basket_category, 
            pair, departure_time, rank)
        return trip

    
    def create_blockgroup_dict(self, df):

        """
        this function assumes that the df has a column for trip viability
        """
        blkgrp_dict = defaultdict(list)
        for _, row in df.iterrows():
            trip = self.trip_from_row(row)
            blkgrp = trip.origin
            viable= row[cn.VIABLE]
            #need a way to add viable to trip
            blkgrp_dict[blkgrp].append(trip)

        return blkgrp_dict


    def calculate_mode_avail(self, trips):
        """
        Input: trips (list of Trips)
        Output: mode index for the list of trips as a function of viability

        """
        #make sure trip has viable attribute
        # Hours of data availability, HOURS constant should be float
        mode_avail = sum([trip.viable for trip in trips])
        mode_index = mode_aval/cn.TRAVEL_HOURS #(?) name constant

        return mode_index



    def create_availability_csv(self, blkgrp_dict):
        """
        Takes in a blockgroup dictionary where blokgroups are keys and list of trips from
        that blockgroups are corresponding values, estimates the availability score for each blockroup
        and returns the csv with each block group's mobility score.

        """
        data = []
        for blkgrp, trips in blkgrp_dict.items():
            mode_index= calculate_mode_avail(trips)
            row={ cn.BLOCK_GROUP: blkgrp, cn.MODE_CHOICE_INDEX: mode_index}
            data.append(row)
        df = pd.DataFrame(data)

        df.to_csv(cn.MODE_CHOICE_FP)

# time of day weight for modes. Walking dependent of time of day, dark or not.
# need to cary things?
# elevation?
