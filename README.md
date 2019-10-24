NERC-ARF Tools
================

Various tools for using, processing or handling airborne remote sensing data acquired
by the National Environment Research Council ([NERC](http://www.nerc.ac.uk/))
Airborne Research Facility ([NERC-ARF](https://bas.ac.uk/nerc-arf ); formerly ARSF).

Developed by the NERC-ARF Data Analysis Node ([NERC-ARF-DAN](http://nerc-arf-dan.pml.ac.uk/)) based at Plymouth Marine Laboratory.

Most tools are written in Python and depend on other libraries such as NumPy, see
individual scripts for more details on required libraries.

Unless otherwise stated tools are made available under the terms of the GNU General Public License
as detailed in [LICENSE](LICENSE).

General Set up
----------------

The majority of these scripts are written in Python and require external libraries
such as [numpy](http://www.numpy.org/) and [GDAL](http://www.gdal.org/).

To install these under Windows it is recommended to use the following steps:

1. Download minconda from http://conda.pydata.org/miniconda.html#miniconda and follow the instructions to install.

2. Open a 'Command Prompt' window and install gdal and numpy by typing:
```
conda install -c conda-forge numpy gdal
```

Alternatively they can be installed through [OSGeo4W](https://trac.osgeo.org/osgeo4w/).
This is recommended if you also plan to install the [arsf_dem_scripts](https://github.com/pmlrsg/arsf_dem_scripts).

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

**convert_pre2009_lidar.py**

A script to convert ASCII LiDAR files used for ARSF data prior to 2009
(.all format) with two returns for each line into into ASCII format with a return
on each line or LAS.

For a description of the .all format used see:

https://nerc-arf-dan.pml.ac.uk/trac/wiki/Processing/LIDARDEMs

For conversion to LAS Requires LAStools > 160730 to use the '-utm ZZnorth'
flag.

Usage:
```
convert_pre2009_lidar.py -i lidar.all -o lidar_las.las
```

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

**plot_info_from_headers.py**

A script to plot information from multiple header files and optionally save parameters to a CSV file.
Requires matplotlib and numpy to be installed. If you are using conda (see above) these can be installed using:
```
conda install numpy matplotlib
```

**copy_header_info.py**

Copy selected keys from one header to another.

**batch_run_apl.py**

A script to batch map level 1b files to level 3b using APL.

**apply_elc_to_bil**

A script to apply an empirical line correction to a BIL file. Takes field and image spectra from white, grey and black target in a CSV file
with the following headings:

```
wavelength,white,grey,black
```

From these performs a linar fit for each wavelength in the image (interpolating
field spectra to match). Coefficients from linear fit are then applied to the image.

Usage:
```
apply_elc_to_bil.py --image_spectra spectra/f168051b_target_spectra.csv \
                    --field_spectra spectra/20170617-field_spec_targets.csv \
                    flightlines/level1b/f168051b.bil \
                    outputs/f168051b_elc.bil
```

**Airborne Processing Library (APL)**

Library for processing hyperspectral data. Available from https://github.com/arsf/apl

Thermal
--------

**owl_temp_emissivity.py**

A script to calculate temperature and emissivity from Owl data.
Available from: https://github.com/pmlrsg/owl_temp_emissivity

Camera
-------

**extract_wild_rc10_gps.py**

Extract GPS coordinates from ARSF Wild RC-10 TIFF images available from
[NEODC](http://neodc.nerc.ac.uk/) using exiftool and save to CSV.

Requires exiftool to be installed from http://www.sno.phy.queensu.ca/~phil/exiftool/

Usage:
```
extract_wild_rc10_gps.py -o photo_locations.csv *.tif
```

Other
------

**read_nav_file.py**

A script / library to read SOL/SBET format navigation files.

**python convert_wgs84_to_geoid.py**

Converts from heights relative to the WGS-84 ellipsoid to relative to EGM96 Geoid.

Conversion is based on 15 minute gridded conversion file available from: https://earth-info.nga.mil/GandG/wgs84/gravitymod/egm96/binary/binarygeoid.html

The tool can be used from the command line:
```
python convert_wgs84_to_geoid.py --lat 54 --lon -4 --height 0
```
Or imported and used as a Python function

```python
import convert_wgs84_to_geoid

convert_wgs84_to_geoid.convert_wgs_84_to_geoid(in_lat=54, in_lon=-4, in_elevation=0,
                                               wgs84_to_geoid=True)
```
Setting `wgs84_to_geoid` to `False` will do the conversion the other way (EGM96 to WGS84).

**ARSF on JASMIN**

Scripts for running ARSF on the [JASMIN](http://jasmin.ac.uk/) system are available from https://github.com/arsf/arsf_on_jasmin
