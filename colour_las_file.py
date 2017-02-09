#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Description: Attribute LAS file with RGB colour information
"""
Attribute points in a LAS file with RGB colour information. Point clouds can be
visualised in viewers which support colouring points by RGB values such as
http://plas.io/

Requires hyperspectral data to be mapped to the same projection as LAS files.

Latest version available from: https://github.com/pmlrsg/arsf_tools

Requires:

* laspy (https://github.com/grantbrown/laspy) - to read LAS files
* GDAL (http://www.gdal.org) - to read hyperspectral files

Known Issues:

Can use a lot of memory as loads three bands of an image to memory
and arrays for x,y,r,g,b from LAS file.

Author: Dan Clewley
Creation Date: 07/12/2015

"""
###########################################################
# This file has been created by ARSF Data Analysis Node and
# is licensed under the GPL v3 Licence. A copy of this
# licence is available to download with this file.
###########################################################

from __future__ import print_function
import argparse
import copy
import sys
import laspy
import numpy
from osgeo import gdal

from arsf_envi_reader import envi_header

#: Debug mode - prints out more information useful for debugging.
DEBUG = False

DEFAULT_WAVELENGTHS = [640, 540, 470]

def get_bands_from_wavelengths(input_image, wavelengths=DEFAULT_WAVELENGTHS):
    """
    Get bands for a list of wavelengths (useful for creating three band
    composites).

    Function adapted from one in createimage.py
    """
    input_header = envi_header.find_hdr_file(input_image)

    if input_header is None:
        raise Exception("Need to use ENVI header to get bands")

    header_dict = envi_header.read_hdr_file(input_header)
    image_wavelengths = header_dict['wavelength'].split(',')

    out_bands = []
    for wavelength in wavelengths:
        band = min(range(len(image_wavelengths)),
                   key=lambda x:abs(float(image_wavelengths[x])-wavelength))
        out_bands.append(band)

    return out_bands


class ExtractPixels(object):
    """
    Class to extract RGB values for a given pixel
    """
    def __init__(self, input_image, red_band_num=None,
                 green_band_num=None, blue_band_num=None):
        self.input_ds = gdal.Open(input_image, gdal.GA_ReadOnly)

        if self.input_ds is None:
            raise Exception("Could not open image {}".format(input_image))

        geotransform = self.input_ds.GetGeoTransform()

        self.image_tl_x = geotransform[0]
        self.pixel_x_size = geotransform[1]
        self.image_tl_y = geotransform[3]
        self.pixel_y_size = geotransform[5]

        imagebands = self.input_ds.RasterCount

        # Check if image bands have been provided.
        if red_band_num is None and green_band_num is None \
           and blue_band_num is None:
            # For a three band image assume 1,2,3
            if imagebands == 3:
                red_band_num = 1
                green_band_num = 2
                blue_band_num = 3
            # For more than three bands try to get from wavelengths
            else:
                try:
                    bands = get_bands_from_wavelengths(input_image)
                    red_band_num = bands[0]
                    green_band_num = bands[1]
                    blue_band_num = bands[2]
                except Exception as err:
                    raise Exception("Image has more than three bands and no "
                                    "bands specified. Could not read from "
                                    "header - please specify"
                                    "\nError message {}".format(err))

        if red_band_num > imagebands or \
           green_band_num > imagebands or \
           blue_band_num > imagebands:
            raise Exception("Specified band is greater than number of bands in "
                            "image ({})".format(imagebands))


        self.red_band = self.input_ds.GetRasterBand(red_band_num).ReadAsArray()
        self.green_band = self.input_ds.GetRasterBand(green_band_num).ReadAsArray()
        self.blue_band = self.input_ds.GetRasterBand(blue_band_num).ReadAsArray()

    def __del__(self):
        self.input_ds = None

    def apply_standard_deviation_stretch(self, in_array):
        """
        Apply a 2 standard deviation stretch to scale pixel values from
        0 - 255
        """
        mean = in_array.mean()
        stdev = in_array.std()

        sd_min = mean - 2*stdev
        sd_max = mean + 2*stdev
        sd_range = sd_max - sd_min

        out_array = (in_array / sd_range) * 255

        out_array[out_array < 0] = 0
        out_array[out_array > 255] = 255

        return out_array

    def scale_bands(self):
        """
        Scale image bands (required if not between 0 - 255)
        """

        self.red_band = self.apply_standard_deviation_stretch(self.red_band)
        self.green_band = self.apply_standard_deviation_stretch(self.green_band)
        self.blue_band = self.apply_standard_deviation_stretch(self.blue_band)

    def get_pixelvals(self, in_x, in_y):
        """
        Get pixel values for a given x and y in geographic coordinates.

        Uses the centre coordinate of each pixel.

        """

        pixel_x = ((in_x - self.image_tl_x) / self.pixel_x_size) \
                  + (self.pixel_x_size / 2.0)
        pixel_y = ((in_y - self.image_tl_y) / self.pixel_y_size) \
                  + (self.pixel_y_size / 2.0)

        if pixel_x < 0 or pixel_y < 0:
            pixel_vals = None
            if DEBUG:
                print("Position {} N, {} E is outside image.".format(in_y, in_x))
        else:
            try:
                red_val = self.red_band[int(pixel_y), int(pixel_x)]
                green_val = self.green_band[int(pixel_y), int(pixel_x)]
                blue_val = self.blue_band[int(pixel_y), int(pixel_x)]

                pixel_vals = [red_val, green_val, blue_val]
            except IndexError:
                pixel_vals = None
                if DEBUG:
                    print("Position {} N, {} E is outside image.".format(in_y,
                                                                         in_x))
        return pixel_vals

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Attribute a LAS file with
 colour information from a raster for visualisation in programs such as:
 http://plas.io/. Bands can be specified via the command line and pixel values
 stretched for display.
 Created by ARSF-DAN at Plymouth Marine Laboratory.""")
    parser.add_argument("inputlas", nargs=1,type=str, help="Input LAS file")
    parser.add_argument("outputlas", nargs=1,type=str, help="Output LAS file")
    parser.add_argument("--image", required=True,
                        help="Image to extract values from.")
    parser.add_argument("--red", required=False,
                        type=int,
                        default=None,
                        help="Band in image to use for red channel")
    parser.add_argument("--green", required=False,
                        type=int,
                        default=None,
                        help="Band in image to use for green channel")
    parser.add_argument("--blue", required=False,
                        type=int,
                        default=None,
                        help="Band in image to use for blue channel")
    parser.add_argument("--scale", required=False,
                        action="store_true",
                        default=False,
                        help="Scale pixel values (if not already 0 - 255)")
    args=parser.parse_args()

    print("Reading in data from {}".format(args.inputlas[0]))
    input_file = laspy.file.File(args.inputlas[0], mode = "r")

    # Increase point source ID to handle RGB fields
    new_header = copy.copy(input_file.header)
    new_header.data_format_id = 2

    output_file = laspy.file.File(args.outputlas[0], mode = "w",
                                  header=new_header,
                                  vlrs = input_file.header.vlrs)

    # Copy across points
    output_file.points = input_file.points

    # Get scaled x and y values
    point_x = input_file.get_x_scaled()
    point_y = input_file.get_y_scaled()
    out_red = output_file.get_red()
    out_green = output_file.get_green()
    out_blue = output_file.get_blue()
    # Set up pixel extraction class

    pixelval = ExtractPixels(args.image,
                             red_band_num=args.red,
                             green_band_num=args.green,
                             blue_band_num=args.blue)

    # Scale pixel values between 0 - 255 if needed.
    if args.scale:
        pixelval.scale_bands()

    print("Getting RGB values:")
    status = 0
    status_percent = 0
    status_inc = point_x.shape[0] / 10

    colour_pixels = 0

    for i in range(point_x.shape[0]):
        pixel_vals = pixelval.get_pixelvals(point_x[i], point_y[i])

        if pixel_vals is not None:
            out_red[i] = pixel_vals[0]
            out_green[i] = pixel_vals[1]
            out_blue[i] = pixel_vals[2]
            colour_pixels += 1

        if i >= status and status_percent < 100:
            print("{}...".format(status_percent), end="")
            sys.stdout.flush()
            status_percent += 10
            status += status_inc

    print("100 %")

    print("Set colour for {}/{} points".format(colour_pixels, point_x.shape[0]))

    pixelval = None

    output_file.set_red(out_red)
    output_file.set_green(out_green)
    output_file.set_blue(out_blue)

    print("Writing out data to {}".format(args.outputlas[0]))
    input_file.close()
    output_file.close()
