#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to for reading ENVI Binary data

Author: Dan Clewley
Creation Date: 15/04/2016

Suggestion for using collections.Itterator from:

http://stackoverflow.com/questions/4019971/how-to-implement-iter-self-for-a-container-object-python

"""

###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

import abc
import collections
import numpy
from . import envi_header

# Try to import c++ arsf binaryreader (faster)
HAVE_ARSF_BINARYREADER = False
try:
    import binfile
    HAVE_ARSF_BINARYREADER = True
except ImportError:
    pass

class _BinaryReader(collections.Iterator):
    """
    Abstract class for reading binary files with different interleaves.
    """
    def __init__(self, input_file):

        self.binreader_file = None
        self.file_handler = None

        header_file = envi_header.find_hdr_file(input_file)
        hdr_data_dict = envi_header.read_hdr_file(header_file)

        self.samples = int(hdr_data_dict["samples"])
        self.lines = int(hdr_data_dict["lines"])
        self.bands = int(hdr_data_dict["bands"])
        self.numpy_dtype = \
                     envi_header.ENVI_TO_NUMPY_DTYPE[hdr_data_dict["data type"]]
        self.byte_size = numpy.dtype(self.numpy_dtype).itemsize
        self.line_size = self.samples * self.bands * self.byte_size
        self.band_size = self.samples * self.lines * self.byte_size
        self.hdr_data_dict = hdr_data_dict
        self.current_line = -1
        self.current_band = -1
        self.interleave_checked = False

        if HAVE_ARSF_BINARYREADER:
            self.binreader_file = binfile.BinFile(input_file)
        else:
            self.file_handler = open(input_file, "rb")

    @abc.abstractmethod
    def __next__(self): pass

    @abc.abstractmethod
    def read_line(self, line_number):
        raise NotImplementedError

    @abc.abstractmethod
    def read_band(self, band_number):
        raise NotImplementedError

    def next(self):
        return self.__next__()

    def get_hdr_dict(self):
        """
        Return a dictionary of parameters from header
        """
        return self.hdr_data_dict

    def have_arsf_binaryreader(self):
        """
        Check if arsf_binaryreader is available
        """
        return HAVE_ARSF_BINARYREADER

    def check_interleave(self, interleave):
        """
        Check if the interleave of the file is that expected
        by the reader.

        Only performs check if interleave_checked is False if not assume already
        checked and return True.

        Stops doing string comparison for each line.
        """
        if not self.interleave_checked:
            if self.hdr_data_dict["interleave"].lower() == interleave:
                self.interleave_checked = True
            else:
                self.interleave_checked = False

        return self.interleave_checked

    def __del__(self):
        if self.file_handler is not None:
            self.file_handler.close()



class BilReader(_BinaryReader):
    """
    Class to read ENVI BIL file line at a time

    For each line returns a numpy array bands*samples

    If arsf_binaryreader (https://github.com/arsf/arsf_binaryreader) is available
    will use this. If not will use NumPy

    Example::

       from arsf_envi_reader import numpy_bin_reader
       from arsf_envi_reader import envi_header

       # Open file for output
       out_file = open("out_file.bil","wb")

       # Open input file
       in_data = numpy_bin_reader.BilReader('FENIX219b-14-1.raw')

       for line in in_data:
          out_line = line + 1
          out_line.tofile(out_file)

       # Copy header
       envi_header.write_envi_header("out_file.bil.hdr",
                                     in_data.get_hdr_dict())

       # Close files
       out_file.close()
       in_data = None

    """

    def __next__(self):
        # Check we have a BIL file
        if not self.check_interleave("bil"):
            raise Exception("The class 'BilReader' is only "
                            "valid for BIL format files")

        self.current_line +=1

        # Check if the line is within image
        if self.current_line >= self.lines:
            raise StopIteration

        # If arsf_binaryreader is available read line using this
        if HAVE_ARSF_BINARYREADER:
            line = self.binreader_file.Readline(self.current_line)
        # If arsf_binaryreader is not available read using NumPy
        else:
            line = numpy.fromstring(self.file_handler.read(self.line_size),
                                    dtype=self.numpy_dtype)
            if line.size < (self.bands * self.samples):
                raise StopIteration

        line = line.reshape(self.bands, self.samples)

        return line

    def read_line(self, line_number):
        """
        Read data for a user specified line

        Currently only supported if ARSF binary ready (binfile) library
        is available.
        """
        if HAVE_ARSF_BINARYREADER:
            line = self.binreader_file.Readline(line_number)
            return line
        else:
            raise NotImplementedError("Need 'binfile' library to specify line")

    def read_band(self, band_number):
        """
        Read data for a user specified band

        Currently only supported if ARSF binary ready (binfile) library
        is available.
        """
        if HAVE_ARSF_BINARYREADER:
            band = self.binreader_file.Readband(band_number)
            return band[1]
        else:
            raise NotImplementedError("Need 'binfile' library to specify band")


class BsqReader(_BinaryReader):
    """
    Class to read ENVI BSQ file band at a time

    For each line returns a numpy array samples*lines

    Example::

       from arsf_envi_reader import numpy_bin_reader
       from arsf_envi_reader import envi_header

       # Open file for output
       out_file = open("out_file.bsq","wb")

       # Open input file
       in_data = numpy_bin_reader.BsqReader('FENIX219b-14-1.raw')

       for band in in_data:
          out_band = band + 1
          out_band.tofile(out_file)

       # Copy header
       envi_header.write_envi_header("out_file.bsq.hdr",
                                     in_data.get_hdr_dict())

       # Close files
       out_file.close()
       in_data = None

    """

    def __next__(self):
        # Check we have a BSQ file
        if not self.check_interleave("bsq"):
            raise Exception("The class 'BsqReader' is only "
                            "valid for BSQ format files")

        self.current_band +=1

        # Check if the line is within image
        if self.current_band >= self.bands:
            raise StopIteration

        # If arsf_binaryreader is available read line using this
        if HAVE_ARSF_BINARYREADER:
            line = self.binreader_file.Readband(self.current_band)[1]
        # If arsf_binaryreader is not available read using NumPy
        else:
            line = numpy.fromstring(self.file_handler.read(self.band_size),
                                    dtype=self.numpy_dtype)
            if line.size < (self.samples * self.lines):
                raise StopIteration

        line = line.reshape(self.samples, self.lines)

        return line

    def read_line(self, line_number):
        """
        Read data for a user specified line

        Currently only supported if ARSF binary ready (binfile) library
        is available.
        """
        if HAVE_ARSF_BINARYREADER:
            line = self.binreader_file.Readline(line_number)
            return line
        else:
            raise NotImplementedError("Need 'binfile' library to specify line")

    def read_band(self, band_number):
        """
        Read data for a user specified band

        Currently only supported if ARSF binary ready (binfile) library
        is available.
        """
        if HAVE_ARSF_BINARYREADER:
            band = self.binreader_file.Readband(band_number)
            return band[1]
        else:
            raise NotImplementedError("Need 'binfile' library to specify band")
