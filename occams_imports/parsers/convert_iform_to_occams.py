"""
Transform data from the iForm CCTG csv codebook format to the
occams codebook format

Parsing assumptions made:

* If the row ends in a choice datatype, the next rows are the choices
* All the datatypes are in the TYPES_MAP...do more research here
"""

import sys
import argparse

import unicodecsv as csv

TYPES_MAP = {u'NUMBER': u'numeric',
             u'TEXT': u'text',
             u'SUBFORM': None,
             u'PICKLIST': u'choice',
             u'SELECT': u'choice',
             u'MULTISELECT': u'choice'}


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


def writerow(writer, row):
    """
    Write row to file

    :param row: dictionary of elements denoting a row of schema/attribute data
    :param writer: python csv writer object
    :return: row written to csv file
    """
    writer.writerow([
        row['schema_name'],
        row['schema_title'],
        row['publish_date'],
        row['variable'],
        row['title'],
        row['description'],
        row['is_required'],
        row['is_system'],
        row['is_collection'],
        row['is_private'],
        row['field_type'],
        row['choices_string'],
        row['order']])


def output_headers(writer):
    """
    Output headers to file

    :param writer: python csv writer object
    :return: headers written to file
    """
    output_headers = [
        u'table',
        u'form',
        u'publish_date',
        u'field',
        u'title',
        u'description',
        u'is_required',
        u'is_system',
        u'is_collection',
        u'is_private',
        u'type',
        u'choices',
        u'order'
    ]
    writer.writerow(output_headers)


def convert(schema_name, schema_title, publish_date, codebook, delimiter=','):
    """
    Convert iForm file to occams format

    :param schema_name:
    :param schema_title:
    :param publish_date:
    :param codebook:
    :param delimiter:
    :return:
    """
    with open(codebook, 'rb') as csvfile:
        reader = csv.reader(csvfile, encoding='utf-8', delimiter=delimiter)

        # Remove headers from file
        headers = reader.next()

        output_csv = open('output.csv', 'wb')
        writer = csv.writer(output_csv, encoding='utf-8')

        row = {}

        row['is_required'] = u'False'
        row['is_system'] = u'False'
        row['is_collection'] = u'False'
        row['is_private'] = u'False'
        row['schema_name'] = schema_name
        row['schema_title'] = schema_title
        row['publish_date'] = publish_date
        row['order'] = 0

        output_headers(writer)

        choices = []
        in_choice = False

        for field in reader:
            # this is a question row, not a choice row
            if field[0]:
                if in_choice:
                    row['choices_string'] = convert_choices(choices)
                    writerow(writer, row)
                    in_choice = False
                    choices = []
                row['order'] += 1
                row['variable'] = field[0].strip()
                row['title'] = field[1].strip()
                row['field_type'] = TYPES_MAP[field[2].strip()]
                row['description'] = u''
                if row['field_type'] not in [u'choice']:
                    writerow(writer, row)

                else:
                    in_choice = True

            # this is a choice row
            else:
                choice_label = field[3].strip()
                choice_order = field[4].strip()
                choices.append([choice_order, choice_label])

        # process last record
        if in_choice:
            row['choices_string'] = convert_choices(choices)
            writerow(writer, row)

        output_csv.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('codebook', help='path of codebook to parse')
    parser.add_argument('schema_name', help='path of codebook to parse')
    parser.add_argument('schema_title', help='path of codebook to parse')
    parser.add_argument('publish_date', help='Date in the form yyyy-mm-dd')
    parser.add_argument('-d', '--delimeter',
                        help='delimeter...not required for comma delimeter')

    args = parser.parse_args()

    codebook = args.codebook
    schema_name = args.schema_name
    schema_title = args.schema_title
    publish_date = args.publish_date

    if args.delimeter:
        delimeter = args.delimeter
        convert(schema_name, schema_title, publish_date, codebook, delimeter)
    else:
        convert(schema_name, schema_title, publish_date, codebook)

if __name__ == '__main__':
    sys.exit(main())
