#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract GPS coordinates from ARSF Wild RC-10 TIFF images using exiftool
and save to CSV.

Requires exiftool to be installed from http://www.sno.phy.queensu.ca/~phil/exiftool/

Known Issues:

Author: Dan Clewley, NERC-ARF-DAN
Creation Date: 06/09/2016

Change history
14/09/2016: (Laura Harris) Added functionality to read lat and long from sbet file.

"""
##################################################################
# This file has been created by NERC-ARF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
##################################################################

from __future__ import print_function
import argparse
import csv
import glob
import os
import subprocess
import sys
import math
import time
try:
    import read_nav_file
except ImportError:
    print("Could not import read_nav_file. Please download from arsf_tools",
          file=sys.stderr)
    sys.exit(1)

def get_exif_info_from_image(image_file):
    """
    Reads exif info from image using exiftool
    and returns as dictionary.
    """
    exif_info_str = subprocess.check_output(["exiftool", image_file])
    exif_info_list = exif_info_str.decode().split("\n")

    exif_info = {}

    for item in exif_info_list:
        if item.count(":") == 1:
            key, par = item.split(":")
            exif_info[key.strip().lower()] = par.strip()
        elif item.count(":") > 1:
            elements = item.split(",")
            for sub_item in elements:
                key, par = sub_item.split(":", 1)
                exif_info[key.strip().lower()] = par.strip()

    return exif_info

def parse_gps_pos_str(gps_pos_str):
    """
    Parses a D M S formatted GPS string and returns decimal degrees

    Example input format:

    52 22 49.30
    """
    gps_pos_items = gps_pos_str.split(" ")

    deg = abs(float(gps_pos_items[0]))
    minutes = float(gps_pos_items[1])
    seconds = float(gps_pos_items[2])

    decimal_deg = deg + (minutes / 60.0) + (seconds / 3600)

    if gps_pos_items[0][0] == "-":
        decimal_deg = -1.0 * decimal_deg

    return decimal_deg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract location from exif "
                                                 "tags of scanned ARSF Wild RC-10"
                                                 " images to CSV file")
    parser.add_argument("inputimages", nargs="*",type=str, help="Input images")
    parser.add_argument("-o", "--out_csv",
                        type=str, required=True,
                        help="Output CSV")
    parser.add_argument("-n", "--nav",
                        type=str, default = None,
                        help="sbet nav file to get lat/long if not tagged in image")
    args=parser.parse_args()

    # On Windows don't have shell expansion so fake it using glob
    if args.inputimages[0].find('*') > -1:
        args.inputimages = glob.glob(args.inputimages[0])

    # if nav file provided, read in
    if args.nav is not None:
        nav_data = read_nav_file.readSbet(args.nav)

    f = open(args.out_csv, "w")

    out_csv_writer = csv.writer(f)
    out_csv_writer.writerow(["ImageName","Date", "Time",
                             "Latitude", "Longitude",
                             "Altitude"])

    for i, image in enumerate(args.inputimages):
        print("[{0}/{1}] {2}".format(i, len(args.inputimages),
                                    os.path.basename(image)))
        try:
            exif_info = get_exif_info_from_image(image)

            # If nav data need to convert GPS time to sbet format (week seconds)
            if args.nav is not None:
                gps_time = exif_info["gps time"].split(":")
                weekseconds = (time.strptime(exif_info["date"],
                              '%d-%b-%y').tm_wday+1) * 24 * 60 * 60
                gps_seconds = (weekseconds + 60**2 * float(gps_time[0])
                              + 60 * float(gps_time[1]) + float(gps_time[2]))
                index=read_nav_file.getArrayIndex(nav_data,'time',gps_seconds)

            #check latitude is present in image
            if "local latitude" not in exif_info and args.nav is not None:
                # get from sbet file if provided
                latitude = math.degrees(nav_data['lat'][index])
            else:
                latitude = parse_gps_pos_str(exif_info["local latitude"])

            #check longitude is present in image
            if "local longitude" not in exif_info and args.nav is not None:
                # get from sbet file if provided
                longitude = math.degrees(math.degrees(nav_data['lat'][index]))
            else:
                longitude = parse_gps_pos_str(exif_info["local longitude"])

            # gps height may be labelled differently
            if "gps height ft" in exif_info:
                gps_height = exif_info["gps height ft"]
            else:
                gps_height = exif_info["gps height"]


            out_row = [os.path.basename(image),
                       exif_info["date"],
                       exif_info["gps time"].replace(" ",""),
                       latitude,
                       longitude,
                       gps_height]

            out_csv_writer.writerow(out_row)

        except Exception as err:
            print(" Failed to get tags from {}\n{}".format(image, err),
                  file=sys.stderr)

    f.close()
