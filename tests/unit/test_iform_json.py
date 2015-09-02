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
