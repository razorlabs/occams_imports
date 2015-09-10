# flake8: noqa

from occams_imports.parsers import iform_json
import unicodecsv as csv


def test_writerow():
    import os

    row = {}
    row['schema_name'] = u'test_schema_name'
    row['schema_title'] = u'test_schema_title'
    row['publish_date'] = u'2015-01-01'
    row['variable'] = u'test_var'
    row['title'] = u'test_title'
    row['description'] = u'test_desc'
    row['is_required'] = False
    row['is_system'] = False
    row['is_collection'] = False
    row['is_private'] = False
    row['field_type'] = False
    row['choices_string'] = u'0=test1;1=test2'
    row['order'] = 7

    output_csv = open('output.csv', 'w')
    writer = csv.writer(output_csv, encoding='utf-8')

    iform_json.writerow(writer, row)
    output_csv.close()

    output_csv = open('output.csv', 'rb')
    reader = csv.reader(output_csv, encoding='utf-8')

    test_row = reader.next()

    assert test_row[0] == u'test_schema_name'
    assert test_row[3] == u'test_var'
    assert test_row[7] == u'False'
    assert test_row[12] == u'7'

    output_csv.close()
    os.remove('output.csv')


def test_output_headers():
    import os

    output_csv = open('output.csv', 'w')
    writer = csv.writer(output_csv, encoding='utf-8')

    iform_json.output_headers(writer)
    output_csv.close()

    output_csv = open('output.csv', 'rb')
    reader = csv.reader(output_csv, encoding='utf-8')

    test_row = reader.next()

    assert test_row[0] == u'table'
    assert test_row[3] == u'field'
    assert test_row[7] == u'is_system'
    assert test_row[12] == u'order'

    output_csv.close()
    os.remove('output.csv')


def test_convert_choices():
    choices = [[u'0', 'label1'], [u'1', 'label2']]
    actual = iform_json.convert_choices(choices)
    expected = u'0=label1;1=label2'

    assert actual == expected


def test_populate_objects():

    options = {u'1140231': {u'options': [{u'condition_value': u'',
                            u'global_id': u'',
                            u'id': 101,
                            u'key_value': u'0',
                            u'label': u'TRUE',
                            u'localizations': [],
                            u'score': 0,
                            u'sort_order': 0},
                           {u'condition_value': u'',
                            u'global_id': u'',
                            u'id': 101,
                            u'key_value': u'1',
                            u'label': u'FALSE',
                            u'localizations': [],
                            u'score': 0,
                            u'sort_order': 1},
                           {u'condition_value': u'',
                            u'global_id': u'',
                            u'id': u'',
                            u'key_value': u'2',
                            u'label': u"Don't know",
                            u'localizations': [],
                            u'score': 0,
                            u'sort_order': 2}],
               u'page_level': {u'created_by': u'test@ucsd.edu',
                               u'created_date': u'2013-10-21T15:53:29+00:00',
                               u'global_id': u'',
                               u'id': u'',
                               u'modified_by': u'test@ucsd.edu',
                               u'modified_date': u'2013-11-23T00:27:48+00:00',
                               u'name': u'test',
                               u'option_icons': u'',
                               u'reference_id': None,
                               u'version': 2}}}

    expected = [[u'0', u'TRUE'], [u'1', u'FALSE'], [u'2', u"Don't know"]]
    actual = iform_json.populate_options(options, u'1140231')

    assert actual == expected


def test_convert():
    codebook = open('iform_input_fixture.json', 'r')

    converted = iform_json.convert(codebook)

    reader = csv.DictReader(converted, encoding='utf-8', delimiter=',')

    for row in reader:
        assert row['form'] == u'test_595_hiv_test_v04'
        assert row['title'] == u'Test label.'

    converted.close()
