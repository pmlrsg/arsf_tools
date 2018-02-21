#!/usr/bin/env python
"""
Empirical Line Calibration

Takes field and image spectra from white, grey and black target in a CSV file
with the following headings:

wavelength,white,grey,black

From these performs a linar fit for each wavelength in the image (interpolating
field spectra to match).

Coefficients from linear fit are then applied to the image.

Author: Dan Clewley
Creation Date: 2018-02-20

"""

from __future__ import print_function
import argparse
import time
import numpy

from arsf_envi_reader import numpy_bin_reader
from arsf_envi_reader import envi_header

DEFAULT_SCALE_FACTOR = 10000

def get_elc_coefficients(image_spectra_file, field_spectra_file):
    """
    Takes images spectra and field spectra from white, grey and black
    targets and performs a linear fit for each band.

    Returns numpy array containing two columns with ax and bx

    """


    image_spectra = numpy.genfromtxt(image_spectra_file,
                                     delimiter=",", names=True)
    field_spectra = numpy.genfromtxt(field_spectra_file,
                                     delimiter=",", names=True)

    elc_coefficients = []

    for i, wavelength in enumerate(image_spectra["wavelength"]):
        # Get radiance from image spectra for given wavelength
        image_white = image_spectra["white"][i]
        image_grey = image_spectra["grey"][i]
        image_black = image_spectra["black"][i]

        # Get coresponding values from field spectra
        # As wavelengths are likely to not exactly match up
        # use interpolation to get value for image wavelength
        field_white = numpy.interp(wavelength, field_spectra["wavelength"],
                                   field_spectra["white"])
        field_grey = numpy.interp(wavelength, field_spectra["wavelength"],
                                  field_spectra["grey"])
        field_black = numpy.interp(wavelength, field_spectra["wavelength"],
                                   field_spectra["black"])

        # Perform linear fit
        ax, bx = numpy.polyfit([image_black, image_grey, image_white],
                               [field_black, field_grey, field_white],
                               1)
        elc_coefficients.append([ax, bx])

    elc_coefficients = numpy.array(elc_coefficients)

    return elc_coefficients

def apply_elc(input_image, output_image, image_spectra_file,
              field_spectra_file,
              scale_factor=DEFAULT_SCALE_FACTOR):
    """
    Derive coefficients for an emprical line calibration and apply
    to a BIL file.
    """

    print("Getting coefficients")
    elc_coefficients = get_elc_coefficients(image_spectra_file,
                                            field_spectra_file)

    print("Applying to image")
    # Read ENVI header
    input_header_file = envi_header.find_hdr_file(input_image)
    input_header_dict = envi_header.read_hdr_file(input_header_file)

    # Open input file
    in_data = numpy_bin_reader.BilReader(input_image)

    # Open file for output
    out_file = open(output_image, "wb")

    for i, line in enumerate(in_data):
        print(" Line {0:05}/{1:05}".format(i, in_data.lines), end="\r")

        # Apply coefficients
        elc_line = elc_coefficients[:,0] * line.transpose() \
                     + elc_coefficients[:,1]
        elc_line = elc_line.transpose()

        # Set any negative values to 0
        elc_line = numpy.where(elc_line < 0, 0, elc_line)

        elc_line = elc_line * scale_factor
        # For default scale factor is over 1000 express as integer
        if scale_factor >= 1000:
            elc_line = elc_line.astype(numpy.uint16)
        else:
            elc_line = elc_line.astype(numpy.float32)
        elc_line.tofile(out_file)

    print(" Line {0:05}/{0:05}".format(in_data.lines), end="\n")

    output_header_dict = input_header_dict

    # See if need to change data type
    if scale_factor >= 1000:
        output_header_dict["data type"] = 12
    else:
        output_header_dict["data type"] = 4

    # Remove radiance data units
    try:
        output_header_dict.pop("radiance data units")
    except KeyError:
        pass
    # Add scale factor
    output_header_dict["reflectance scale factor"] = scale_factor

    procesing_comment = """\nConverted to reflectance using empirical line method. Field spectra: {}, Image spectra: {}\n""".format(field_spectra_file, image_spectra_file)
    try:
        output_header_dict["_comments"] = output_header_dict["_comments"] + \
                                                procesing_comment
    except KeyError:
        output_header_dict["_comments"] = procesing_comment

    output_header_dict["description"] = "BIL file created by {} on {}".format(__file__,
                                            time.strftime("%Y-%m-%d %H:%M:%S"))

    # Copy header
    envi_header.write_envi_header(output_image + ".hdr",
                                  output_header_dict)

    # Close files
    out_file.close()
    in_data = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Use an empirical line calibration to "
                                     "convert image spectra to surface "
                                     "reflectance")
    parser.add_argument("inputimage", nargs=1,
                        type=str, help="Input image")
    parser.add_argument("outputimage", nargs=1,
                        type=str, help="Output image")
    parser.add_argument("--image_spectra",
                        required=True,
                        type=str, help="CSV file with target spectra from images")
    parser.add_argument("--field_spectra",
                        required=True,
                        type=str, help="CSV file with target spectra from field")
    parser.add_argument("--scale", type=float,
                        required=False,
                        default=DEFAULT_SCALE_FACTOR,
                        help="Scale factor to apply to reflectance values. "
                             "Used so image can be saved as uint16. "
                             "(Default {}".format(DEFAULT_SCALE_FACTOR))

    args = parser.parse_args()

    apply_elc(args.inputimage[0], args.outputimage[0],
              args.image_spectra, args.field_spectra)
    print("Saved to {}".format(args.outputimage[0]))
