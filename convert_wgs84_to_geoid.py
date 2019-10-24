#!/usr/bin/env python
"""
Script to convert heights from relative to WGS84 to relative to EMG96 Geoid

Dan Clewley / NEODAAS / PML

This file has been created by the NERC Earth Observation Data Aqusition and Analysis Service (NEODAAS)
and is licensed under the GPL v3 Licence. A copy of this licence is available to download with this file.

"""
from __future__ import print_function
import argparse
import os
import subprocess

# Get path to file containing offsets between elipsiid and geoid
WWGSG_FILE = os.path.join(os.path.dirname(__file__), "data", "ww15mgh.tif")

def get_pixel_value(in_lat, in_lon, raster_file):
    """
    Gets values from an input raster for a given point by calling
    'gdallocationinfo'

    """
    gdallocationinfo_cmd = ["gdallocationinfo","-valonly","-geoloc","-wgs84",
                            raster_file,
                            str(in_lon),
                            str(in_lat)]

    # Run command
    try:
        gdal_out = subprocess.check_output(gdallocationinfo_cmd)
    except (OSError, subprocess.CalledProcessError):
        raise subprocess.CalledProcessError("Running the command:\n{}\n failed with {}"
                                            "Are the GDAL tools installed and available?"
                                            "".format(" ".join(gdallocationinfo_cmd),
                                            gdal_out))

    # Convert output to a float
    try:
        pixel_val = float(gdal_out.split()[0])
    except ValueError:
        raise ValueError("Could not convert gdallocationinfo output to a float:\n {}".format(gdal_out))

    return pixel_val

def convert_wgs_84_to_geoid(in_lat, in_lon, in_elevation, wgs84_to_geoid=True):
    """
    Converts elevation relative to WGS84 ellipsoid to relative to EGM96 geoid
    Geoid
    """

    ellipsoid_diff = get_pixel_value(in_lat, in_lon, WWGSG_FILE)

    if wgs84_to_geoid:
        new_elevation = in_elevation - ellipsoid_diff
    else:
        new_elevation = in_elevation + ellipsoid_diff

    return new_elevation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert heights between ellipsoid and geoid (approximation of AMSL)") 
    parser.add_argument("--lat",type=float, required=True,
                        help="Latitude")
    parser.add_argument("--lon",type=float, required=True,
                        help="Longitude")
    parser.add_argument("--height",type=float, required=True,
                        help="Height to convert")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--wgs84_to_egm96", action="store_true", default=True, 
                        help="Input Height is relative to WGS84 Ellipsoid and should be"
                             " converted to relative to EGM96 Geoid")
    group.add_argument("--egm96_to_wgs84", action="store_true", default=False, 
                        help="Input Height is relative to EGM96 Geoid and should be"
                              " converted to relative to WGS84 Ellipsoid")
    args=parser.parse_args()

    out_height = convert_wgs_84_to_geoid(args.lat, args.lon, args.height,
                                         wgs84_to_geoid=(not args.egm96_to_wgs84))

    print(out_height)

