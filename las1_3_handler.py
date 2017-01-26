#! /usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

###
# Python library for reading Las1.3 header files and extracting ASCII full
# waveform information for a specified area
#
#Available Functions:
# readLASHeader: reads an LAS 1.3 file into a list of records (only saves records headers)
# printLASHeader: prints Public Header formatted from LAS 1.3 file
# writeWaveform: creates waveform files, one file per waveform
# getUserInput: request user to input area for waveform data extraction
# readLASWaves: function that extracts waveforms from LAS 1.3 file
# plotWaveform: function to plot a waveform
#
#
################
# Public Header(usually 243 bytes)
################
# 0 File Signature (“LASF”)              char[4]            4 bytes  *
# 4 File Source ID                       unsigned short     2 bytes  *
# 6 Global Encoding                      unsigned short     2 bytes  *
# 8 Project ID - GUID data 1             unsigned long      4 bytes
# 12 Project ID - GUID data 2             unsigned short     2 byte
# 14 Project ID - GUID data 3             unsigned short     2 byte
# 16 Project ID - GUID data 4             unsigned char[8]   8 bytes
# 24 Version Major                        unsigned char      1 byte   *
# 25 Version Minor                        unsigned char      1 byte   *
# 26 System Identifier                    char[32]           32 bytes *
# 58 Generating Software                  char[32]           32 bytes *
# 90 File Creation Day of Year            unsigned short     2 bytes  *
# 92 File Creation Year                   unsigned short     2 bytes  *
# 94 Header Size                          unsigned short     2 bytes  *
# 96 Offset to point data                 unsigned long      4 bytes  *
# 100 Number of Variable Length Records    unsigned long      4 bytes  *
# 104 Point Data Format ID (0-99 for spec) unsigned char      1 byte   *
# 105 Point Data Record Length             unsigned short     2 bytes  *
# 107 Number of point records              unsigned long      4 bytes  *
# 111 Number of points by return           unsigned long[7]   28 bytes *
# 139 X scale factor                       Double             8 bytes  *
# 147 Y scale factor                       Double             8 bytes  *
# 155 Z scale factor                       Double             8 bytes  *
# 163 X offset                             Double             8 bytes  *
# 171 Y offset                             Double             8 bytes  *
# 179 Z offset                             Double             8 bytes  *
# 187 Max X                                Double             8 bytes  *
# 195 Min X                                Double             8 bytes  *
# 203 Max Y                                Double             8 bytes  *
# 211 Min Y                                Double             8 bytes  *
# 219 Max Z                                Double             8 bytes  *
# 227 Min Z                                Double             8 bytes  *
# 235 Start of Waveform Data Packet Record Unsigned long long 8 bytes  *

""" Module to read Fullwaveform LiDAR files format LAS 1.3 """

import re
import sys
import os
import os.path
import struct
import math
import warnings
import pylab
from matplotlib.backends.backend_pdf import PdfPages

public_header_length = 235 # Public Header length in bytes.
VbleRec_header_length = 54 # Variable Length Record Header length in bytes
EVLR_length = 60 #Extended Variable Lenght Record Header, in Version 1.3 the only EVLR is waveform data packets
point_data_length = 57
light_speed = 0.299792458 #meters per nanosecond
point_scale_factors=[] #Contained in  the file header, these scale factors must be applied to each point x,y,z
point_offsets=[] #Contained in  the file header, these scale factors must be applied to each point x,y,z
pub_head_format = "=4sHHlHH8sBB32s32sHHHLLBHL5L12dQ"
VbleRec_head_format="=H16sHH32s"
EVLR_format="=H16sHQ32s"
point_data_format="=3lHBBbBBBdBQL4f" #Note it should be 3lHBBbHBdBQL4f but User data (field [7]) is decomposed in two :0,gain
wv_packet_format = "=cclldd"

##
#Function readLASHeader
# Reads an LAS 1.3 file into a list of records (only saves records headers)
# V0.0: only reads point records type 4 (it doesn't even check if it's a different type)
#
# Arguments:
#  filename: Name of LAS file to read
#
# Returns:
#  headdata: Header values
##

def readLASHeader(filename):
    tb=None

    # Check given file exists

    if (not os.path.isfile(filename)):
        print "\nFile " + filename + " does not exist"
        print "Please check your file location and try again \n"
        sys.exit(1)
    #end if

    # Check the file ends in *.LAS
    basename, extension = os.path.splitext(filename)

    if extension != ".LAS":
        print "\nFile " + filename + " is not a *.LAS file"
        print "Please specify a LAS file on the command line\n"
        sys.exit(1)
    #end if

    # Open the LAS file
    try:
        lasfile = open(filename, "rb")
    except IOError:
        print "\nCould not open LAS file " + filename
        print "Please check your file permissions and try again\n"
        sys.exit(1)
    #end try

    # Read the public header
    try:
        record = lasfile.read(public_header_length)
    except:
        tb = sys.exc_info()[2]
        print "\nReading failed on input LAS file " + filename
        sys.exit(1)
    #end try

       # Unpack data from binary to list and append to output
    headdata = struct.unpack(pub_head_format, record)

    lasfile.close()

# Only LAS 1.3 (full wave form data) implemented
    version=str(headdata[7])+'.'+str(+headdata[8])

    if version != '1.3':
        print "\nSpecified file is a LAS %s.%s file, not a LAS 1.3 file" % (headdata[7], headdata[8])
        print "Please check your file and try again \n"
        sys.exit(1)
    #end if

    return(headdata)

# end function


##
# Function printLASHeader
# Prints Public Header formatted from LAS 1.3 file.
#
# Arguments:
#  headdata: header as returned by ReadLASHeader
#  filename: filename of LAS1.3 file
##

def printLASHeader(headdata,filename):

    print "\nHeader file of " , filename
    print "File Signature (“LASF”) ", headdata[0]
    print "File Source ID  ", headdata[1]
    print "Global Encoding ", headdata[2]
    print "Project ID - GUID data 1 ", headdata[3]
    print "Project ID - GUID data 2 ", headdata[4]
    print "Project ID - GUID data 3 ", headdata[5]
    print "Project ID - GUID data 4 ", headdata[6]
    print "Version Major %c" % headdata[7]
    print "Version Minor ", headdata[8]
    print "System Identifier ", headdata[9]
    print "Generating Software ", headdata[10]
    print "File Creation Day of Year  ", headdata[11]
    print "File Creation Year ", headdata[12]
    print "Header Size    ", headdata[13]
    print "Offset to point data ", headdata[14]
    print "Number of Variable Length Records ", headdata[15]
    print "Point Data Format ID (0-99 for spec) ", headdata[16]
    print "Point Data Record Length ", headdata[17]
    print "Number of point records ", headdata[18]
    print "Number of points by return  ", headdata[19:23]
    print "X scale factor ", headdata[24]
    print "Y scale factor  ", headdata[25]
    print "Z scale factor ", headdata[26]
    print "X offset  ", headdata[27]
    print "Y offset  ", headdata[28]
    print "Z offset ", headdata[29]
    print "Max X  ", headdata[30]
    print "Min X  ", headdata[31]
    print "Max Y  ", headdata[32]
    print "Min Y ", headdata[33]
    print "Max Z  ", headdata[34]
    print "Min Z  ", headdata[35]
    print "Start of Waveform Data Packet Record ", headdata[36] , "\n"

#end function


##
#Function writeWaveform
# Creates waveform files, one file per waveform.
#
# Arguments:
#  wavedata: wavedata[0][*] contains the point info (point data record format 4)
#            wavedata[1][*] contains the amplitude values
#  wv_info: contains generic information about the waveforms as read from the Waveform Packet Descriptor"""
#  output_dir: directory to output ASCII files to
##

def writeWaveform(wavedata,wv_info,output_dir):

    GPStime= wavedata[0][10]
    sampling=wv_info[3]/1000.0 #sampling frequency in nanoseconds
    sample_length=sampling*light_speed/2
    #wv_filename="waveform_%0.6d_%0.6d_%d.txt"%(int(GPStime),(int(round((math.modf(wavedata[0][10])[0])*1000000))),int(wavedata[0][4]&7))
    wv_filename=output_dir+"waveform_%0.6d_%0.6d_%d.txt"%(int(GPStime),int(round((math.modf(GPStime)[0])*1000000)),int(wavedata[0][4]&7))
    wvfile = open(wv_filename, "w")

    w_point=[0,0,0]
    for i in range(3):
        w_point[i]=wavedata[0][i]*point_scale_factors[i]+point_offsets[i]
    #end for

    print >>wvfile, "Point {0:31} {1} {2} {3}".format("", wavedata[0][0]*point_scale_factors[0], wavedata[0][1]*point_scale_factors[1], wavedata[0][2]*point_scale_factors[2])
    print >>wvfile, "Return Number {0:23} {1}".format("", int(wavedata[0][4]&7))
    print >>wvfile, "Number of returns for this pulse {0:4} {1}".format("", int((wavedata[0][4]& 56)/8))
    print >>wvfile, "Time {0:32} {1}".format("", wavedata[0][10])
    print >>wvfile, "Scan Angle {0:26} {1}".format("", wavedata[0][6])
    print >>wvfile, "Classification {0:22} {1}".format("", wavedata[0][5])
    print >>wvfile,"Temporal Sample Spacing  {0:12} {1}".format("", sampling)
    #Temporal Sample Spacing(sample rate Ms): 1000 = 1 nanosecond, 500 = 2 nanoseconds
    print >>wvfile, "AGC gain {0:28} {1}".format("", wavedata[0][8])
    print >>wvfile,"Digitiser Gain {0:22} {1}".format("",wv_info[4])
    print >>wvfile,"Digitiser Offset {0:20} {1}".format("", wv_info[5]) # Digitizer offset (seems to be always 0)

    print >>wvfile, "No. of Samples {0:22} {1}".format("", wavedata[0][13])
    print >>wvfile, "Sample Length {0:23} {1}".format("", sample_length)
    print >>wvfile, "Return Point Location {0:15} {1}".format("", wavedata[0][14]/1000)
    # offset in nanooseconds from the first digitized value to the location within the waveform packet that the associated return
    # pulse was detected

    print >>wvfile, "Point in Waveform {0:19} {1}".format("", wavedata[0][14]*light_speed/2/1000) #/1000 to convert from pico to nanoseconds


    print >>wvfile, "X Offset {0:28} {1}".format("", wavedata[0][15]*1000*sampling) # *1000 to convert from km to meters *sampling to get offset between each sample
    print >>wvfile, "Y Offset {0:28} {1}".format("", wavedata[0][16]*1000*sampling) # *1000 to convert from km to meters *sampling to get offset between each sample
    print >>wvfile, "Z Offset {0:28} {1}".format("", wavedata[0][17]*1000*sampling) # *1000 to convert from km to meters *sampling to get offset between each sample

    #output a warning if the z offset is -ve. This is not necessarily a problem but it could mean that the vector has been
    #stored in the LAS file incorrectly (opposite signs to standard) as was the case with some LAS files produced with an early version of ALSPP
    if wavedata[0][17] > 0:
        print "WARNING: Z offset vector component is positive - this may mean that the vector has been stored in the LAS file with opposite sign to standard."
        print "If this is the case then waveform and origin positions will be incorrect. If you expect Z to increase from the lidar to the target then this is probably not a problem."

    # Calculating origin from: X=xo+x(t)
    xo= w_point[0]- wavedata[0][15]*wavedata[0][14]
    yo= w_point[1]- wavedata[0][16]*wavedata[0][14]
    zo= w_point[2]- wavedata[0][17]*wavedata[0][14]
    #print >>wvfile, "Xo\t", xo
    #print >>wvfile, "Yo\t", yo
    #print >>wvfile, "Zo\t",  zo
    print >>wvfile, "Intensity  X  Y  Z"

    for i in range(len(wavedata[1])):
        print >>wvfile, wavedata[1][i],round(xo,4),round(yo,4),round(zo,4)
        xo+=(wavedata[0][15]*sampling*1000)
        yo+=(wavedata[0][16]*sampling*1000)
        zo+=(wavedata[0][17]*sampling*1000)
    #end for

    wvfile.close()

#end function

##
# Function getUserInput
# Request user to input area for waveform data extraction
#
# Arguments:
#  headdata: header as returned by ReadLASHeader
#
# Returns:
#  user_inputs[N,S,E,W]: area seleceted by user for full waveform extraction
##

def getUserInput(headdata):

    Max_x= headdata[30]
    Max_y= headdata[32]
    Min_x= headdata[31]
    Min_y= headdata[33]

    attempt=0

        #Read user limits
    print "Enter limits of the area to extract:"
    try:
        max_north = float(raw_input("Enter Max North (Range %f-%f)"%(Min_y,Max_y)))
    except:
        print "Invalid value entered"
        try :
            max_north = float(raw_input("Enter Max North (Range %f-%f)"%(Min_y,Max_y)))
        except:
            print "Invalid value entered"
            print "Please check your data and try again\n"
            sys.exit(1)

    while max_north > Max_y or max_north < Min_y:
        if attempt >= 2:
            print
            print "Specified max y value is not valid"
            print "Please check your data and try again\n"
            sys.exit(1)
        else :
            print
            print "Max north must be between " , Min_y, "and ", Max_y
            print
            try:
                max_north = float(raw_input("Enter Max North (Range %f-%f)"%(Min_y,Max_y)))
            except:
                print "Invalid value entered"
                try :
                    max_north = float(raw_input("Enter Max North (Range %f-%f)"%(Min_y,Max_y)))
                except:
                    print "Invalid value entered"
                    print "Please check your data and try again\n"
                    sys.exit(1)
            attempt+=1
        #end if

    try:
        min_north = float(raw_input("Enter Min North (Range %f-%f)"%(Min_y,max_north)))
    except:
        print "Invalid value entered"
        try :
            min_north = float(raw_input("Enter Min North (Range %f-%f)"%(Min_y,max_north)))
        except:
            print "Invalid value entered"
            print "Please check your data and try again\n"
            sys.exit(1)


    while min_north > max_north or min_north < Min_y:
        if attempt >= 2:
            print
            print "Specified min y value is not valid"
            print "Please check your data and try again\n"
            sys.exit(1)
        else :
            print
            print "Min north must be between " , Min_y, "and ", max_north
            print
            try:
                min_north = float(raw_input("Enter Min North (Range %f-%f)"%(Min_y,max_north)))
            except:
                print "Invalid value entered"
                try :
                    min_north = float(raw_input("Enter Min North (Range %f-%f)"%(Min_y,max_north)))
                except:
                    print "Invalid value entered"
                    print "Please check your data and try again\n"
                    sys.exit(1)
            attempt+=1
        #end if


    try:
        max_east = float(raw_input("Enter Max East (Range %f-%f)"%(Min_x,Max_x)))
    except:
        print "Invalid value entered"
        try :
            max_east = float(raw_input("Enter Max East (Range %f-%f)"%(Min_x,Max_x)))
        except:
            print "Invalid value entered"
            print "Please check your data and try again\n"
            sys.exit(1)



    while max_east > Max_x or max_east < Min_x:
        if attempt >= 2:
            print
            print "Specified max x value is not valid"
            print "Please check your data and try again\n"
            sys.exit(1)
        else :
            print
            print "Max east must be between " , Min_x, "and ", Max_x
            print
            try:
                max_east = float(raw_input("Enter Max East (Range %f-%f)"%(Min_x,Max_x)))
            except:
                print "Invalid value entered"
                try :
                    max_east = float(raw_input("Enter Max East (Range %f-%f)"%(Min_x,Max_x)))
                except:
                    print "Invalid value entered"
                    print "Please check your data and try again\n"
                    sys.exit(1)
            attempt+=1
        #end if


    try:
        min_east = float(raw_input("Enter Min East (Range %f-%f)"%(Min_x,max_east)))
    except:
        print "Invalid value entered"
        try :
            min_east = float(raw_input("Enter Min East (Range %f-%f)"%(Min_x,max_east)))
        except:
            print "Invalid value entered"
            print "Please check your data and try again\n"
            sys.exit(1)

    while min_east > max_east or min_east < Min_x:
        if attempt >= 2:
            print
            print "Specified min x value is not valid"
            print "Please check your data and try again"
            sys.exit(1)
        else :
            print
            print "Min east must be between " , Min_x, "and ", max_east
            print
            try:
                min_east = float(raw_input("Enter Min East (Range %f-%f)"%(Min_x,max_east)))
            except:
                print "Invalid value entered"
                try :
                    min_east = float(raw_input("Enter Min East (Range %f-%f)"%(Min_x,max_east)))
                except:
                    print "Invalid value entered"
                    print "Please check your data and try again\n"
                    sys.exit(1)
            attempt+=1
        #end if

    #end if

    user_inputs=[max_north, min_north, max_east, min_east]

    return (user_inputs)

#end function

##
# Function readLASWaves
# Function that extracts waveforms from LAS 1.3 files.
#
# Arguments:
#  headdata: header as returned by ReadLASHeader
#  filename: LAS 1.3 file to extract data from
#  user_limits: area to be extracted
#  plottoscreen: whether to plot waveforms to screen
#  plotfile: name of a pdf file to plot to
#
# Returns:
#  creates one output filr for waveform named waveform_tttttt_tttttt_x.txt where x indicates the number of return: 1 for first return, 2 for second return...etc"""
##

def readLASWaves(headdata,filename,output_dir,user_limits,plottoscreen=False,plotfile=None):

    record = ""
    tb=None

    # check output data location is writeable
    try:
        test=output_dir+"temp_file.txt"
        try_file = open(test, "w")
    except :
        print "\nOutput directory %s is not writeable" %output_dir
        print "Please change directory or specify an output directory using -o /path/to/dir\n"
        sys.exit(1)
    #remove temp file
    os.remove(test)
    #end try

    lasfile = open(filename, "rb")

    try:
        record = lasfile.read(public_header_length)
    except:
        tb = sys.exc_info()[2]
        print "Reading failed on input LAS file " + filename + "\n"
        sys.exit(1)
    #end try

    if plotfile != None:
        pdfplots = PdfPages(plotfile)
    else:
        pdfplots=None

    #printPubHeader(headdata)
    point_scale_factors.append(headdata[24]) # X scale factor
    point_scale_factors.append(headdata[25]) # Y scale factor
    point_scale_factors.append(headdata[26]) # Z scale factor
    point_offsets.append(headdata[27]) # X offset
    point_offsets.append(headdata[28]) # Y offset
    point_offsets.append(headdata[29]) # Z offset

   # Read as many records as indicated on the header
    N_vble_rec= headdata[15]


    for v_rec in range(N_vble_rec):
        try:
            v_record = lasfile.read(VbleRec_header_length)
        except:
            tb = sys.exc_info()[2]
            raise IOError, "Reading failed on input LAS file while reading Vble length record " + filename, tb
        #end try

        headdata_rec = struct.unpack(VbleRec_head_format, v_record)

        Rec_length = headdata_rec[3]

        skip_record = lasfile.read(Rec_length)


#If RecordID= 1001 it is the intensity histogram
# of 1st returns w/ intensity of 0
# of 1st returns w/ intensity of 1
# of 1st returns w/ intensity of 2
#…
# of 1st returns w/ intensity of 255
# of 2nd returns w/ intensity of 0
# of 2nd returns w/ intensity of 1
# of 2nd returns w/ intensity of 2
#…
# of 2nd returns w/ intensity of 255
# of 3rd returns w/ intensity of 0
# of 3rd returns w/ intensity of 1
# of 3rd returns w/ intensity of 2
#…
# of 3rd returns w/ intensity of 255
# of returns with AGC value of 0
# of returns with AGC value of 1
# of returns with AGC value of 2
#…
# of returns with AGC value of 255
# of all returns with intensity of 0
# of all returns with intensity of 1
# of all returns with intensity of 2
#…
# of all returns with intensity of 255

        if (headdata_rec[2] == 1001):
            i_hist = struct.unpack("=%dl" %(Rec_length/4),skip_record)
            #print i_hist
        #end if

#If RecordID= 1002 it is Leica mission info containing
#0_ Laser Pulserate: 1 Hz
#1_ Field Of View: 0.1 degrees
#2_ Scanner Offset: 1 ticks
#3_ Scan Rate:  0.1 Hz
#4_ Flying Altitude (AGL): meters
#5_ GPS Week Number at start of line:   week
#6_ GPS Seconds of Week at start of line: seconds
#7_ Reserved
#NOTE Leica definition says this record contains 26 bytes but it actually contains only 22 so not sure what is what...
# By comparisson with FlightLineLog fields 0,3,4,5 and 6 are ok


        if (headdata_rec[2] == 1002):
            mis_info = struct.unpack("=lHHhhhll",skip_record)
            #print mis_info
            laser_pulse_rate=mis_info[0]
            field_of_view=mis_info[1]
            scanner_offset=mis_info[2]
            scan_rate=mis_info[3]
            fly_altitude=mis_info[4] # Corresponds to the Nadir Range in the FlightLineLog
        #end if

#If RecordID= 1003 it is User inputs containing:
# IMU Roll Correction
# IMU Pitch Correction
# IMU Heading Correction
# POS Time Offset
# Range Offset – Return 1
# Range Offset – Return 2
# Range Offset – Return 3
# Range Offset – Return 4
# Range Offset – Return 5
# Elevation Offset
# Scan Angle Correction
# Encoder Latency
# Torsion Constant
# Scanner Ticks Per Revolution
# Low Altitude Temperature
# High Altitude Temperature
# Low Altitude
# High Altitude
# Temperature Gradient


        if (headdata_rec[2] == 1003):
            user_info = struct.unpack("=3l9hll4hd",skip_record)
            #print user_info
        #end if

#If RecordID>= 100 it is a waveform Packet Descriptor

        if (headdata_rec[2] >= 100) and (headdata_rec[2] < 356):

            wv_info = struct.unpack("=cclldd",skip_record)
        #end if

    #end for

    # Read points
    Size_points = headdata[17]
    N_points = headdata[18]
    Offset_points = headdata[14]
    Offset_EVLRH = headdata[36]

    max_north = user_limits[0]
    min_north = user_limits[1]
    max_east = user_limits[2]
    min_east = user_limits[3]

    # Move to first point
    lasfile.seek(Offset_points)
    count =0
    c_point=[0,0]
    print "Starting to process %d points" %N_points
    print "Will output ASCII files to ", output_dir

    for p in range(N_points):
        Point = lasfile.read(Size_points)
        point_info = struct.unpack(point_data_format,Point)
        c_point=[0,0]
        return_num=(point_info[4]&7)
        n_returns=(point_info[4] & 56)
        scan_dir=(point_info[4]&64)/64
        edge_fl=(point_info[4]&128)/128
        c_point[0]=(point_info[0]*point_scale_factors[0])+point_offsets[0]
        c_point[1]=(point_info[1]*point_scale_factors[1])+point_offsets[1]
        if  min_east<c_point[0]<max_east and min_north<c_point[1]< max_north:
            wave_desc = point_info[11]

            if wave_desc <> 0: # if there is waveform asociated to this point
                wavedata = []
                wavedata.append(point_info)
                wave_offset = Offset_EVLRH + point_info[12]
                wave_size = point_info[13]

                tmp= lasfile.tell() #saves current position in input file before jumpin to wave info
                lasfile.seek(wave_offset)
                wave_dat = lasfile.read(wave_size)
                wave_data = struct.unpack("=%db" %wave_size, wave_dat)
                wavedata.append(wave_data)

                writeWaveform(wavedata,wv_info,output_dir)

                if plottoscreen != False or plotfile != None:
                    plotWaveform(wavedata,wv_info[3]/1000.0,fileobj=pdfplots,title="waveform_%0.6d_%0.6d_%d.txt"%(int(wavedata[0][10]),int(round((math.modf(wavedata[0][10])[0])*1000000)),int(wavedata[0][4]&7)))

                lasfile.seek(tmp) # Goes back to next point in file

                count+=1
            #end if
        #end if
    #end for

    if plotfile != None:
        pdfplots.close()

    if count==0:
        print "\nNo wave forms have been found for the specified area"
        print "Please check your data and try again\n"
    else:
        print "Number of extracted waves:", count

    #end if

    # After points, read EVLR
    #It doesn't contain anything useful really... so commented out
#  try:
#    evlr_record = lasfile.read(EVLR_length)
#  except:
#    tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
#    raise IOError, "Reading failed on input LAS file while reading Vble length record " + filename, tb
#  #end try

#  if len(evlr_record) != struct.calcsize("=H16sHQ32s"):
#    raise Exception("Extended VLR length is not equal to expected size")
#
#  evlr_data = struct.unpack("=H16sHQ32s", evlr_record)
#  #It doesn't contain anything useful really...
#  #print "Extended Variable Length Record Header:", evlr_data

    lasfile.close()

#end function

# Function to plot the waveforms either to the screen interactively or to a pdf file
def plotWaveform(waveform,sampletime,fileobj=None,title=None):
       #plot the waveform data as a blue line
    pylab.plot(waveform[1],'b-',label='Waveform')
    #plot the discrete point as a red circle - x position is return point location, y is intensity
    pylab.plot(waveform[0][14]/(1000*sampletime),waveform[0][3],'ro',label='Discrete')
    #add axis labels
    pylab.xlabel('Sample number')
    pylab.ylabel('Intensity')
    #if a title has been given then add it
    if title != None:
        pylab.title(title)
    #set the lower y limit to be 0 and the upper to be 5 higher than it is already
    pylab.ylim([0,pylab.ylim()[1]+5])
    #add a basic legend
    pylab.legend()
    #if a fileobj has been passed then save the plot to the file
    #else show it on the screen
    if fileobj != None:
        fileobj.savefig()
        pylab.clf()
    else:
        pylab.show()
