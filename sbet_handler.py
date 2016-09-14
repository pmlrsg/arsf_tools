#! /usr/bin/env python

# Library to read and write Applanix's SBET (Smoothed Best Estimate of Trajectory) format
# Also reads/writes AISA's nav file format
#
# Author: Ben Taylor
# Last edited: 20th Jul 2010
#
# Change history:
# 7th May 2009: Created
# 10th Jun 2009: Added writeNav function
# 11th Aug 2009: Added getPosition and checkApproxEquality functions
# 12th Aug 2009: Rewrote getPosition to be more efficient, removed checkApproxEquality (no longer used, not appropriate 
#                to this library on its own), added readNav function
# 13th Aug 2009: Updated readNav to allow returning partial output
# 8th Oct 2009: Minor fix to readNav to make it return partial output in more circumstances and to be able to scan corrupt files
# 26th Oct 2009: Added index_only option to getPosition
# 20th Jul 2010: Added getBounds function
#
# Available functions:
# sbetKey: takes the name of a record field and returns the index
# readSbet: Reads an SBET file into a list of records
# writeSbet: Writes an SBET file from a list of (appropriately-ordered) records
# readNav: Reads a nav file into a list of records
# writeNav: Writes an AISA nav file from a list of (appropriately-ordered) records
# getPosition: Gets the position record closest to a specified GPS time
# getBounds: Gets the north, south east and west boundaries of an SBET file
#
# You may use or alter this script as you wish, but no warranty of any kind is offered, nor is it guaranteed 
# not to cause security holes in an unsafe environment.

# SBET format contains the following fields (all 8-byte double-precision, in order).
# All must be set in the input data array to be able to write an SBET, and they will
# be returned in this order when reading one.
#
# 1: GPS time (s)
# 2: Latitude (rad)
# 3: Longitude (rad)
# 4: Altitude (m)
# 5: E-W velocity (m/s)
# 6: N-S velocity (m/s)
# 7: Vertical velocity (m/s)
# 8: Attitude roll component (rad)
# 9: Attitude pitch component (rad)
# 10: Attitude heading component (rad)
# 11: Wander angle (rad)
# 12: E-W acceleration (m/s^2)
# 13: N-S acceleration (m/s^2)
# 14: Vertical acceleration (m/s^2)
# 15: X-axis angular rate (rad/s)
# 16: Y-axis angular rate (rad/s)
# 17: Z-axis angular rate (rad/s)

import re
import sys
import os
import os.path
import struct
import math
import warnings

record_length = 136 # Record length in bytes of an SBET record
nav_record_length = 28 # Record length in bytes of a nav record
sync_record_length = 14 # Record length in bytes of a sync record
sbet_rec_format = "=ddddddddddddddddd" # Record format for SBET record - 17 double-precision fields
nav_rec_format = "=hdhhHiihh" # Record format for nav record - short-double-short-short-Ushort-int-int-short-short (standard size, leaving it as native causes pain on 64-bit machines, believe me)
sync_rec_format = "=hhhhhhh" # Record format for specim sync record - 7 signed shorts

# Function sbetkey
# Given the name of a field of the sbet, returns its index in the sbet records
# takes;
# key = field name as a string
# returns;
# record index
def sbetKey(key):
   sbetkeys = ['time','lat','lon','alt','ewspeed','nsspeed','vertspeed','roll','pitch','heading','wander','ewacc','nsacc','vertacc','xacc','yacc','zacc']
   return sbetkeys.index(key)

# Function sbetToDailyGps
# Given a SBET list, will convert the GPS times to daily
# takes;
# sbetData = SBET record list
# returns;
# sbetData, times converted to daily
def sbetToDailyGps(sbetData):
   secondsInDay = 24 * 60 * 60
   gpsTimeIndex = sbetKey('time')
   for record in sbetData:
      record[gpsTimeIndex] = record[gpsTimeIndex] % secondsInDay
   return sbetData

# Function readSbet
# Reads an SBET file into a list of records
#
# Arguments:
# filename: Name of SBET file to read
#
# Returns: List of records read from the SBET file
def readSbet(filename):
    
    record = ""
    output = []
    
    # Check given file exists
    if (not os.path.isfile(filename)):
        raise IOError, "File " + filename + " does not exist or is not a file"
    # end if
    
    # Open the SBET file
    try:
        sbet = open(filename, "rb")
    except:
        raise IOError, "Could not open SBET file " + filename, sys.exc_info()[2]
    # end try
    
    # Read the first record
    try:
        record = sbet.read(record_length)
    except:
        tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
        try:
            sbet.close()
        except:
            pass
        # end try
        raise IOError, "Reading failed on input SBET file " + filename, tb
    finally:
        tb = None # Break circular reference
    # end try
    
    # For each record read from the file
    while (record != ""):
    
        # If we ran out of file before we got a whole record, this probably isn't a valid SBET
        if (len(record) < record_length):
            raise IOError, "SBET record length was shorter than expected, file may be corrupt or not an SBET file"
        # end if
        
        # Unpack data from binary to list and append to output
        recdata = struct.unpack(sbet_rec_format, record)
        output.append(recdata)
        
        # Read the next record
        try:
            record = sbet.read(record_length)
        except:
            tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
            try:
                sbet.close()
            except:
                pass
            # end try
            raise IOError, "Reading failed on input SBET file " + filename, tb
        finally:
            tb = None # Break circular reference
        # end try
    # end while
    
    # Close the file
    try:
        sbet.close() # Don't really care if this fails
    except:
        pass
    # end try
    
    return output
# end function

# Function writeSbet
# Writes an SBET file from a list of (appropriately-ordered) records
#
# Arguments:
# filename: Name of SBET file to write to
# data: List containing records to be written
def writeSbet(filename, data):

    # Open the output file for writing
    try:
        sbet = open(filename, "wb")
    except:
        raise IOError, "Unable to open output SBET file " + filename + " for writing.", sys.exc_info()[2]
    # end try
    
    # For each given record
    for record in data:
    
        # If the record has other than 17 fields, it can't be put into an SBET file - remove the file created
        if (len(record) != 17):
            sbet.close()
            try:
                os.remove(filename)
            except:
                pass
            # end try
            raise ValueError, "Given data contains records with other than 17 fields, SBET files require exactly 17 fields"
        # end if
        
        # Pack the record into a binary string
        datastr = struct.pack(sbet_rec_format, record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14], record[15], record[16])
        
        # Write the packed string to the output file
        try:
            sbet.write(datastr)
        except:
            tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
            # If writing fails, remove the partially-written file
            sbet.close()
            try:
                os.remove(filename)
            except:
                pass
            # end try
            raise IOError, "Failed writing data to output SBET file " + filename, tb
        finally:
            tb = None # Break circular reference
        # end try
    # end for
    
    # Close the file
    try:
        sbet.close()
    except:
        pass
    # end try
# end function

##################################
# Function readNav
# Reads a nav file into a list of records
#
# Arguments:
# filename: Name of nav file to read
# partial: If True then if readNav encounters an invalid nav record it will return the valid 
#       records up to that point rather than raising an error (it will produce a warning instead,
#       and will still raise an error if it fails at the start of the file).
# thorough: If True then if it finds an invalid record it will scan the file byte by byte until it finds
#       another valid record (potentially slow). If False it will just error on the first invalid record.
#
# Returns: List of records read from the nav file
##################################
def readNav(filename, partial=False, thorough=False):
    
    record = False
    output = []
    readall = False
    byte1 = None
    byte2 = None
    
    # Check given file exists
    if (not os.path.isfile(filename)):
        raise IOError, "File " + filename + " does not exist or is not a file"
    # end if
    
    # Open the nav file
    try:
        nav = open(filename, "rb")
    except:
        raise IOError, "Could not open nav file " + filename, sys.exc_info()[2]
    # end try
    
    # For each record read from the file
    while (record != ""):
        
        # If we're in readall mode (ie found corrupt records and reading everything) then read two bytes and see if we've got a record
        if (readall):
            while (readall):
            
                # Read one byte
                try:
                    byte2 = nav.read(1)
                except:
                    try:
                        sbet.close()
                    except:
                        pass
                    # end try
                    raise IOError, "Reading failed on input nav file " + filename
                # end try
                
                # If we've read two bytes then check to see if it looks like the start of a record
                if (byte1 != None):
                    # If we read zero bytes we're at EOF
                    if (len(byte2) == 0):
                        if (not partial):
                            raise IOError, "EOF reached without being in a valid record"
                        else:
                            if (len(output) > 0):
                                warnings.warn("EOF reached without being in a valid record, " + filename + " may be corrupt or not a nav file. Outputting " + str(len(output)) + " valid results so far because partial output specified", UserWarning, 3)
                                try:
                                    nav.close()
                                except:
                                    pass
                                # end try
                                return output
                            else:
                                raise IOError, "EOF reached without being in a valid record"
                            # end if
                        # end if
                    else:
                        # Concatenate the last two bytes we read and unpack them
                        dataitem = struct.unpack("h", byte1 + byte2)[0]
                        
                        # If the number is a start of record flag then we're probably on a new valid record, 
                        # read the rest of the record and then start reading normally
                        if ((dataitem == -28160) or (dataitem == -32257)):
                            try:
                                extra = nav.read(sync_record_length - 2)
                            except:
                                tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
                                try:
                                    sbet.close()
                                except:
                                    pass
                                # end try
                                raise IOError, "Reading failed on input nav file " + filename, tb
                            finally:
                                tb = None # Break circular reference
                            # end try
                            
                            # Add the two bytes we've got to the ones we just read to get the whole record
                            record = byte1 + byte2 + extra
                            readall = False
                        # end if
                    # end if
                # end if
                
                # If we're here then we didn't start a valid record, discard byte1, copy byte2 to byte1 and then scan the next byte
                byte1 = byte2            
            # end while
        else:
            # Read enough for a sync record
            try:
                record = nav.read(sync_record_length)
            except:
                tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
                try:
                    sbet.close()
                except:
                    pass
                # end try
                raise IOError, "Reading failed on input nav file " + filename, tb
            finally:
                tb = None # Break circular reference
            # end try
        # end if
        
        # If we've got a zero-length record we're at EOF
        if (len(record) == 0):
            break
        # end if
    
        # If we ran out of file before we got a whole record, this probably isn't a valid SBET
        if (len(record) < sync_record_length):
            if (not partial):
                raise IOError, "Nav record length was shorter than expected, file may be corrupt or not a nav file"
            else:
                if (len(output) > 0):
                    warnings.warn("Nav record length was shorter than expected, " + filename + " may be corrupt or not a nav file. Outputting " + str(len(output)) + " valid results so far because partial output specified", UserWarning, 3)
                    break
                else:
                    raise IOError, "Nav record length was shorter than expected, file may be corrupt or not a nav file"
                # end if
            # end if
        # end if
        
        # Unpack data from binary to list
        recdata = struct.unpack(sync_rec_format, record)
        
        # If the record starts with -28160, it's a nav record and we need to read more from the file for this record
        if (recdata[0] == -28160):
            
            # Read enough extra bytes to make up a nav record and add them to the end of the previous data
            try:
                record = record + nav.read(nav_record_length - sync_record_length)
            except:
                tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
                try:
                    sbet.close()
                except:
                    pass
                # end try
                raise IOError, "Reading failed on input nav file " + filename, tb
            finally:
                tb = None # Break circular reference
            # end try
            
            # If we ran out of file before we got a whole record, this probably isn't a valid nav file
            if (len(record) < nav_record_length):
                if (not partial):
                    raise IOError, "Nav record length was shorter than expected, file may be corrupt or not a nav file"
                else:
                    if (len(output) > 0):
                        warnings.warn("Nav record length was shorter than expected, " + filename + " may be corrupt or not a nav file. Outputting " + str(len(output)) + " valid results so far because partial output specified", UserWarning, 3)
                        break
                    else:
                        raise IOError, "Nav record length was shorter than expected, file may be corrupt or not a nav file"
                    # end if
                # end if
            # end if
            
            # Unpack data from binary to list (again, format is different)
            recdata = struct.unpack(nav_rec_format, record)
        elif (recdata[0] != -32257):
            # If we get in here then the record is neither a nav record nor a sync record, in which case we don't know
            # what it is and this isn't a valid nav file.
            if (not thorough):
                if (not partial):
                    raise IOError, "Unknown record type encountered (neither nav nor sync), " + filename + " is not a valid nav file."
                else:
                    if (len(output) > 0):
                        warnings.warn("Unknown record type encountered (neither nav nor sync), " + filename + " is not a valid nav file. Outputting " + str(len(output)) + " valid results so far because partial output specified", UserWarning, 3)
                        break
                    else:
                        raise IOError, "Unknown record type encountered at start of file (neither nav nor sync), " + filename + " is not a valid nav file."
                    # end if
                # end if
            else:
                # If we're in here then we need to read byte-by-byte until we find something that looks like a valid record
                readall = True
            # end if
        # end if
        
        # Copy record to output
        if (not readall):       
            output.append(recdata)
        # end if
    # end while
    
    # Close the file
    try:
        nav.close() # Don't really care if this fails
    except:
        pass
    # end try
    
    return output
# end function

# Function writeNav
# Writes an AISA nav file from a list of (appropriately-ordered) records
#
# Arguments:
# filename: Name of nav file to write to
# data: List containing records to be written
def writeNav(filename, data):

    # Open the output file for writing
    try:
        nav = open(filename, "wb")
    except:
        raise IOError, "Unable to open output nav file " + filename + " for writing.", sys.exc_info()[2]
    # end try
    
    # For each given record
    for record in data:
        issync = False
    
        # Check number of records to see if it's a valid nav (9 fields) or sync (7 fields) record
        if (len(record) == 9):
            issync = False
        elif (len(record) == 7):
            issync = True
        else:
            nav.close()
            try:
                os.remove(filename)
            except:
                pass
            # end try
            raise ValueError, "Given data contains records with other than 7 or 9 fields, nav files require exactly 7 or 9 fields"
        # end if
        
        # Pack the record into a binary string
        if (not issync):
            datastr = struct.pack(nav_rec_format, int(record[0]), float(record[1]), int(record[2]), int(record[3]), int(record[4]), int(record[5]), int(record[6]), int(record[7]), int(record[8]))
        else:
            datastr = struct.pack(sync_rec_format, int(record[0]), int(record[1]), int(record[2]), int(record[3]), int(record[4]), int(record[5]), int(record[6]))
        # end if
        
        # Write the packed string to the output file
        try:
            nav.write(datastr)
        except:
            tb = sys.exc_info()[2] # Get traceback (causes circular reference to clean up later)
            # If writing fails, remove the partially-written file
            nav.close()
            try:
                os.remove(filename)
            except:
                pass
            # end try
            raise IOError, "Failed writing data to output nav file " + filename, tb
        finally:
            tb = None # Break circular reference
        # end try
    # end for
    
    # Close the file
    try:
        nav.close()
    except:
        pass
    # end try
# end function

################################
# Function getPosition
# Gets the GPS position closest to the given GPS time from the given SBET file
# Note: This is confusing because it turns out the SBET file actually uses UTC
# (but times it as a time-of-week like GPS). I've elected to leave the variable
# names and comments as GPS time because it's then clear it's a time-of-week.
# Behaviour is unaffected because it just does a straight lookup on the time in
# the file anyway.
# 
# Arguments
# gpstime: GPS time of week to match
# sbet_data: Data list read from an SBET file using readSbet() 
# index_only: If True returns the index position of the matching record rather than the time. Default False
# 
# Returns: A list containing the details for the SBET record found (format as for the SBET file format), or the index of the matching SBET record
# Raises KeyError if the given GPS time was not found in the SBET file
################################
def getPosition(gpstime, sbet_data, index_only=False):
    
    output = []
    mintimeoffset = 1.0
    start_time = sbet_data[0][0]
    second_time = sbet_data[1][0]
    
    # Work out which index the record before the given time will be from the time difference between the records
    # Then start from one earlier than that as insurance against rounding errors
    time_inc = round(float(second_time - start_time), 5)
    time_diff = float(gpstime - start_time)
    search_index = int(math.floor(time_diff / time_inc)) - 1
    
    # If we shifted earlier from the first record, shift back again
    if (search_index == -1):
        search_index = 0
    # end if
    
    # If the time_diff of second/first time is not right and that makes the search_index wrong
    if ((start_time <= gpstime and gpstime <= sbet_data[-1][0]) and ((search_index > len(sbet_data) or search_index < 0) or sbet_data[search_index][0] >= gpstime)):
       search_index = 0

    # Check the calculated index isn't out of range (if it is then the given time is outside the SBET range)
    if ((search_index < 0) or (search_index >= len(sbet_data))):
        raise KeyError, "No SBET records found matching GPS time (outside range)" + str(gpstime)
    # end if
    
    # Loop through the next few records, stop when we've gone past the given time
    while ((search_index < len(sbet_data) - 1) and (sbet_data[search_index][0] <= gpstime)):
    
        # If the time is exactly equal we can just return it (unlikely though)
        if (sbet_data[search_index][0] == gpstime):
            output = sbet_data[search_index]
            break
        # end if
        
        # If the next record is past the given time then the time we want is between this record and the next 
        # - return whichever is closer
        if (sbet_data[search_index+1][0] > gpstime):
            if (gpstime - sbet_data[search_index][0] < sbet_data[search_index+1][0] - gpstime):
                output = sbet_data[search_index]
            else:
                output = sbet_data[search_index+1]
                search_index = search_index + 1
            # end if
            break
        else:
            # If the next record is still less than the given time, increment the index
            search_index = search_index + 1
        # end if
    # end while
    
    # If we don't have anything in output then we didn't find a match
    if (output == []):
        raise KeyError, "No SBET records found matching GPS time " + str(gpstime)
    # end if
    
    if (not index_only):
        return output
    else:
        return search_index
    # end if
# end function

#######################################
# Function getBounds
# Gets the north, south east and west boundaries of an SBET file,
# optionally within specified GPS time constraints
#
# Arguments
# sbetfilename: Name of SBET file to read in
# starttime: GPS time of week to start at
# endtime: GPS time of week to end at
#
# Returns a dictionary containing keys "n", "s", "e", "w", "up" and "down" containing the boundary
# co-ordinates in each direction. Note that heights are against the ellipsoid and the base may not
# be at sea level anyway, so the "down" value is unlikely to be zero.
# 
# Note returns lat/lons in RADIANS, not degrees (because that's what's in the SBET file).
########################################
def getBounds(sbetfilename, starttime=None, endtime=None):
    
    # Read SBET file
    try:
        sbet_data = readSbet(sbetfilename)
    except:
        raise IOError, "Could not read sbet file " + sbetfilename + ". Reason: " + str(sys.exc_info()[1]), sys.exc_info()[2]
    # end try
    
    # Check that the start time is before the end time if both were given
    if (starttime != None) and (endtime != None):
        if endtime < starttime:
            raise ValueError, "Specified end time is before specified start time."
        # end if
    # end if
    
    # If a start time was specified work out what index in the data file matches it
    if (starttime != None):
        try:
            start_index = getPosition(starttime, sbet_data, True)
        except:
            raise IOError, "Could not get start position from SBET file. Reason: " + str(sys.exc_info()[1]), sys.exc_info()[2]
        # end try
    else:
        start_index = 0
    # end if
    
    # If an end time was given work out what index in the data file matches it
    if (endtime != None):
        try:
            end_index = getPosition(endtime, sbet_data, True)
        except:
            raise IOError, "Could not get end position from SBET file. Reason: " + str(sys.exc_info()[1]), sys.exc_info()[2]
        # end try
    else:
        end_index = len(sbet_data)
    # end if
    
    # Initialise output dictionary
    bounds = dict()
    bounds["n"] = None
    bounds["s"] = None
    bounds["e"] = None
    bounds["w"] = None
    bounds["up"] = None
    bounds["down"] = None
    
    # Go through SBET file between start and end times getting max values
    # in each direction.
    for i in range(start_index, end_index):
        if (bounds["n"] == None):
            bounds["n"] = sbet_data[i][1]
            bounds["s"] = sbet_data[i][1]
            bounds["e"] = sbet_data[i][2]
            bounds["w"] = sbet_data[i][2]
            bounds["up"] = sbet_data[i][3]
            bounds["down"] = sbet_data[i][3]
        # end if
        
        if (bounds["n"] < sbet_data[i][1]):
            bounds["n"] = sbet_data[i][1]
        # end if
        if (bounds["s"] > sbet_data[i][1]):
            bounds["s"] = sbet_data[i][1]
        # end if
        if (bounds["e"] < sbet_data[i][2]):
            bounds["e"] = sbet_data[i][2]
        # end if
        if (bounds["w"] > sbet_data[i][2]):
            bounds["w"] = sbet_data[i][2]
        # end if
        if (bounds["up"] < sbet_data[i][3]):
            bounds["up"] = sbet_data[i][3]
        # end if
        if (bounds["down"] > sbet_data[i][3]):
            bounds["down"] = sbet_data[i][3]
        # end if
    # end for
    
    return bounds
# end function
