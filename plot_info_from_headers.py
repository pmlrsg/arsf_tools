#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gets information from multiple ENVI header files and plots them or saves
to a file. Also has the option to save all values to a csv file. Assumes that if
there are 2 detectors, one is VNIR and the second is SWIR. Can be used on
raw, level 1 or level 3 headers. Applications could be to examine the varitaion in length of
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
import numpy as np
import glob

def tryint(s):
    """ Converts a string number to an integer or returns non-numbers as strings.
    """
    try:
        return int(s)
    except ValueError:
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
                            help="Output directory to store plots to. If not used, plots will "
                                 "still be displayed.")
    parser.add_argument("-v","--values", nargs='+', required=False, type=str,
                            help="Values to plot: fps, tint, nbands, nsamples, nlines, "
                            "binning, temp, all", default = "fps, tint")
    parser.add_argument("-c","--outcsv", required=False, type=str,
                            help="Output file to store values for each band to")
    parser.add_argument("-k","--keep_order", required=False, action = "store_true",
                            help="If used, will keep the order specified in the commmand line")
    args = parser.parse_args()

    # On Windows don't have shell expansion so fake it using glob
    if args.inputfiles[0].find('*') > -1:
        args.inputfiles = glob.glob(args.inputfiles[0])
    else:
        args.inputfiles = args.inputfiles

    # Check multiple files provided
    if len(args.inputfiles) < 2:
        print("Only one input file provided. Use get_info_from_header.py to display to screen")
        sys.exit()

    # Reorder files by line number
    if not args.keep_order:
        args.inputfiles.sort(key=alphanum_key)

    #Static dictionary filled with all the information for every plot (titles, labels filename etc)
    labeldict={'fps' : {'xlabel':'File Index','ylabel':'Frames per second','filename':'fps.png'},
                'tint' : {'xlabel':'File Index','ylabel':'Integration time (ms)','filename':'tint.png'},
                'nbands' : {'xlabel':'File Index','ylabel':'Number of bands','filename':'nbands.png'},
                'nsamples' : {'xlabel':'File Index','ylabel':'Number of spatial samples','filename':'nsamples.png'},
                'nlines' : {'xlabel':'File Index','ylabel':'Number of lines','filename':'nlines.png'},
                'binning' : {'xlabel':'File Index','ylabel':'Spectral binning factor','filename':'binning.png'},
                'temp' : {'xlabel':'File Index','ylabel':'Temperature of detector (K)','filename':'temp.png'}
    }

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
        else:
            dates.append(float('nan'))
        if 'gps start time' in header_dict.keys():
            start_times.append(header_dict['gps start time'].split(' ')[-1])
        else:
            start_times.append(float('nan'))
        if 'gps stop time' in header_dict.keys():
            stop_times.append(header_dict['gps stop time'].split(' ')[-1])
        else:
            stop_times.append(float('nan'))
        if "bands" in header_dict.keys():
            nbands.append(int(header_dict['bands']))
        else:
            nbands.append(float('nan'))
        if "samples" in header_dict.keys():
            nsamples.append(int(header_dict['samples']))
        else:
            nsamples.append(float('nan'))
        if "lines" in header_dict.keys():
            nlines.append(int(header_dict['lines']))
        else:
            nlines.append(float('nan'))
        if "fps" in header_dict.keys():
            fps.append(float(header_dict['fps']))
        else:
            fps.append(float('nan'))
        if "tint" in header_dict.keys():
            tint.append(float(header_dict['tint']))
        else:
            tint.append(float('nan'))
        if "tint1" in header_dict.keys():
            tint1.append(float(header_dict['tint1']))
        elif "tint_vnir" in header_dict.keys():
            tint1.append(float(header_dict['tint_vnir']))
        else:
            tint1.append(float('nan'))
        if "tint2" in header_dict.keys():
            tint2.append(float(header_dict['tint2']))
        elif "tint_swir" in header_dict.keys():
            tint2.append(float(header_dict['tint_swir']))
        else:
            tint2.append(float('nan'))
        if "binning" in header_dict.keys():
            binning.append(int(header_dict['binning'][0]))
        elif "binning_vnir" in header_dict.keys():
            binning.append(int(header_dict['binning_vnir'][0]))
        else:
            binning.append(float('nan'))
        if "binning2" in header_dict.keys():
            binning2.append(int(header_dict['binning2'][0]))
        elif "binning_swir" in header_dict.keys():
            binning2.append(int(header_dict['binning_swir'][0]))
        else:
            binning2.append(float('nan'))
        if "temperature" in header_dict.keys():
        # won't be in dark frame files
            temp.append(float(header_dict['temperature'].split(',')[0]))
        else:
            temp.append(float('nan'))

    #Dynamic dictionary created from the keys in the header_dict
    dicttoplot={'fps': {'fps' : fps} ,
                'tint': {'tint' : tint, 'tint1' : tint1, 'tint2' : tint2},
                'nbands' : {'bands' : nbands},
                'nsamples' : {'samples' : nsamples},
                'nlines' : {'lines' : nlines},
                'binning' : {'binning' : binning, 'binning2' : binning2},
                'temp' : {'temperature' : temp}
             }

    #Loop for plotting each item from the dicttoplot
    for item in dicttoplot.keys():
        if item in args.values or 'all' in args.values:
            ylims = []
            for each in dicttoplot[item]:
                if np.isnan(np.nansum(dicttoplot[item][each])):
                    continue
                plt.plot(dicttoplot[item][each],label=each)
                plt.xlabel(labeldict[item]['xlabel'])
                plt.ylabel(labeldict[item]['ylabel'])
                ylims.append(np.nanmin(dicttoplot[item][each]))
                ylims.append(np.nanmax(dicttoplot[item][each]))

            if not ylims: #no data to plot
                continue
            # set y axis outside data
            plt.ylim(min(ylims)-1, max(ylims)+1)
            if len(ylims) > 2:
                plt.legend()

            if args.outdir is not None:
                plt.savefig(os.path.join(args.outdir,labeldict[item]['filename']))
            else:
                plt.show()

    # Save (all) parameters to csv if requested
    if args.outcsv is not None:

        # first check all files have same records
        for item in dicttoplot.keys():
            for each in dicttoplot[item]:
                if np.nansum(dicttoplot[item][each])>0:
                    if len(dicttoplot[item][each]) != len(nbands):
                        print("Some header files are missing certain entries. Cannot create csv.")
                        sys.exit(1)

        with open(args.outcsv,'w') as f:
            out_file = csv.writer(f)

            for i in range(len(nbands)):
                # For first line write header
                if i == 0:
                    header_row = ['File']
                    if len(dates)==len(nbands):
                        header_row.append('Date')
                    if len(start_times)==len(nbands):
                        header_row.append('UTC_Start_Time')
                    if len(stop_times)==len(nbands):
                        header_row.append('UTC_Stop_Time')
                    if np.nansum(nbands)>0:
                        header_row.append('Bands')
                    if np.nansum(nsamples)>0:
                        header_row.append('Samples')
                    if np.nansum(nlines)>0:
                        header_row.append('Lines')
                    if np.nansum(fps)>0:
                        header_row.append('FPS')
                    if np.nansum(tint)>0:
                        header_row.append('Tint (ms)')
                    if np.nansum(tint1)>0:
                        header_row.append('Tint1 (ms)')
                    if np.nansum(tint2)>0:
                        header_row.append('Tint2 (ms)')
                    if np.nansum(binning)>0:
                        header_row.append('Spectral_Binning')
                    if np.nansum(binning2)>0:
                        header_row.append('Spectral_Bining2')
                    if np.nansum(temp)>0:
                        header_row.append('Temp, K')
                    out_file.writerow(header_row)
                else:
                    out_line = [args.inputfiles[i]]
                    if len(dates)==len(nbands):
                        out_line.append(dates[i])
                    if len(start_times)==len(nbands):
                        out_line.append(start_times[i])
                    if len(stop_times)==len(nbands):
                        out_line.append(stop_times[i])
                    if np.nansum(nbands)>0:
                        out_line.append(nbands[i])
                    if np.nansum(nsamples)>0:
                        out_line.append(nsamples[i])
                    if np.nansum(nlines)>0:
                        out_line.append(nlines[i])
                    if np.nansum(fps)>0:
                        out_line.append(fps[i])
                    if np.nansum(tint)>0:
                        out_line.append(tint[i])
                    if np.nansum(tint1)>0:
                        out_line.append(tint1[i])
                    if np.nansum(tint2)>0:
                        out_line.append(tint2[i])
                    if np.nansum(binning)>0:
                        out_line.append(binning[i])
                    if np.nansum(binning2)>0:
                        out_line.append(binning2[i])
                    if np.nansum(temp)>0:
                        out_line.append(temp[i])
                    out_file.writerow(out_line)

        print("csv file written to {}".format(args.outcsv))
