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

    :schema_name: system name of the schema
    :schema_title: human readable name of the schema
    :publish_date: publish date of the schema
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


def flush_last_row(writer, row, last_row, choices):
    """
    :writer:  csv writer
    :row: dictionary of row data
    :last_row: dictionary of data from the last row
    :choices: list of choices
    :return: last_order_number, choices
    """
    last_row['choices_string'] = convert_choices(choices)
    last_order_number = row['order']
    last_row['field_type'] = u'choice'
    writerow(writer, last_row)
    choices = []

    return last_order_number, choices


def flush_row(writer, row, schema_name, schema_title, publish_date):
    """
    :writer:  csv writer
    :row: dictionary of row data
    :schema_name: system name of the schema
    :schema_title: human readable name of the schema
    :publish_date: publish date of the schema
    :return: last_order_number, last_row, row, first_choice_row
    """
    writerow(writer, row)
    last_order_number = row['order']
    last_row = dict(row)
    row = init_row(schema_name, schema_title, publish_date)
    first_choice_row = True

    return last_order_number, last_row, row, first_choice_row


def convert(codebook, delimiter=','):
    """
    Convert QDS file to occams format

    :param codebook:
    :param delimiter:
    :return:
    """
    reader = csv.reader(codebook, encoding='utf-8', delimiter=delimiter)

    headers = reader.next()

    output_csv = six.StringIO()
    writer = csv.writer(output_csv, encoding='utf-8')

    output_headers(writer)

    first_row = True
    choices = []
    last_row = {}
    first_choice_row = True
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

        if row['order'] == last_order_number:
            last_row = dict(row)
            choices.append([choice_order, choice_label])
            last_order_number = row['order']
            first_choice_row = False

        elif row['order'] != last_order_number and choice_label == u'':
            if choices:
                last_order_number, choices = flush_last_row(
                    writer, row, last_row, choices)

            row['choices_string'] = u''
            last_order_number, last_row, row, first_choice_row = flush_row(
                writer, row, schema_name, schema_title, publish_date)

        elif row['order'] != last_order_number and choice_label != u'':
            if choices:
                last_order_number, choices = flush_last_row(
                    writer, row, last_row, choices)
                first_choice_row = True

            if first_choice_row:
                last_row = dict(row)
                choices.append([choice_order, choice_label])
                first_choice_row = False
                last_order_number = row['order']
            else:
                choices.append([choice_order, choice_label])
                row['choices_string'] = convert_choices(choices)
                row['field_type'] = u'choice'

                last_order_number, last_row, row, first_choice_row = flush_row(
                    writer, row, schema_name, schema_title, publish_date)

                choices = []

    if choices:
        row['choices_string'] = convert_choices(choices)
        row['field_type'] = u'choice'
        last_order_number, last_row, row, first_choice_row = flush_row(
            writer, row, schema_name, schema_title, publish_date)

    codebook.close()

    output_csv.flush()
    output_csv.seek(0)

    return output_csv
