#! /usr/bin/env python
""" Detect satellites passing over the range of astronomical observations

"""
import numpy as np

# Defining location of observer
from astropy.coordinates import EarthLocation

# For start time and end time
from datetime import datetime, timedelta

# Using sky field to load the TLE data
from skyfield.api import load

# Using skyfield to define the observer location
from skyfield.toposlib import Topos

# specifying timezone of observer
import pytz

class Observer:
    def __init__(self, name, latitude, longitude, elevation_from_sea):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude 
        self.elevation_from_sea = elevation_from_sea

        # self.location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
        self.start_time = None
        self.end_time = None
        self.time_step = None
        self.azimuth_fov = None
        self.elevation_fov = None

    def set_observer_times(self, start_time, end_time, time_step):
        self.start_time = start_time
        self.end_time = end_time
        self.time_step = time_step

    def set_observer_range(self, elevation_fov, azimuth_fov):
        self.elevation_fov = elevation_fov
        self.azimuth_fov = azimuth_fov

class Satellite:
    def __init__(self, name):
        self.name = name
        self.TLE_data = None

    def set_TLE_data(self, TLE_data):
        self.TLE_data = TLE_data

def initialise_observer(latitude, longitude, elevation):
    """ Define the observer location wiht astropy

    Args:
        latitude (degree): _description_
        longitude (degree): _description_
        elevation (metres): _description_

    Returns:
        _type_: _description_
    """
    observer_location = EarthLocation(lat=latitude, lon=longitude, height=elevation)

    return observer_location

def check_satellite_in_range(altitude, azimuth, azimuth_fov, elevation_fov):
    """
    Check if a position (given by altitude and azimuth) is within the specified range.

    Args:
        altitude (float): The altitude angle in degrees.
        azimuth (float): The azimuth angle in degrees.
        azimuth_fov (tuple): A tuple containing the minimum and maximum azimuth angles in degrees.
        elevation_fov (tuple): A tuple containing the minimum and maximum elevation angles in degrees.

    Returns:
        bool: True if the position is within the specified range, False otherwise.
    """
    min_azimuth, max_azimuth = azimuth_fov
    min_elevation, max_elevation = elevation_fov

    is_in_azimuth_fov = min_azimuth <= azimuth <= max_azimuth
    is_in_elevation_fov = min_elevation <= altitude <= max_elevation

    return is_in_azimuth_fov and is_in_elevation_fov

def check_satellite_in_fov(altitude_difference, azimuth_difference, azimuth_fov_range, elevation_fov_range):
    """Checks if satellite is within the field of view 

    Args:
        altitude_difference (decimal degrees): represents degree difference between observer and space object in alitude
        azimuth_difference (decimal degrees): represents degree difference between observer and space object in alitude
        azimuth_fov_range (float): decimal degree range for fov
        elevation_fov_range (float): decimal degree range for fov

    Returns:
        _type_: _description_
    """    
    is_in_altitude_fov = altitude_difference <= 0.5*azimuth_fov_range
    is_in_azimuth_fov = azimuth_difference <= 0.5*elevation_fov_range

    return is_in_altitude_fov and is_in_azimuth_fov

def calculate_satellite_position_in_range(observer_object, satellite_object):

    # url for satellite object in the TLE format
    # station_url = f"https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_object.name}&FORMAT=TLE"
    all_station_url = 'http://celestrak.org/NORAD/elements/stations.txt'
    all_satellites = load.tle_file(all_station_url)

    # create set of satellite
    all_satellite_sorted_by_names = {sat.name: sat for sat in all_satellites}
    satellite = all_satellite_sorted_by_names[satellite_object.name]
    
    observation_times = np.arange(observer_object.start_time, observer_object.end_time, observer_object.time_step).astype(datetime)

    # Defining location as a Topos class from skyfield
    ## https://snyk.io/advisor/python/skyfield/functions/skyfield.api.Topos
    observer = Topos(latitude_degrees = observer_object.latitude, 
                                        longitude_degrees = observer_object.longitude, 
                                        elevation_m = observer_object.elevation_from_sea)
    
    print('observer:', observer)
    # list to store observed satellite positions
    observed_satellite_positions = []
    
    for current_observation_time in observation_times:
        # Creating a timescale object from skyfield library to convert datetime into skyfield time format
        timescale = load.timescale()
        print('Current_observation_time (datetime object):', current_observation_time)

        # creating skyfield appropriate current_observation_time
        current_observation_time_skyfield = timescale.utc(current_observation_time.year, current_observation_time.month, current_observation_time.day, current_observation_time.hour, current_observation_time.minute, current_observation_time.second)

        print('current_observation_time_skyfield (utc): ', current_observation_time_skyfield)
        print('satellite: ', satellite)
        
        # TLE data normally contains  
   
        difference = (satellite - observer).at(current_observation_time_skyfield)
        print('difference:', difference)

        # Checking if satellite is in the field of view of the observer

        altitude_difference, azimuth_difference, distance_difference = difference.altaz()

        print(f'satellite altaz: {altitude_difference.degrees} {azimuth_difference.degrees}')
        if check_satellite_in_fov(altitude_difference.degrees, azimuth_difference.degrees, observer_object.azimuth_fov, observer_object.elevation_fov):
            observed_satellite_positions.append((current_observation_time_skyfield, satellite.at(current_observation_time_skyfield).altaz()))

    return observed_satellite_positions

def main():
    
    # Range of observation using local time
    observation_start_time = datetime(2023, 9, 6, 21, 50, 0)
    observation_end_time = datetime(2023, 9, 6, 21, 55, 0)
    observation_time_step = timedelta(minutes=5)

    # Creating curtin university observer object 
    ## Curtin university is UTC+8 (8 hours ahead of UTC)
    curtin_timezone = pytz.timezone('Etc/GMT-8')
    curtin_university_observer_object = Observer(name='Curtin', latitude=-32.0061951, longitude=115.8944182, elevation_from_sea=17.92)

    curtin_university_observer_object.set_observer_times(observation_start_time, observation_end_time, observation_time_step)
    curtin_university_observer_object.set_observer_range(elevation_fov=60.0, azimuth_fov=60.0)

    adelaide_university_observer_object = Observer(name='Curtin', latitude=-34.921230, longitude=138.599503, elevation_from_sea=59)

    adelaide_university_observer_object.set_observer_times(observation_start_time, observation_end_time, observation_time_step)
    adelaide_university_observer_object.set_observer_range(elevation_fov=60.0, azimuth_fov=60.0)

    # Defining satellite object
    ISS_satellite_object = Satellite("ISS (ZARYA)")

    satellite_objects = [ISS_satellite_object]

    for satellite in satellite_objects:

        # satellite_position_in_curtin_university_range = calculate_satellite_position_in_range(curtin_university_observer_object, satellite)
        # print(satellite_position_in_curtin_university_range)

        satellite_position_in_adelaide_university_range = calculate_satellite_position_in_range(adelaide_university_observer_object, satellite)

        
        print(satellite_position_in_adelaide_university_range)

    return 

if __name__ == "__main__":
    main()