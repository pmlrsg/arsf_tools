ARSF Tools
===========

Various tools for using, processing or handling airborne remote sensing data acquired
by the National Environment Research Council ([NERC](http://www.nerc.ac.uk/))
Airborne Research & Survey Facility (ARSF). Developed by the ARSF Data Analysis
Node ([ARSF-DAN](https://arsf-dan.nerc.ac.uk/)) based at Plymouth Marine Laboratory.

Most tools are written in Python and depend on other libraries such as NumPy, see
individual scripts for more details on required libraries.

Unless otherwise stated tools are made available under the terms of the GNU General Public License
as detailed in [LICENSE](LICENSE).

LiDAR
------

**fwf_extract.py**

A tool to extract waveform data from LAS1.3 LiDAR files.
Requires: las1_3_handler.py

**las1_3_handler.py**

A library to read and extract data from a LAS1.3 file.

**las13**

A directory containing the las13 library for reading LAS1.3 files. Consists of a C++ library with python bindings.
See separate [README](las13/README) for more details.

**colour_las_file.py**

A script to attribute LAS files with colours from an image (e.g., hyperspectral data).
Requires GDAL python bindings and [laspy](https://github.com/grantbrown/laspy).

**ARSF DEM Scripts**

Scripts to create Digital Elevation Models (DEMs) from LiDAR data are housed in a separate repository: https://github.com/pmlrsg/arsf_dem_scripts

**LiDAR Analysis GUI**

Our inhouse LiDAR visualisation tool is available from https://github.com/arsf/lag

Hyperspectral
--------------

**assign_projection.py**

A script to assign missing projection information to a GDAL dataset. Requires GDAL Python bindings.

**get_info_from_header.py**

A script to print information from a header file and optionally save wavelengths to a CSV file.

**copy_header_info.py**

Copy selected keys from one header to another.

**batch_run_apl.py**

A script to batch map level 1b files to level 3b using APL.

**Airborne Processing Library (APL)**

Library for processing hyperspectral data. Available from https://github.com/arsf/apl

Other
------

**read_sol_file.py**

A script / library to read SOL navigation files and write records to an ASCII text file.

**ARSF on JASMIN**

Scripts for running ARSF on the [JASMIN](http://jasmin.ac.uk/) system are available from https://github.com/arsf/arsf_on_jasmin
