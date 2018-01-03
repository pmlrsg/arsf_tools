#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copies selected information from one header file to another.

Example usage:

  copy_header_info.py f221013_mapped_osng.bil.hdr f221013_nadir_mapped_osng.hdr -k "map info" "projection info" "wavelength"

Author: Dan Clewley
Creation Date: 27/08/2015

"""

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

from __future__ import print_function
import argparse
import os
import shutil
import sys

from arsf_envi_reader import envi_header

def copy_header_dict_items(source_header_dict, target_header_dict, keys):
    """
    Copy selected keys from source header to target. Replacing if they exist
    """
    for key in keys:
        try:
            target_header_dict[key] = source_header_dict[key]
            print("Copied {}".format(key))
        except KeyError:
            print("Could not find {}. Skipping".format(key),file=sys.stderr)

def run_copy_header(sourceheader, targetheader, keys):
    """
    Copy information from sourceheader to targetheader
    for given keys.

    """
    # Read header info to dictionaries
    source_header_dict = envi_header.read_hdr_file(args.sourceheader[0],
                                                   keep_case=True)
    target_header_dict = envi_header.read_hdr_file(args.targetheader[0],
                                                   keep_case=True)

    copy_header_dict_items(source_header_dict, target_header_dict, args.keys)

    # Make a backup copy of the origional header
    try:
        if os.path.isfile(args.targetheader[0] + '.bak'):
            print("Backup file {}.bak already exists. Please remove "
                  "and retry".format(args.targetheader[0]), file=sys.stderr)
            sys.exit(1)
        shutil.copy2(args.targetheader[0],args.targetheader[0] + '.bak')
    except IOError:
        print("Could create backup copy of header in same destination as source "
              "- possibly due to folder permissions. Aborting",file=sys.stderr)
    except Exception:
        raise

    envi_header.write_envi_header(args.targetheader[0], target_header_dict)

    print("Copied items to {0}, origional header "
          "saved as {0}.bak".format(args.targetheader[0]))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='''
                        Copy information from one ENVI header to another.
                        Created by ARSF-DAN at Plymouth Marine Laboratory.
                        Latest version available from https://github.com/pmlrsg/arsf_tools/.''')
    parser.add_argument("sourceheader", nargs=1,type=str,
                            help="Header containing information to copy from")
    parser.add_argument("targetheader", nargs=1,type=str,
                            help="Header to copy fields into")
    parser.add_argument("-k","--keys", nargs='*', required=False, type=str,
                            help="Keys to copy from 'sourceheader' to 'targetheader'")
    args = parser.parse_args()

    run_copy_header(args.sourceheader[0], args.targetheader[0], args.keys)
