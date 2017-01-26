#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script to convert ASCII LiDAR files used for ARSF data
prior to 2009 (.all) into ASCII or LAS files

For a description of the .all format used see:

https://arsf-dan.nerc.ac.uk/trac/wiki/Processing/LIDARDEMs

Conversion to LAS Requires LAStools > 160730 to use the '-utm ZZnorth'
flag.

Author: Dan Clewley
Creation Date: 07/09/2016

"""

##################################################################
# This file has been created by NERC-ARF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
##################################################################

from __future__ import print_function
import argparse
import csv
import os
import sys
import tempfile
import re
import subprocess

# Try to get LAStools path from DEM Scripts
LASTOOLS_PATH = ""
try:
    from arsf_dem import dem_common
    LASTOOLS_PATH = dem_common.LASTOOLS_FREE_BIN_PATH
except ImportError:
    # If can't import DEM scripts assume on main path
    pass

# Minimum height difference to consider returns as separate
MIN_HEIGHT_DIFF = 0.01

def convert_pre2009_all_to_ascii(input_all_file, output_ascii_file):
    """

    Imput format is:

    1. GPS_time
    2. ZZeasting (last return)
    3. northing (last return)
    4. height(m) (last return)
    5. intensity (last return)
    6. ZZeasting (first return)
    7. northing (first return)
    8. height(m) (first return)
    9. intensity (first return)

    # Output format is:

    1. time
    2. easting
    3. northing
    4. elevation
    5. intensity
    6. return number
    7. number of returns

    """
    input_all = open(input_all_file, "r")
    output_ascii_handler = open(output_ascii_file, "w")
    output_ascii = csv.writer(output_ascii_handler, delimiter=" ")

    utm_zone = None

    for line in input_all:
        num_returns = 1
        # Strip leading space and convert consecutive delimiters to single one
        line = re.sub("\s+", " ", line.strip())
        elements = line.split(' ')
        gps_time = elements[0]
        if utm_zone is None:
            utm_zone = elements[1][:2]
        easting_last_return = elements[1][2:]
        northing_last_return = elements[2]
        height_last_return = elements[3]
        intensity_last_return = elements[4]

        if len(elements) > 5:
            easting_first_return = elements[5][2:]
            northing_first_return = elements[6]
            height_first_return = elements[7]
            intensity_first_return = elements[8]

            # Some pulses have two returns which are the same or very similar
            # so don't consider as separate. Require a minimum height difference
            # between returns within a pulse to consider them separate.
            height_diff = abs(float(height_first_return)
                              - float( height_last_return))
            if height_diff > MIN_HEIGHT_DIFF:
                num_returns = "2"

                # Write out first return
                output_ascii.writerow([gps_time,
                                       easting_first_return, northing_first_return,
                                       height_first_return, intensity_first_return,
                                       "1", num_returns])

        # Write out last (possibly only) return
        output_ascii.writerow([gps_time,
                               easting_last_return, northing_last_return,
                               height_last_return, intensity_last_return,
                               num_returns, num_returns])

    input_all.close()
    output_ascii_handler.close()

    return utm_zone

def convert_ascii_to_las(input_ascii, output_las, utm_zone):
    """
    Converts ASCII file to LAS/LAZ using txt2las
    Parses using txyzirn
    """
    las2txt_cmd = [os.path.join(LASTOOLS_PATH, "txt2las"),
                   "-parse", "txyzirn",
                   "-utm", utm_zone,
                   "-i", input_ascii, "-o", output_las]
    subprocess.check_call(las2txt_cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .all format LiDAR "
                                                 "data to LAS or ASCII")
    parser.add_argument("-i", "--inall", type=str,
                        help="Input directory containing .all files",
                        required=True)
    parser.add_argument("-o", "--outfile", type=str,
                        default=None,
                        help="Output file (.txt or .las)",
                        required=True)
    args = parser.parse_args()

    if os.path.splitext(args.outfile)[1].lower() == ".txt":
        print("Converting to txt...")
        utm_zone = convert_pre2009_all_to_ascii(args.inall, args.outfile)
        print("Saved to {}".format(args.outfile))
        print("UTM Zone = {}".format(utm_zone))
    else:
        # As we're creating a large temp file need to make sure this is removed
        # if process fails so use try/except/finally
        print("Converting to temporary text file...")
        tmp_ascii_fd, tmp_ascii_file = tempfile.mkstemp(prefix="arsf_ascii_conversion")
        os.close(tmp_ascii_fd)
        try:
            utm_zone = convert_pre2009_all_to_ascii(args.inall, tmp_ascii_file)
            print("Converting to LAS file...")
            # Need to specify hemisphere when passing UTM zone to txt2las
            # As most ARSF data is in the northern hemisphere go with this
            lastools_utm_zone = "{}north".format(utm_zone)
            convert_ascii_to_las(tmp_ascii_file, args.outfile, lastools_utm_zone)
            print("Saved to {}".format(args.outfile))
            print("UTM Zone = {}".format(utm_zone))
        except subprocess.CalledProcessError as err:
            print("Error converting to LAS:\n{}".format(err), file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        finally:
            os.remove(tmp_ascii_file)
