"""
Transform data from the QDS csv codebook format to the
occams codebook format
"""

import sys
import six

import unicodecsv as csv


def convert_choices(choices):
    """
    Convert choices to occams choices string

    :param choices: list of choices, ie. [[u'0', 'label1'], [u'1', 'label2']]
    :return: choices string, i.e. '0=label1;1=label2'
    """
    choice_string = u';'.join(['{}={}'for choice in choices])
    choice_list = []

    for choice in choices:
        choice_list.append(choice[0])
        choice_list.append(choice[1])

    return choice_string.format(*choice_list)


def convert(schema_name, schema_title, publish_date, codebook, delimiter=','):
    """
    Convert QDS file to occams format

    :param schema_name:
    :param schema_title:
    :param publish_date:
    :param codebook:
    :param delimiter:
    :return:
    """
    pass
