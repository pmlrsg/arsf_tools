#!/usr/bin/env python
"""
Apply Savitzky-Golay filter to an ENVI BIL file

Uses scipy

http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html

And arsf_envi_reader (available from: https://github.com/pmlrsg/arsf_tools)

Dan Clewley
16/06/2016

"""

from __future__ import print_function
import argparse
from scipy import signal

from arsf_envi_reader import numpy_bin_reader
from arsf_envi_reader import envi_header

POLY_ORDER = 3
WINDOW_SIZE = 7

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inputimage", nargs=1,
                        type=str, help="Input image")
    parser.add_argument("outputimage", nargs=1,
                        type=str, help="Output image")
    args = parser.parse_args()

    # Open input file
    in_data = numpy_bin_reader.BilReader(args.inputimage[0])

    # Open file for output
    out_file = open(args.outputimage[0], "wb")

    for i, line in enumerate(in_data):
        print(" Line {0}/{1}".format(str(i).zfill(len(str(in_data.lines))),
                                     in_data.lines), end="\r")
        # Apply filter
        out_line = signal.savgol_filter(line,
                                        WINDOW_SIZE, POLY_ORDER,
                                        axis=0)
        # Remove negative values
        out_line[out_line < 0] = 0
        # Set output to the same as input
        out_line = out_line.astype(line.dtype)
        out_line.tofile(out_file)

    print(" Line {0}/{0}".format(in_data.lines), end="\n")

    # Copy header
    envi_header.write_envi_header(args.outputimage[0] + ".hdr",
                                  in_data.get_hdr_dict())

    # Close files
    out_file.close()
    in_data = None
