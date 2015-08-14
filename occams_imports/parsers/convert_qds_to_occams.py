"""
Transform data from the QDS csv codebook format to the
occams codebook format
"""

import sys
import six

import unicodecsv as csv

from convert_iform_to_occams import output_headers


def convert(codebook, delimiter=','):
    """
    Convert QDS file to occams format

    :param codebook:
    :param delimiter:
    :return:
    """
    reader = csv.reader(codebook, encoding='utf-8', delimiter=delimiter)

    # Remove headers from file
    headers = reader.next()

    output_csv = six.StringIO()
    writer = csv.writer(output_csv, encoding='utf-8')

    output_headers(writer)
    from pdb import set_trace; set_trace()
    codebook.close()

    output_csv.flush()
    output_csv.seek(0)
    output_csv.close()