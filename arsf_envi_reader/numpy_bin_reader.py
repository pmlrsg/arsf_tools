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

import collections
import numpy
from . import envi_header

class BilReader(collections.Iterator):
   """
   Class to read ENVI BIL file line at a time

   For each line returns a numpy array bands*samples

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
   def __init__(self, input_file):
      self.file_handler = open(input_file, "rb")

      header_file = envi_header.find_hdr_file(input_file)
      hdr_data_dict = envi_header.read_hdr_file(header_file)

      # Check we have a BIL file
      if hdr_data_dict["interleave"].lower() != "bil":
         raise Exception("The class 'BilReader' is only "
                         "valid for BIL format files")

      self.samples = int(hdr_data_dict["samples"])
      self.lines = int(hdr_data_dict["lines"])
      self.bands = int(hdr_data_dict["bands"])
      self.numpy_dtype = envi_header.ENVI_TO_NUMPY_DTYPE[hdr_data_dict["data type"]]
      self.byte_size = numpy.dtype(self.numpy_dtype).itemsize
      self.line_size = self.samples * self.bands * self.byte_size
      self.hdr_data_dict = hdr_data_dict

   def __next__(self):
      line = numpy.fromstring(self.file_handler.read(self.line_size),
                              dtype=self.numpy_dtype)
      if line.size < (self.bands * self.samples):
         raise StopIteration
      line = line.reshape(self.bands, self.samples)

      return line

   def next(self):
       return self.__next__()

   def get_hdr_dict(self):
      """
      Return a dictionary of parameters from header
      """
      return self.hdr_data_dict

   def __del__(self):
      self.file_handler.close()

class BsqReader(collections.Iterator):
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
   def __init__(self, input_file):
      self.file_handler = open(input_file, "rb")

      header_file = envi_header.find_hdr_file(input_file)
      hdr_data_dict = envi_header.read_hdr_file(header_file)

      # Check we have a BIL file
      if hdr_data_dict["interleave"].lower() != "bsq":
         raise Exception("The class 'BsqReader' is only "
                         "valid for BSQ format files")

      self.samples = int(hdr_data_dict["samples"])
      self.lines = int(hdr_data_dict["lines"])
      self.bands = int(hdr_data_dict["bands"])
      self.numpy_dtype = envi_header.ENVI_TO_NUMPY_DTYPE[hdr_data_dict["data type"]]
      self.byte_size = numpy.dtype(self.numpy_dtype).itemsize
      self.band_size = self.samples * self.lines * self.byte_size
      self.hdr_data_dict = hdr_data_dict

   def __next__(self):
      band = numpy.fromstring(self.file_handler.read(self.band_size),
                              dtype=self.numpy_dtype)
      if band.size < (self.samples * self.lines):
         raise StopIteration
      band = band.reshape(self.samples, self.lines)

      return band

   def next(self):
       return self.__next__()

   def get_hdr_dict(self):
      """
      Return a dictionary of parameters from header
      """
      return self.hdr_data_dict

   def __del__(self):
      self.file_handler.close()


