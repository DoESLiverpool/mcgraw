#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import code # for debugging
import os
import re
import vpype
import vpype_cli
from vpype_gcode import gwrite


DEFAULT_DIMENSIONS="297mm 420mm"
DEFAULT_SPLIT_LAYERS=False
PAPER_SIZES={
    "a3-portrait": "297mm 420mm",
    "a3-landscape": "420mm 297mm",
    "a4-portrait": "210mm 297mm",
    "a4-landscape": "297mm 210mm",
    "a5-portrait": "148mm 210mm",
    "a5-landscape": "210mm 148mm",
}


def main(file_handles=[], dimensions=DEFAULT_DIMENSIONS, split_layers=DEFAULT_SPLIT_LAYERS, vpype_config='mcgraw-config.toml'):
    if vpype_config:
        vpype.config_manager.load_config_file(vpype_config)
    
    # (output_width, output_height) = parse_dimensions(dimensions)

    for file_handle in file_handles:
        doc = vpype.read_multilayer_svg(file_handle, quantization=0.1)
        # doc = vpype.read_svg(file_handle, quantization=0.1)

        # doc_width = (doc.page_size[0], 'px')
        # doc_height = (doc.page_size[1], 'px')

        # code.interact(local=dict(globals(), **locals()))

        for id, layer in doc.layers.items():
            tmp = layer.merge(tolerance=0.1)
            # tmp = vpype_cli.linesort(tmp)
            doc.layers[id] = tmp

        # if(split_layers):

        # doc = doc.scale(x, y)
        # doc = vpype_cli.scaleto(doc, (output_width, output_height))

        # gwrite.gwrite raises a KeyError because doc.layers does not have a 0th item.
        # I tried repacking the doc.layers dict, to make sure its keys start from 0:
        #   doc._layers = {i: doc.layers[k] for i, k in enumerate(doc.layers)}
        # But then gwrite.gwrite just gives `KeyError: 1` instead!!

        # I tried reading the SVG without layers:
        #   doc = vpype.read_svg(file_handle, quantization=0.1)
        # But then click/parser.py complains `TypeError: unhashable type: 'list'`

        output_filename = "{}.gcode".format(os.path.splitext(file_handle.name)[0])
        with open(output_filename, 'w') as output_file:
            gwrite.gwrite(doc, output_file, 'mcgraw')


def parse_dimensions(dimensions):
    d = dimensions.lower().strip()

    # default to portrait if orientation is unspecified
    if d in [ "a3", "a4", "a5" ]:
        d = "{}-portrait".format(d)

    # convert paper size shorthand to width/height dimensions
    if d in PAPER_SIZES:
        d = PAPER_SIZES[d]

    match = re.search(r'([0-9.]+)([a-z]+),?\s+([0-9.]+)([a-z]+)', d, re.I)
    if match:
        width_value = match.group(1)
        width_units = match.group(2)
        height_value = match.group(3)
        height_units = match.group(4)
    else:
        raise ValueError("parse_dimensions must be passed a page size string, or a string containing two physical dimensions separated by a space")

    return (width_value, width_units), (height_value, height_units)


def clean_dimensions(dimensions):
    d = dimensions.lower().strip()

    # default to portrait if orientation is unspecified
    if d in [ "a3", "a4", "a5" ]:
        d = "{}-portrait".format(d)

    # convert paper size shorthand to width/height dimensions
    if d in PAPER_SIZES:
        d = PAPER_SIZES[d]

    return dimensions


def convert_length(val, unit_in, unit_out):
    ratios = { 'mm': 0.001, 'cm': 0.01, 'in': 0.0254, 'm': 1.0 }

    for unit in [unit_in, unit_out]:
        if unit not in ratios:
            raise ValueError(
                "{} is not a supported length unit (supported units: {})".format(
                    unit,
                    ratios.keys().join(',')
                )
            )

    return val * ratios[unit_in] / ratios[unit_out]


description = """
Converts the given SVG files into G-Code files, suitable for
plotting on McGraw the DoES Liverpool pen plotter.

The input files must be in SVG format.
"""

examples = """how to specify dimensions:
  WIDTH HEIGHT      eg: "21cm 29.7cm" or "210mm 297mm" (A4 paper size)
  PAPERSIZE         one of: "a3" (portrait), "a3-portrait", "a3-landscape",
                    "a4" (portrait), "a4-portrait", "a4-landscape",
                    "a5" (portrait), "a5-portrait", "a5-landscape"

examples:
  %(prog)s input.svg
  %(prog)s --dimensions "a4-landscape" input.svg
  %(prog)s --dimensions "10cm 10cm" --split-layers input.svg
  %(prog)s *.svg
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=description,
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "file_handles",
        metavar="FILE",
        type=argparse.FileType('r'),
        nargs="+",
        help="an SVG file to be converted (you can pass multiple files at once)"
    )
    parser.add_argument(
        "-d",
        "--dimensions",
        default=DEFAULT_DIMENSIONS,
        help="intended physical width and height of your artwork, see below for examples (default: %(default)s)"
    )
    parser.add_argument(
        "-s",
        "--split-layers",
        action="store_true",
        default=DEFAULT_SPLIT_LAYERS,
        help="output a separate G-Code file for each layer in the SVG (default: do not split)"
    )

    args = parser.parse_args()

    main(file_handles=args.file_handles, dimensions=args.dimensions, split_layers=args.split_layers)
