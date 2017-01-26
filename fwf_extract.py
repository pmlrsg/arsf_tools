#! /usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################


#To run:
# python fwf_extract.py LAS1.3_filename
#
#
# Requires las1_3_handler.py
#
#

import las1_3_handler
import os
import sys
import argparse

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('f', metavar ='<filename>',help ='LAS file to extract data from',default=0)
    parser.add_argument('-o', metavar = 'output dir', help ='directory to output ASCII files (defaults to current directory if not specified)',default=0)
    parser.add_argument('--area', type=float, nargs=4, metavar =('North', 'South', 'East', 'West'), help = 'limits of area you wish to extract. If not specified you will be asked to enter them interactively on the command line',default= (0,0,0,0))
    parser.add_argument('--header', dest ='print_header', action='store_const', const=1, default=0,help ='outputs the header information of the LAS file')
    parser.add_argument('--plottoscreen', dest ='plottoscreen', action='store_true', default=False,help ='Plot all waveforms to the screen')
    parser.add_argument('--plottofile', dest ='plottofile', type=str,nargs=1,default=[None],help ='Plot all waveforms to a PDF file')

    args = parser.parse_args()
    user_limits = args.area
    las_file = args.f
    output_dir = args.o
    print_header= args.print_header

# gets the header data from the LAS 1.3 file & check file is in correct format
    headdata=las1_3_handler.readLASHeader(las_file)

# if --header is specified, print the header to sceen
    if print_header == 1:
        las1_3_handler.printLASHeader(headdata,las_file)

    #end if
    if output_dir == 0:
        print "\nOutput directory was not specified, will use current directory\n"
        output_dir = os.getcwd()+'/'
    else:
        output_dir = os.path.abspath(output_dir)+'/'

    #end if

# Only POINT DATA RECORD FORMAT 4 implemented
    if headdata[16] != 4:
        print "Point data record format %d not suported (only point data record format 4 implemented)" %headdata[16]
        sys.exit(1)
        #end if

     # check output data location is writeable
    try:
        test=output_dir+"temp_file.txt"
        try_file = open(test, "w")
    except :
        print "\nOutput directory %s is not writeable" %output_dir
        print "Please change directory or specify a writeable output directory using -o /path/to/dir\n"
        sys.exit(1)
    #remove temp file
    os.remove(test)
    #end try




# Limits of the LAS 1.3 file
    Max_x= headdata[30]
    Max_y= headdata[32]
    Min_x= headdata[31]
    Min_y= headdata[33]

# if user limits were not specified on the command line ask user to input them
    if user_limits == (0,0,0,0):
        user_limits = las1_3_handler.getUserInput(headdata)
    #end if

# area for extraction
    max_north = user_limits[0]
    min_north = user_limits[1]
    max_east = user_limits[2]
    min_east = user_limits[3]

# check specified area is valid
    if max_north > Max_y or min_north < Min_y :
        print "Error with northing values entered (max %f min %f)\n" %(max_north, min_north)
        print "Northing values must be between %f and %f " %(Min_y,Max_y)
        print "Please check user inputs and try again \n"
        sys.exit(1)
    elif max_north < min_north:
        print "Error with northing values entered (max %f min %f)\n" %(max_north, min_north)
        print "Min Northing %f must be less than Max Northing %f" %(min_north,max_north)
        print "Please check user inputs and try again \n"
        sys.exit(1)
    elif max_east > Max_x or min_east < Min_x:
        print "Error with easting values entered (max %f min %f)\n" %(max_east, min_east)
        print "Easting values must be between %f and %f " %(Min_x,Max_x)
        print "Please check user inputs and try again \n"
        sys.exit(1)
    elif max_east < min_east:
        print "Error with easting values entered (max %f min %f)\n" %(max_east, min_east)
        print "Min East %f must be less than Max East %f" %(min_east,max_east)
        print "Please check user inputs and try again \n"
        sys.exit(1)
       #end if

     #end if

# run the Las 1.3 extractions
    las1_3_handler.readLASWaves(headdata,las_file, output_dir,user_limits,plottoscreen=args.plottoscreen,plotfile=args.plottofile[0])


main(sys.argv[1:])
