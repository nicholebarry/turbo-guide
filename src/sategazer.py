#! /usr/bin/env python
""" Detect satellites passing over the range of astronomical observations

"""

import configparser
import ephem 
import numpy as np
import warnings

from argparse import ArgumentParser
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy import units as u

# requesting satellit TLE data  
import requests

# convert string to valid filename 
from slugify import slugify

# Defining location of observer
from astropy.coordinates import EarthLocation

# For start time and end time
from datetime import datetime, timedelta

# Using sky field to load the TLE data
from skyfield.api import load

# Using skyfield to define the observer location
from skyfield.toposlib import Topos

# Convert from astropy units to units for Topos in skyfield
import astropy.units as u

# specifying timezone of observer
import pytz

class Observer:
    def __init__(self, name, latitude, longitude, elevation):
        self.name = name

        self.location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
        self.start_time = None
        self.end_time = None
        self.time_step = None
        self.azimuth_range = None
        self.elevation_range = None

    def set_observer_times(self, start_time, end_time, time_step):
        self.start_time = start_time
        self.end_time = end_time
        self.time_step = time_step

    def set_observer_range(self, elevation_range, azimuth_range):
        self.elevation_range = elevation_range
        self.azimuth_range = azimuth_range

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

def check_satellite_in_range(altitude, azimuth, azimuth_range, elevation_range):
    """
    Check if a position (given by altitude and azimuth) is within the specified range.

    Args:
        altitude (float): The altitude angle in degrees.
        azimuth (float): The azimuth angle in degrees.
        azimuth_range (tuple): A tuple containing the minimum and maximum azimuth angles in degrees.
        elevation_range (tuple): A tuple containing the minimum and maximum elevation angles in degrees.

    Returns:
        bool: True if the position is within the specified range, False otherwise.
    """
    min_azimuth, max_azimuth = azimuth_range
    min_elevation, max_elevation = elevation_range

    is_in_azimuth_range = min_azimuth <= azimuth <= max_azimuth
    is_in_elevation_range = min_elevation <= altitude <= max_elevation

    return is_in_azimuth_range and is_in_elevation_range

def calculate_satellite_position_in_range(observer_object, satellite_object):

    # url for satellite object in the TLE format
    # station_url = f"https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_object.name}&FORMAT=TLE"
    all_station_url = 'http://celestrak.org/NORAD/elements/stations.txt'
    all_satellites = load.tle_file(all_station_url)

    # create set of satellite
    all_satellite_sorted_by_names = {sat.name: sat for sat in all_satellites}
    TLE_data = all_satellite_sorted_by_names[satellite_object.name]
    
    observation_times = np.arange(observer_object.start_time, observer_object.end_time, observer_object.time_step).astype(datetime)

    # Defining location as a Topos class from skyfield

    observer_location_skyfield = Topos(observer_object.location.lat.to_value(u.deg), 
                              observer_object.location.lon.to_value(u.deg), 
                              observer_object.location.height.to_value(u.m))
    
    # list to store observed satellite positions
    observed_satellite_positions = []
    
    for current_observation_time in observation_times:
        # Creating a timescale object from skyfield library to convert datetime into skyfield time format
        timescale = load.timescale()
        print('Current_observation_time (datetime object):', current_observation_time)
        # creating skyfield appropriate current_observation_time
        current_observation_time_skyfield = timescale.utc(current_observation_time.year, current_observation_time.month, current_observation_time.day, current_observation_time.hour, current_observation_time.minute, current_observation_time.second)
        print('UTC date and time (current_observation_time_skyfield):', current_observation_time_skyfield.utc_strftime())
        print('current_observation_time_skyfield (utc): ', current_observation_time_skyfield)
        # TLE data normally contains  
        topocentric_position = (TLE_data - observer_location_skyfield).at(current_observation_time_skyfield)

        # Checking if satellite is in the field of view of the observer

        altitude, azimuth, distance = topocentric_position.altaz()
        # Compare to stellarium
        print(f'azimuth: {azimuth}\naltitude: {altitude}')
        if check_satellite_in_range(altitude.degrees, azimuth.degrees, observer_object.azimuth_range, observer_object.elevation_range):
            observed_satellite_positions.append((current_observation_time_skyfield, altitude.degrees, azimuth.degrees))

    return observed_satellite_positions

def main():
    
    # Range of observation using utc time
    observation_start_time = datetime(2023, 9, 6, 16, 25, 0)
    observation_end_time = datetime(2023, 9, 6, 16, 35, 0)
    observation_time_step = timedelta(minutes=5)

    # Creating curtin university observer object 
    ## Curtin university is UTC+8 (8 hours ahead of UTC)
    curtin_timezone = pytz.timezone('Etc/GMT-8')
    curtin_university_observer_object = Observer(name='Curtin', latitude=-32.0061951, longitude=115.8944182, elevation=17.92)

    curtin_university_observer_object.set_observer_times(observation_start_time, observation_end_time, observation_time_step)
    curtin_university_observer_object.set_observer_range(elevation_range=[0,360], azimuth_range=[0,360])

    adelaide_university_observer_object = Observer(name='Curtin', latitude=-34.921230, longitude=138.599503, elevation=59)

    adelaide_university_observer_object.set_observer_times(observation_start_time, observation_end_time, observation_time_step)
    adelaide_university_observer_object.set_observer_range(elevation_range=[0,360], azimuth_range=[0,360])

    # Defining satellite object
    ISS_satellite_object = Satellite("ISS (ZARYA)")

    satellite_objects = [ISS_satellite_object]

    for satellite in satellite_objects:

        satellite_position_in_curtin_university_range = calculate_satellite_position_in_range(curtin_university_observer_object, satellite)

        satellite_position_in_adelaide_university_range = calculate_satellite_position_in_range(adelaide_university_observer_object, satellite)

        print(satellite_position_in_curtin_university_range)
        print(satellite_position_in_adelaide_university_range)

    return 

if __name__ == "__main__":
    main()