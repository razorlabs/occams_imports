from occams_imports.parsers import iform_json


def test_convert_choices():
    choices = [[u'0', 'label1'], [u'1', 'label2']]
    actual = iform_json.convert_choices(choices)
    expected = u'0=label1;1=label2'

    assert actual == expected
