"""
Parse data from iFormBuilder JSON export

JSON export has a data_type map with numerical keys.

Here is a map of key, values from the iFormBuilder documentation:

https://iformbuilder.zendesk.com/hc/en-us/articles/201702880?

1: Text
2: Number
3: Date
4: Time
5: Date-Time
6: Toggle
7: Select
8: Pick List
9: Multi-Select
10: Range
11: Image
12: Signature
13: Sound
15: QR Code
16: Label
17: Divider
18: Subform
19: Text Area
20: Phone
21: SSN
22: Email
23: Zip Code
24: Assign To
25: Unique ID
28: Drawing
31: RFID
32: Attachment
33: Read Only
35: Image Label
37: Location
38: Socket Scanner
39: Linea Pro
"""

import json
import six

import unicodecsv as csv

# maps iFormBuilder data_type code to OCCAMS datastore datatype
DATA_TYPE_MAP = {
    7: u'choice',
    8: u'choice'
}


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


def populate_options(options, optionlist_id):
    """
    Retrieve all options form json export

    :options: dict of options
    :optionlist_id: id of the option to retrieve

    :return: list of lists of key and label, i.e. [[key, label],[0:u'value']]
    """
    option_list = []
    if unicode(optionlist_id) in options:
        for options in options[unicode(optionlist_id)]['options']:
            option_list.append([options['key_value'], options['label']])

    return option_list


def convert(codebook):
    #jfile = open(codebook, 'r')
    data = codebook.read()
    jdata = json.loads(data)

    output_csv = six.StringIO()
    writer = csv.writer(output_csv, encoding='utf-8')

    output_headers(writer)

    options = jdata['assets_map']['option_list']

    # from pdb import set_trace; set_trace()

    for pages in jdata['assets_map']['pages']:
        page = jdata['assets_map']['pages'][pages]['elements']
        schema_name = jdata['assets_map']['pages'][pages]['page_level']['name']
        schema_title = schema_name
        publish_date = jdata['assets_map']['pages'][pages]['page_level']['created_date'][0:10]
        # from pdb import set_trace; set_trace()
        print schema_name, schema_title, publish_date
        for question in page:
            row = {
                u'schema_name': schema_name,
                u'schema_title': schema_title,
                u'publish_date': publish_date,
                u'title': question[u'label'],
                u'description': u'',
                u'is_required': u'False',
                u'is_system': u'False',
                u'is_collection': u'False',
                u'is_private': u'False'
            }
            # skip questions with no sort order or data_type 16
            # these are instrucitons...this is an assumption
            try:
                row[u'order'] = question[u'sort_order']
            except KeyError:
                continue

            row['field_type'] = DATA_TYPE_MAP[question[u'data_type']]
            try:
                optionlist_id = question['optionlist_id']
            except KeyError:
                optionlist_id = None

            base_string = '_'.join(schema_name.split('_')[2:-1])
            row['variable'] = '{}_{}'.format(base_string, question[u'name'])
            # print question['name'], question['label'], question['created_date']
            if optionlist_id:
                choices = populate_options(options, optionlist_id)
                row['choices_string'] = convert_choices(choices)
            else:
                row['choices_string'] = u''

            writerow(writer, row)

    codebook.close()
    output_csv.flush()
    output_csv.seek(0)

    return output_csv

