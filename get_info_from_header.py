#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gets information from ENVI header file and prints this to screen or saves
to a text file.

Author: Dan Clewley
Creation Date: 07/08/2015

read_hdr_file written by Ben Taylor
"""

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

from __future__ import print_function
import argparse
import csv
import os
import sys
from arsf_envi_reader import envi_header

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='''
                        Get information from ENVI header file and prints to screen.
                        Can optionally save some attributes (e.g., wavelengths) to
                        a CSV file.
                        Created by ARSF-DAN at Plymouth Marine Laboratory.
                        Latest version available from https://github.com/pmlrsg/arsf_tools/.''')
    parser.add_argument("inputfile", nargs=1,type=str,
                            help="Input header")
    parser.add_argument("-o","--outcsv", required=False, type=str,
                            help="Output file to store values for each band to")
    args = parser.parse_args()

    # Check a header file has been provided.
    if os.path.splitext(args.inputfile[0])[-1].lower() != '.hdr':
        print('Must provide header file as input (ending with ".hdr")', file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.inputfile[0]):
        print('Could not open input header ({})'.format(args.inputfile[0]), file=sys.stderr)
        sys.exit(1)

    header_dict = envi_header.read_hdr_file(args.inputfile[0])

    band_info_dict = {}
    nbands =  int(header_dict['bands'])

    print('The header contains the following information:\n')
    for item in header_dict.keys():
        # Check if there are the same number of items as bands, if so don't print
        # them out, just the number of values
        if nbands != 1 and header_dict[item].count(',') >= nbands - 1:
            print(' {} : {} values'.format(item, header_dict['bands']))
            item_list = header_dict[item].split(',')
            band_info_dict[item] = item_list
        else:
            print(' {} : {}'.format(item, header_dict[item]))

    # If a CSV file has been passed in save attributes where there is a value for
    # each band to it.
    if args.outcsv is not None:
        with open(args.outcsv,'w') as f:
            out_file = csv.writer(f)

            for i in range(nbands):
                # For first line write header
                if i == 0:
                    header_row = ['Band']
                    header_row.extend(band_info_dict.keys())
                    out_file.writerow(header_row)

                out_line = [str(i+1)]
                for item in band_info_dict.keys():
                    out_line.append(band_info_dict[item][i])
                out_file.writerow(out_line)
        print('\nWrote the following to {}:'.format(args.outcsv))
        print('\n'.join(band_info_dict.keys()))
