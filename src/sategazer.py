#! /usr/bin/env python
""" Detect satellites passing over the FoV of astronomical observations

"""

import configparser
import ephem 
import numpy as np
import warnings

from argparse import ArgumentParser
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy import units as u

def convert_coord_to_deg(source_coords):
    """ Convert coordinate strings to decimal degrees format

    Parameters
    ----------
    source_coords : string
        RA and Dec

    Returns
    -------
    source_pos: 
        _description_
    """
    if ':' in source_coords:
        source_pos = SkyCoord(source_coords, unit=(u.hourangle, u.deg))
    else:
        source_pos = SkyCoord(source_coords, unit=(u.deg, u.deg))

    return source_pos


def calculate_satellite_dist(centre_pos, time_start):
    """ Calculate satellites' distances from the observing pointing centre

    Parameters
    ----------
    centre_pos : 
        an array of ra and dec of the pointing centre  in decimal degrees
    time_start : string 
        observation time (UTC) e.g. '2023/09/04 00:55:37.0')

    Returns
    -------
    sat_dists : float
        an array of distances of satellites 
    sat_names : string array
        an arry of satellites names
        
    """
    # Read TLE file to get satellite information
    file_tle = './data/satellites.txt'
    with open(file_tle) as f:
        tle = f.read().strip().split('\n')
    
    # Convert a list of TLE to a numpy array
    arr_indx = int(len(tle) / 3), 3
    tle_arr = np.array(tle)
    tle_arr = tle_arr.reshape(arr_indx)
    
    # Caculate distances of satellites from observing centre
    sat_names = []
    sat_dists = []
    for i in range(arr_indx[0]):
        sat = ephem.readtle(tle_arr[i][0], tle_arr[i][1], tle_arr[i][2])
        sat.compute(time_start)
        sat_ra = ephem.degrees(sat.ra)
        sat_dec = ephem.degrees(sat.dec)
        sat_pos = SkyCoord(sat_ra, sat_dec, unit=(u.deg, u.deg))
        sat_dists.append(centre_pos.separation(sat_pos).value)
        sat_names.append(tle_arr[i][0])
    
    return sat_dists, sat_names


def sategazer_parser():
    """ Configure inputs for sategazer

    Returns
    -------
    parser : argparse.ArgumentParser
        The parser for sategazer
    """
    parser = ArgumentParser(description='Run satgazer to search for satellites passing over the FoV')
    parser.add_argument('-c','--coordinates', dest='coords', required='true', help='RA and Dec of observing centre separated with a space', type=str)
    parser.add_argument('-f','--fov', dest='fov', required ='true', help='FoV of an observatios in degree', type=float)
    parser.add_argument('-t','--obstime', dest='obstime', required='true', help='Start time of observation in UTC e.g. 2023/09/04 00:55:37.0', type=str)
    parser.add_argument('-i','--integration', dest='obsduration', required='true', help='Integration time in hr')
    
    return parser

def main():
    # Get inputs
    parser = sategazer_parser()
    params = parser.parse_args()

    cenpos = convert_coord_to_deg(params.coords)
    sat_dis, sat_nam = calculate_satellite_dist(cenpos, params.obstime)
    print(cenpos)

if __name__ == "__main__":
    main()