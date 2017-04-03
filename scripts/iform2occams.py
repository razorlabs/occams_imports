#!/usr/bin/env python

"""
This script consolidates iForm data dictionaries into single version eCRFs

NOTE: This is a python 2 script and depents on occams_imports

Sample usage:

python iform2occams.py --src ~/Documents/files/ --dst ~/Documents/output.csv
"""

import os
import fnmatch
import sys

import click

from occams_imports.parsers.iform_json import convert as convert_iform


def glob_json(path):
    """
    Recursively iterate through all JSON files in a directory
    """
    for __, __, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.json'):
            yield filename


@click.command()
@click.option(
    '--src',
    type=click.Path(exists=True),
    help='Input iForm data dictionary directory or file'
)
@click.option(
    '--dst',
    type=click.File('wb'),
    default=sys.stdout,
    help='(Optional) Output codebook file name, otherwise prints to STDOUT'
)
def main(src, dst):
    """
    Converter script of iForm data dictionaries to OCCAMS code books
    """

    if os.path.isdir(src):
        filenames = glob_json(src)

    elif os.path.isfile(src):
        src, basename = os.path.split(src)
        filenames = [basename]

    else:
        raise Exception('Unkown source file type: %s' % src)

    header = None

    for filename in filenames:

        with open(os.path.join(src, filename), 'rb') as in_buffer:
            parsed_buffer = convert_iform(in_buffer)

            firstline = parsed_buffer.readline()

            # Only write the header for the first file processed
            if not header:
                header = firstline
                dst.write(firstline)

            for line in parsed_buffer:
                dst.write(line)

            parsed_buffer.close()

    dst.close()


if __name__ == '__main__':
    main()
