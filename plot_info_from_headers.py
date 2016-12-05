#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gets information from multiple ENVI header files and plots them or saves
to a file. Also has the option to save all values to a csv file. Assumes that if
there are 2 detectors, one is VNIR and the second is SWIR. Can be used on 
raw, level 1 or level 3 headers. Will display a blank plot if the value is missing
from all headers. Applications could be to examine the varitaion in length of 
files for a particualr project, check consistency in settings such as frame rate
and integration time or to examine the temperature of the detector to confirm
that it is fully cooled and stable for all acquisitions.

Author: Laura Harris
Creation Date: 02/12/2016

read_hdr_file written by Ben Taylor
"""

###########################################################
# This file has been created by the NERC-ARF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

from __future__ import print_function
import argparse
import csv
import os
import sys
from arsf_envi_reader import envi_header
import matplotlib.pyplot as plt
import re

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='''
                       Get information from multiple ENVI header files and plots key values.
                       Can optionally save plots to a file instead.
                       Created by NERC-ARF-DAN at Plymouth Marine Laboratory.
                       Latest version available from https://github.com/pmlrsg/arsf_tools/.''')
   parser.add_argument("inputfiles",  type=str, nargs='+',
                           help="Input headers")
   parser.add_argument("-o","--outdir", required=False, type=str,
                           help="Output directory to store plots to")
   parser.add_argument("-v","--values", nargs='+', required=False, type=str,
                           help="Values to plot: fps, tint, nbands, nsamples, nlines, "
                           "binning, temp, all", default = "fps, tint")
   parser.add_argument("-c","--outcsv", required=False, type=str,
                           help="Output file to store values for each band to")
   parser.add_argument("-k","--keep_order", required=False, action = "store_true",
                           help="If used, will keep the order specified in the commmand line")
   args = parser.parse_args()

   # Check multiple files provided
   if len(args.inputfiles) < 2:
      print("Only one input file provided. Use get_info_from_header.py to display to screen")
      sys.exit()

   # Set up values to plot
   nbands = []
   nsamples = []
   nlines = []
   fps = []
   tint = []
   tint1 = []
   tint2 = []
   binning = []
   binning2 = []
   temp = []
   dates = []
   start_times = []
   stop_times = []

   # Reorder files by line number
   if not args.keep_order:
      args.inputfiles.sort(key=alphanum_key)

   for each_hdr in args.inputfiles:
      # Check a header file has been provided.
      if os.path.splitext(each_hdr)[-1].lower() != '.hdr':
         print('Must provide header file as input (ending with ".hdr")', 
               file=sys.stderr)
         sys.exit(1)
      if not os.path.isfile(each_hdr):
         print('Could not open input header ({})'.format(each_hdr), 
               file=sys.stderr)
         sys.exit(1)

      header_dict = envi_header.read_hdr_file(each_hdr)

      # Get supplimentary info for csv if available
      if 'acquisition date' in header_dict.keys():
         dates.append(header_dict['acquisition date'].split(' ')[-1])
      if 'gps start time' in header_dict.keys():
         start_times.append(header_dict['gps start time'].split(' ')[-1])
      if 'gps stop time' in header_dict.keys():
         stop_times.append(header_dict['gps stop time'].split(' ')[-1])

      if "bands" in header_dict.keys():
         nbands.append(int(header_dict['bands']))
      if "samples" in header_dict.keys():
         nsamples.append(int(header_dict['samples']))
      if "lines" in header_dict.keys():
         nlines.append(int(header_dict['lines']))
      if "fps" in header_dict.keys():
         fps.append(float(header_dict['fps']))
      if "tint" in header_dict.keys():
         tint.append(float(header_dict['tint']))
      if "tint1" in header_dict.keys():
         tint1.append(float(header_dict['tint1']))
      if "tint_vnir" in header_dict.keys():
         tint1.append(float(header_dict['tint_vnir']))
      if "tint2" in header_dict.keys():
         tint2.append(float(header_dict['tint2']))
      if "tint_swir" in header_dict.keys():
         tint2.append(float(header_dict['tint_swir']))
      if "binning" in header_dict.keys():
         binning.append(int(header_dict['binning'][0]))
      if "binning_vnir" in header_dict.keys():
         binning.append(int(header_dict['binning_vnir'][0]))
      if "binning2" in header_dict.keys():
         binning2.append(int(header_dict['binning2'][0]))
      if "binning_swir" in header_dict.keys():
         binning2.append(int(header_dict['binning_swir'][0]))
      if "temperature" in header_dict.keys():
      # won't be in dark frame files
         temp.append(float(header_dict['temperature'].split(',')[0]))

   # Plot selected values
   if "fps" in args.values or "all" in args.values:
      plt.plot(range(1, len(fps)+1), fps)
      plt.xlabel('File Index')
      plt.ylabel('Frames per second')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'fps.png'))
      plt.show()

   if "tint" in args.values or "all" in args.values:
      if "tint" in header_dict.keys():
          plt.plot(range(1, len(tint)+1), tint)
      if "tint1" in header_dict.keys() or "tint_vnir" in header_dict.keys():
          plt.plot(range(1, len(tint1)+1), tint1, label = 'VNIR')
      if "tint2" in header_dict.keys() or "tint_swir" in header_dict.keys():
         plt.plot(range(1, len(tint2)+1), tint2, label = 'SWIR')
      if ("tint1" in header_dict.keys() and "tint2" in header_dict.keys() or
          "tint_vnir" in header_dict.keys() and "tint_swir" in header_dict.keys()):
         plt.ylim(min(min(tint1), min(tint2))-1, max(max(tint1), max(tint2))+1)
         plt.legend()
      plt.xlabel('File Index')
      plt.ylabel('Integration Time, ms')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'tint.png'))
      plt.show()

   if "nbands" in args.values or "all" in args.values:
      plt.plot(range(1, len(nbands)+1), nbands)
      plt.xlabel('File Index')
      plt.ylabel('Number of bands')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'nbands.png'))
      plt.show()

   if "nsamples" in args.values or "all" in args.values:
      plt.plot(range(1, len(nsamples)+1), nsamples)
      plt.xlabel('File Index')
      plt.ylabel('Number of spatial samples')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'nsamples.png'))
      plt.show()

   if "nlines" in args.values:
      plt.plot(range(1, len(nlines)+1), nlines)
      plt.xlabel('File Index')
      plt.ylabel('Number of lines')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'nlines.png'))
      plt.show()

   if "binning" in args.values or "all" in args.values:
      if "binning" in header_dict.keys() and "binning2" not in header_dict.keys():
          plt.plot(range(1, len(binning)+1), binning)
      if ("binning" in header_dict.keys() and "binning2" in header_dict.keys() or
          "binning_vnir" in header_dict.keys() and "binning_swir" in header_dict.keys()):
         plt.plot(range(1, len(binning)+1), binning, label = 'VNIR')
         plt.plot(range(1, len(binning2)+1), binning2, label = 'SWIR')
         plt.ylim(min(min(binning), min(binning2))-1, max(max(binning), max(binning2))+1)
         plt.legend()
      plt.xlabel('File Index')
      plt.ylabel('Spectral Binning Factor')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'binning.png'))
      plt.show()

   if "temp" in args.values or "all" in args.values:
      plt.plot(range(1, len(temp)+1), temp)
      plt.xlabel('File Index')
      plt.ylabel('Temperature of Detector, K')
      if args.outdir is not None:
         plt.savefig(os.path.join(args.outdir, 'temp.png'))
      plt.show()

   # Save (all) parameters to csv if requested
   if args.outcsv is not None:
      with open(args.outcsv,'w') as f:
         out_file = csv.writer(f)

         for i in range(len(nbands)):
            # For first line write header
            if i == 0:
               header_row = ['File']       
               if len(dates)>0:
                  header_row.append('Date')
               if len(start_times)>0:
                  header_row.append('UTC_Start_Time')
               if len(stop_times)>0:
                  header_row.append('UTC_Stop_Time')
               if len(nbands)>0:
                  header_row.append('Bands')
               if len(nsamples)>0:
                  header_row.append('Samples')
               if len(nlines)>0:
                  header_row.append('Lines')
               if len(fps)>0:
                  header_row.append('FPS')
               if len(tint)>0:
                  header_row.append('Tint, ms')
               if len(tint1)>0:
                  header_row.append('Tint1, ms')
               if len(tint2)>0:
                  header_row.append('Tint2, ms')
               if len(binning)>0:
                  header_row.append('Spectral_Binning')
               if len(binning2)>0:
                  header_row.append('Spectral_Bining2')
               if len(temp)>0:
                  header_row.append('Temp, K')
               out_file.writerow(header_row)
            else:
               out_line = [args.inputfiles[i]]
               if len(dates)>0:
                  out_line.append(dates[i])
               if len(start_times)>0:
                  out_line.append(start_times[i])
               if len(stop_times)>0:
                  out_line.append(stop_times[i])
               if len(nbands)>0:
                  out_line.append(nbands[i])
               if len(nsamples)>0:
                  out_line.append(nsamples[i])
               if len(nlines)>0:
                  out_line.append(nlines[i])
               if len(fps)>0:
                  out_line.append(fps[i])
               if len(tint)>0:
                  out_line.append(tint[i])
               if len(tint1)>0:
                  out_line.append(tint1[i])
               if len(tint2)>0:
                  out_line.append(tint2[i])
               if len(binning)>0:
                  out_line.append(binning[i])
               if len(binning2)>0:
                  out_line.append(binning2[i])
               if len(temp)>0:
                  out_line.append(temp[i])
               out_file.writerow(out_line)

      print("csv file written to {}".format(args.outcsv))

