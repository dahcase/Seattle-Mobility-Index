import init
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from geocoder import Geocoder
import constants as cn
import seamo_exceptions as se
import data_accessor as daq

class Coordinate:
    """
    Coordinate class.
    """
    def __init__(self, lat, lon):
        """
        Initialize Coordinate with a latitude and a longitude (both floats).
        """
        self.lat = lat
        self.lon = lon
        self.block_group = None
        self.neighborhood_long = None
        self.neighborhood_short = None
        self.council_district = None
        self.urban_village = None
        self.zipcode = None
        self.parking_cost = None


    def __str__(self):
        """
        Stringify a Coordinate.
        Format is 'lat,lon'
        """
        return "{0}, {1}".format(self.lat, self.lon)


    def set_geocoded_attributes(self, block_group, neighborhood_long, neighborhood_short,
                                council_district, urban_village, zipcode):
        self.block_group = block_group
        self.neighborhood_long = neighborhood_long
        self.neighborhood_short = neighborhood_short
        self.council_district = council_district
        self.urban_village = urban_village
        self.zipcode = zipcode
        return self


    def set_geocode(self):
        try:
            self._geocode(self.lat, self.lon)
        except KeyError:
            #TODO: fix!
            self.block_group = None
            self.neighborhood_long = None
            self.neighborhood_short = None
            self.council_district = None
            self.urban_village = None
            self.zipcode = None
            # raise se.NotInSeattleError("No Parking Data Available")
        return self

    def set_parking_cost(self):
        parking_dict = daq.open_pickle(cn.PICKLE_DIR, cn.PARKING_RATES_PICKLE)
        if self.block_group == None:
            self.set_geocode()
        try:
            parking_dict[self.block_group]
        except:
            self.parking_cost = 0
        else:
            self.parking_cost = parking_dict[self.block_group]
        return self


    def haversine_distance(self, coordinate):
        """
        Calculate haversine distance between this Coordinate
        and another Coordinate.

        input: coordinate (Coordinate)
        output: distance (float)
                in miles
        """
       
        # This Coordinate 
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        # The Coordinate to calculate distance to
        lat2 = radians(coordinate.lat)
        lon2 = radians(coordinate.lon)

        # Differences
        diff_lon = lon2 - lon1
        diff_lat = lat2 - lat1

        # Solve for distance applying inverse Haversine
        a = sin(diff_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(diff_lon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = cn.EARTH_RADIUS_KM * c 
        # Convert to miles
        distance *= cn.KM_TO_MILES
    
        return distance


    def _geocode(self, lat, lon):
        geo = Geocoder()
        df = geo.geocode_point((float(lat), float(lon)))
        # import pdb; pdb.set_trace()
        self.block_group = df[cn.BLOCK_GROUP].item()
        self.neighborhood_long = df[cn.NBHD_LONG].item()
        self.neighborhood_short = df[cn.NBHD_SHORT].item()
        self.council_district = df[cn.COUNCIL_DISTRICT].item()
        self.urban_village = df[cn.URBAN_VILLAGE].item()
        self.zipcode = df[cn.ZIPCODE].item()
        return self


    def get_attribute(self, attribute):
        attribute = {cn.BLOCK_GROUP: self.block_group,
                    cn.NBHD_LONG: self.neighborhood_long,
                    cn.NBHD_SHORT: self.neighborhood_short,
                    cn.COUNCIL_DISTRICT: self.council_district,
                    cn.URBAN_VILLAGE: self.urban_village,
                    cn.ZIPCODE: self.zipcode}[attribute]
        return attribute
