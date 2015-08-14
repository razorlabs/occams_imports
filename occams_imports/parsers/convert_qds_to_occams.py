"""
Transform data from the QDS csv codebook format to the
occams codebook format

Per Remi...each input file shall contain only one form and one publish_date

"""
import six

import unicodecsv as csv

from convert_iform_to_occams import output_headers, writerow, convert_choices


def init_row(schema_name, schema_title, publish_date):
    """
    Init a row dict but keep incrementing the order count
    """
    row = {}

    row['is_required'] = u'False'
    row['is_system'] = u'False'
    row['is_collection'] = u'False'
    row['is_private'] = u'False'
    row['schema_name'] = schema_name
    row['schema_title'] = schema_title
    row['publish_date'] = publish_date

    return row


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

    first_row = True
    choices = []
    in_choice = False
    last_order_number = -1

    for field in reader:
        if first_row:
            schema_name = field[0].strip()
            schema_title = field[1].strip()
            publish_date = field[2].strip()
            row = init_row(schema_name, schema_title, publish_date)
            first_row = False

        row['variable'] = field[3].strip()
        row['order'] = field[5].strip()
        row['title'] = field[6].strip()
        row['units'] = field[9].strip()
        row['field_type'] = field[10].strip()

        choice_label = field[8].strip()
        variable2 = field[4].strip()
        choice_order = field[7].strip()

        if row['field_type'] in [u'float', u'int']:
            row['field_type'] = u'number'
        row['description'] = u''

        # not sure what to do with these, skip for now
        if variable2 == u'Calculated':
            continue

        if row['order'] != last_order_number and not in_choice:
            row['choices_string'] = u''
            writerow(writer, row)
            last_order_number = row['order']
            row = init_row(schema_name, schema_title, publish_date)

        elif row['order'] != last_order_number and in_choice:
            in_choice = False
            last_order_number = row['order']
            row['choices_string'] = convert_choices(choices)
            row['field_type'] = u'choice'
            writerow(writer, row)
            row = init_row(schema_name, schema_title, publish_date)

        elif row['order'] == last_order_number:
            choices.append([choice_order, choice_label])
            in_choice = True

    codebook.close()

    output_csv.flush()
    output_csv.seek(0)

    return output_csv
