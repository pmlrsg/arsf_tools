ARSF Tools
==========

Various tools for using, processing or handling ARSF data provided by the Data Analysis Node at Plymouth Marine Laboratory.


fwf_extract.py: 
   A tool to extract waveform data from LAS1.3 LiDAR files.
   Requires: las1_3_handler.py

las1_3_handler.py:
   A library to read and extract data from a LAS1.3 file.

read_sol_file.py:
   A script / library to read SOL navigation files and write records to an ASCII text file.

las13:
   A directory containing the las13 library for reading LAS1.3 files. Consists of a C++ library with python bindings.

assign_projection.py:
   A script to assign missing projection information to a GDAL dataset. Requires GDAL Python bindings.
