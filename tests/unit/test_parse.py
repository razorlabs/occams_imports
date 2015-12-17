# flake8: noqa

import mock

from occams_imports.parsers import parse


def test_is_true():
    assert parse.is_true('True') is True
    assert parse.is_true('T') is True
    assert parse.is_true('t') is True
    assert parse.is_true(1) is True
    assert parse.is_true('F') is False
    assert parse.is_true('false') is False
    assert parse.is_true(0) is False


def test_remove_system_entries():
    records = [{'is_system': True}, {'is_system': False}]

    assert parse.remove_system_entries(records) == [{'is_system': False}]


def test_parse_choice_string():
    row = {
        'choices': '0=MyLabel;1=KeySeparatedByEquals;3=DelimitedBySemiColon'
    }

    choices = parse.parse_choice_string(row)
    expected = [
        ['0', 'MyLabel'],
        ['1', 'KeySeparatedByEquals'],
        ['3', 'DelimitedBySemiColon']]

    assert choices == expected

    row = {
        'choices': '0=MyLabel;1= TestWhiteSpace'
    }

    choices = parse.parse_choice_string(row)
    expected = [
        ['0', 'MyLabel'],
        ['1', 'TestWhiteSpace']]

    assert choices == expected


def test_get_choices():
    raw_choices = [[u'0', u'label'], [u'1', u'label2']]

    choices = parse.get_choices(raw_choices)

    assert choices['0'].name == u'0'
    assert choices['0'].title == u'label'
    assert choices['0'].order == 0

    assert choices['1'].name == u'1'
    assert choices['1'].title == u'label2'
    assert choices['1'].order == 1


def test_parse_dispatch():
    import six
    from occams_imports.parsers import parse

    with mock.patch('occams_imports.parsers.parse.iform_json') as mock_convert:
        codebook_format = u'iform'
        delimiter = u'comma'

        codebook = six.StringIO()
        mock_convert.convert.return_value = six.StringIO()

        response = parse.parse_dispatch(codebook, codebook_format, delimiter)
        codebook.close()

        assert mock_convert.convert.called == True

    with mock.patch('occams_imports.parsers.parse.convert_qds_to_occams') \
        as mock_convert:

        codebook_format = u'qds'
        delimiter = u'comma'

        codebook = six.StringIO()
        mock_convert.convert.return_value = six.StringIO()

        response = parse.parse_dispatch(codebook, codebook_format, delimiter)
        codebook.close()

        assert mock_convert.convert.called == True


def test_parse_dispatch_tab_delimiter():
    import six
    from occams_imports.parsers import parse

    with mock.patch('occams_imports.parsers.parse.iform_json') as mock_convert:
        codebook_format = u'iform'
        delimiter = u'tab'

        codebook = six.StringIO()
        mock_convert.convert.return_value = six.StringIO()

        response = parse.parse_dispatch(codebook, codebook_format, delimiter)
        codebook.close()

        assert mock_convert.convert.called == True

    with mock.patch('occams_imports.parsers.parse.convert_qds_to_occams') \
        as mock_convert:

        codebook_format = u'qds'
        delimiter = u'comma'

        codebook = six.StringIO()
        mock_convert.convert.return_value = six.StringIO()

        response = parse.parse_dispatch(codebook, codebook_format, delimiter)
        codebook.close()

        assert mock_convert.convert.called == True


def test_convert_date():
    import datetime
    from occams_imports.parsers.parse import convert_date

    actual = convert_date('ajdkfj')
    assert actual == None

    actual = convert_date('2015-01-01')
    assert actual == datetime.date(2015, 1, 1)

    actual = convert_date('01/01/2015')
    assert actual == datetime.date(2015, 1, 1)

    actual = convert_date('01/01/15')
    assert actual == datetime.date(2015, 1, 1)


def test_choices_list():
    from occams_imports.parsers.parse import choices_list

    actual = choices_list(u'', u'number', {'choices': None})
    assert actual == []

    actual = choices_list(u'0=MyLabel', u'choice', {'choices': '0=MyLabel'})
    assert actual == [['0', 'MyLabel']]


def test_parse():
    from datetime import date
    from pkg_resources import resource_filename

    codebook = open(
        resource_filename('tests.fixtures', 'codebook.csv'), 'rb')
    records = parse.parse(codebook)

    assert len(records) == 27
    assert records[0]['schema_name'] == u'ClinicalAssessment595vitd'
    assert records[0]['name'] == u'id'
    assert records[0]['is_system'] is True
    assert records[0]['is_collection'] is False
    assert records[13]['name'] == u'cont'
    assert records[13]['is_required'] is True
    assert records[13]['is_system'] is False
    assert records[13]['is_collection'] is False
    assert records[13]['is_private'] is False
    assert records[13]['choices'] == [
        ['0', 'No'],
        ['1', 'Yes (Week 36, continuing to Week 48)'],
        ['2', 'Yes (Week 48, continuing post study)']]
    assert records[13]['publish_date'] == date(2014, 10, 23)



