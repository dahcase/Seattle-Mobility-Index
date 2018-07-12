# coding: utf-8
"""
Basket Destination Calculator

This script constructs a market basket of destinations relevant to people
who travel in Seattle. The basket may nearby points of interest and activity
centers that are specific to each origin, and citywide destinations
that are the same for all starting points. 

https://public.tableau.com/views/Basket_of_Destinations/Dashboard?:embed=y&:display_count=yes

This script accesses the Google Map Distance Matrix API and ranks each
possible origin-destination pair by their driving distance.
The basket definition is created by using parameters to filter each
class of destination.
"""
import json
from urllib.request import Request, urlopen

import pandas as pd

import __init__
import constants as cn


class Coordinate:
    """
    Coordinate class.
    """
    def __init__(self, lat, lon):
        """
        Initialize with a latitude and a longitude.
        """
        self.lat = lat
        self.lon = lon


    def __str__(self):
        """
        Format is 'lat,lon'
        """
        return "{0},{1}".format(self.lat, self.lon)

    def calculate_distance(self, coordinate):
        """
        Calculate the distance between two coordinates
        """
        return distance

class BasketCalculator:

    origin_df = pd.read_csv(cn.ORIGIN_FP)
    dest_df = pd.read_csv(cn.DEST_FP)

    def __init__(self, api_key):
        """
        Initialize BasketCalculator with an API key.
       
        Inputs: api_key (string)
        """
        self.api_key = api_key


    def origins_to_distances(self, origin_df=origin_df, dest_df=dest_df):
        """
        For every origin, store the distance to every destination in the
        full basket of destinations. Distance is calculated via the Google
        Distance Matrix API.

        Inputs: origin_df (dataframe), dest_df (dataframe)
        Outputs: dist_df (dataframe)
       
        """
        dist_matrix = []
        for i, row in origin_df.iterrows():
            blockgroup = row[cn.BLOCKGROUP]
            origin = Coordinate(row[cn.CENSUS_LAT], row[cn.CENSUS_LON])
            distances = self.calculate_distance_to_basket(origin, dest_df)
            for place_id, data in distances.items():
                distance = data[cn.DISTANCE]
                dest_class = data[cn.CLASS]
                pair = "{0}-{1}".format(blockgroup, place_id)
                dist_matrix.append([pair, distance, dest_class])

        dist_df = pd.DataFrame(dist_matrix, columns=[cn.PAIR, cn.DISTANCE, cn.CLASS])
   
        # rank it by proximity
        dist_df = self.rank_destinations(dist_df)

        return dist_df


    def rank_destinations(self, dist_df):
        """
        For each blockgroup, rank destinations by class for proximity.

        Input: dataframe
        Output: dataframe with an added 'rank' column
        """
        # Group by blockgroup and destination class
        grouped = dist_df.groupby([cn.BLOCKGROUP, cn.CLASS])
        # Rank by proximity (closest is highest)
        dist_df[cn.RANK] = grouped[cn.DISTANCE].rank(
            ascending=True, method='first')
        return dist_df


    def calculate_distance_API(self, origin, destination):
        """
        Calculate the distance between an origin and destination pair.
        Calls Google Distance Matrix API.
   
        Input:  origin (Coordinate)
                destination (Coordinate)
        Output: distance in miles (int)
        """
        distance = 0

        url = cn.DIST_MATRIX_URL +\
              'units={0}'.format(cn.IMPERIAL_UNITS) +\
              '&mode={0}'.format(cn.DRIVING_MODE) +\
              '&origins={0}'.format(str(origin)) +\
              "&destinations={0}".format(str(destination)) +\
              "&key={0}".format(self.api_key)
        request = Request(url)
        try:
            response = urlopen(request).read()
        except:
            raise Exception("Couldn't open link.") 

        data = json.loads(response)

        if data['status'] != 'OK':
            message = data['error_message']
            raise Exception(message)
            # Going to make a SeamoError type.
        else:
            elements = data['rows'][0]['elements']
            element = elements[0]
            if element['status'] == 'NOT_FOUND':
                # If the origin-destination pair is not found, should write to a log.
                raise Exception('Could not find the distance for that pair.') 
            elif element['status'] == 'OK':
                distance = element['distance']['value']

        return distance


    def calculate_distance_haversine(self, origin, destination):
        """
        Calculate haversine distance between two points
        """
        return distance

    def calculate_distance_to_basket(self, origin, dest_df):
        """Calculate the distance (and travel time) to each destination
        and produce a CSV file of the data.
        This calls the Google Matrix API.

        Inputs:
            origin (Coordinate)
            dest_df (DataFrame)
        Output:
            distances (dict)

        """
        distances = {}

        for index, row in dest_df.iterrows():
            destination = Coordinate(row[cn.GOOGLE_PLACES_LAT],
                                     row[cn.GOOGLE_PLACES_LON])
            dest_class = row[cn.CLASS]
            place_id = row[cn.PLACE_ID]

            distance = self.calculate_distance(origin, destination)
            if distance:
                # Store the distance and the class of destination
                distances[cn.PLACE_ID] = { cn.DISTANCE: distance,
                                           cn.CLASS: dest_class }

        return distances


    def create_basket(self, dist_df, basket_combination):
        """
        Given a list of integers denoting counts for basket categories
        and a dataframe of origin-destination pairs with each destination for 
        each class ranked by proximity to the origin, create a basket of 
        destinations for each blockgroup.

        Input: dist_df (dataframe), basket_combination (list)
        Output: dataframe
        """
        # A list to store intermediate dataframes organized by destination class
        dfs_by_class = []
        
        for i, category in enumerate(cn.BASKET_CATEGORIES):
            class_df = dist_df[(dist_df[cn.CLASS] == category) & 
                        (dist_df[cn.RANK] <= basket_combination[i])]
            dfs_by_class.append(class_df)

        # Concatenate the intermediate dataframes
        basket_df = pd.concat(dfs_by_class)

        # Note: Need to post-process the column names.

        return basket_df


if __name__ == "__main__":
    """
    Ask the user for their API key.
    """
    api_key = input("Enter your Google API key: ")
    basket_calculator = BasketCalculator(api_key)

    origin_df = BasketCalculator.origin_df
    dest_df = BasketCalculator.dest_df

    # distance_df = basket_calculator.origins_to_distances(origin_df, dest_df)
    # Is it a problem that this is all stored in memory until write to file?   

    cn.BASKET
    google_dist_fp = cn.GOOGLE_DIST_FP
    
    dist_df = pd.read_csv(google_dist_fp)
    basket = basket_calculator.create_basket(dist_df, BEST_BASKET)
    
    basket.to_csv("basket-steve.csv") 

    # Import Darius csv to sql code
    # Output to sql.
