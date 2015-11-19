"""
Parse an occams codebook

This data is the structure of the schemas and attributes for forms not the
collected data
"""

import re
from datetime import datetime

import six
import unicodecsv as csv

from occams_imports.parsers import iform_json
from occams_imports.parsers import convert_qds_to_occams


def is_true(value):
    """
    Determine if string is a true value

    :return:  True if string is true
    """
    if isinstance(value, six.string_types):
        value = value.lower()[0]

    return value in ['y', 't', 1]


def remove_system_entries(records):
    """
    Construct a new list of records where is_system is false

    :param records:  a list of dictionaries denoting each row of a codebook

    :return:  Filtered list of non-system rows
    """
    return [record for record in records if record['is_system'] is False]


def parse_choice_string(row):
    """
    Parse choice string, e.g.:

    '0=MyLabel;1=KeySeparatedByEquals;3=DelimitedBySemiColon'

    :param row: A csv DictReader row from codebook
    :return: list of choices in the form[[code, label], [code, label]]
    """
    choices = []
    raw_choices = re.split(r';(?=\s*-*\d+\s*\=)', row['choices'])
    for raw_choice in raw_choices:
        code, label = raw_choice.split('=', 1)
        code = code.strip()
        label = label.strip()
        choices.append([code, label])

    return choices


def get_choices(raw_choices):
    from occams_datastore import models as datastore
    """
    sample input = [[u'0', label], [u'1': label2]]

    sample output = {
        u'0': models.Choice(
            name=u'1',
            title=u'label',
            order=0
            )
        u'1': models.Choice(
            name=u'1',
            title=u'label2',
            order=1
            )
    }

    :param raw_choices: a dict of choices...key is option, value is label

    :return: a dictionary of choice datastore objects
    """
    choices = {}
    if raw_choices:

        for i, item in enumerate(raw_choices):
            code = item[0]
            label = item[1]
            choices[code] = datastore.Choice(
                name=code.strip(),
                title=label.strip(),
                order=i
            )

    return choices


def parse_dispatch(codebook, codebook_format, delimiter):
    """
    Dispatch to specific parser

    :codebook: codebook file
    :codebook_format: denotes type of codebook, i.e. 'occams'
    :delimiter: delimiter used in the codebook file

    :return: list of dictionaries...a dictionary denotes a row from the csv
    """
    if delimiter == u'comma':
        delimiter = ','
    elif delimiter == u'tab':
        delimiter = '\t'

    if codebook_format == u'iform':
        codebook = iform_json.convert(codebook)

    elif codebook_format == u'qds':
        codebook = convert_qds_to_occams.convert(
            codebook, delimiter=delimiter)

    return parse(codebook, delimiter=delimiter)


def parse(codebook, delimiter=','):
    """
    Parse codebook csv

    :param codebook: path of csv codebook to parse

    :return: list of dictionaries...a dictionary denotes a row from the csv
    """

    records = []

    reader = csv.DictReader(codebook, encoding='utf-8', delimiter=delimiter)

    for row in reader:
        is_system = is_true(row['is_system'])

        schema_name = row['table'].strip()
        schema_title = row['form'].strip()

        date_string = row['publish_date'].strip()

        try:
            publish_date = datetime.strptime(
                date_string, '%Y-%m-%d').date()
        except ValueError:
            publish_date = None

        if publish_date is None:
            try:
                publish_date = datetime.strptime(
                    date_string, '%m/%d/%Y').date()
            except ValueError:
                publish_date = None

        if publish_date is None:
            try:
                publish_date = datetime.strptime(
                    date_string, '%m/%d/%y').date()
            except ValueError:
                publish_date = None

        field_name = row['field'].strip()
        field_title = row['title'].strip()
        description = row['description'].strip()

        is_required = is_true(row['is_required'])

        is_collection = is_true(row['is_collection'])

        is_private = is_true(row['is_private'])

        field_type = row['type'].strip().lower()
        if field_type == u'integer':
            field_type = u'number'

        if row['choices'] is not None and \
           row['choices'].strip() != u'' and field_type == u'choice':
            choices = parse_choice_string(row)

        else:
            choices = []

        try:
            order = int(row['order'])
        except ValueError:
            order = None

        records.append({
            'name': field_name,
            'title': field_title,
            'description': description,
            'is_required': is_required,
            'is_system': is_system,
            'is_collection': is_collection,
            'is_private': is_private,
            'type': field_type,
            'order': order,
            'schema_name': schema_name,
            'schema_title': schema_title,
            'publish_date': publish_date,
            'choices': choices
        }
        )

    codebook.close()

    return records
