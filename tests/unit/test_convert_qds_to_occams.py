# flake8: noqa

from occams_imports.parsers import convert_qds_to_occams as cqo
import unicodecsv as csv


def test_init_row():
    schema_name = u'test_name'
    schema_title = u'test_title'
    publish_date = u'2015-01-01'

    row = cqo.init_row(schema_name, schema_title, publish_date)

    assert row['schema_name'] == u'test_name'
    assert row['is_system'] == u'False'


def test_flush_last_row():
    import os

    output_csv = open('output.csv', 'w')
    writer = csv.writer(output_csv, encoding='utf-8')

    last_row = {}
    last_row['schema_name'] = u'test_schema_name'
    last_row['schema_title'] = u'test_schema_title'
    last_row['publish_date'] = u'2015-01-01'
    last_row['variable'] = u'test_var'
    last_row['title'] = u'test_title'
    last_row['description'] = u'test_desc'
    last_row['is_required'] = False
    last_row['is_system'] = False
    last_row['is_collection'] = False
    last_row['is_private'] = False
    last_row['field_type'] = False
    last_row['choices_string'] = u'0=test1;1=test2'
    last_row['order'] = 6

    row = {}
    row['schema_name'] = u'test_schema_name2'
    row['schema_title'] = u'test_schema_title2'
    row['publish_date'] = u'2015-01-01'
    row['variable'] = u'test_var2'
    row['title'] = u'test_title2'
    row['description'] = u'test_desc2'
    row['is_required'] = False
    row['is_system'] = False
    row['is_collection'] = False
    row['is_private'] = False
    row['field_type'] = False
    row['choices_string'] = u'0=test2;1=test3'
    row['order'] = 7

    choices = [[u'0', 'test1'], [u'1', 'test2']]

    last_order_number, choices = cqo.flush_last_row(
        writer, row, last_row, choices)

    assert last_order_number == 7
    assert choices == []

    output_csv.close()
    os.remove('output.csv')


def test_flush_row():
    import os

    output_csv = open('output.csv', 'w')
    writer = csv.writer(output_csv, encoding='utf-8')

    row = {}
    row['schema_name'] = u'test_schema_name2'
    row['schema_title'] = u'test_schema_title2'
    row['publish_date'] = u'2015-01-01'
    row['variable'] = u'test_var2'
    row['title'] = u'test_title2'
    row['description'] = u'test_desc2'
    row['is_required'] = False
    row['is_system'] = False
    row['is_collection'] = False
    row['is_private'] = False
    row['field_type'] = False
    row['choices_string'] = u'0=test2;1=test3'
    row['order'] = 7

    schema_name = u'test_schema_name'
    schema_title = u'test_schema_title'
    publish_date = u'2015-01-01'

    last_order_number, last_row, row, first_choice_row = cqo.flush_row(
        writer, row, schema_name, schema_title, publish_date)

    assert last_order_number == 7
    assert last_row['title'] == u'test_title2'
    assert last_row['order'] == 7
    assert row['schema_name']  == u'test_schema_name'
    assert row['schema_title'] == u'test_schema_title'
    assert first_choice_row is True

    output_csv.close()
    os.remove('output.csv')

def test_convert():
    codebook = open('qds_input_fixture.csv', 'r')

    converted = cqo.convert(codebook)

    reader = csv.DictReader(converted, encoding='utf-8', delimiter=',')

    row1 = reader.next()
    row2 = reader.next()
    row3 = reader.next()

    assert row1['field'] == u'TODAY'
    assert row1['table'] == u'Test_Schema_Title'
    assert row1['type'] == u'string'

    assert row2['field'] == u'GENDER'
    assert row2['table'] == u'Test_Schema_Title'
    assert row2['type'] == u'choice'

    assert row3['field'] == u'BIRTHSEX'
    assert row3['table'] == u'Test_Schema_Title'
    assert row3['type'] == u'choice'

    converted.close()
