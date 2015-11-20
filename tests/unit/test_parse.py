# flake8: noqa

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



def test_parse():
    from datetime import date
    from pkg_resources import resource_filename

    codebook = open(resource_filename('tests', 'codebook.csv'), 'rb')
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


def test_get_choices():
    raw_choices = [[u'0', u'label'], [u'1', u'label2']]

    choices = parse.get_choices(raw_choices)

    assert choices['0'].name == u'0'
    assert choices['0'].title == u'label'
    assert choices['0'].order == 0

    assert choices['1'].name == u'1'
    assert choices['1'].title == u'label2'
    assert choices['1'].order == 1
