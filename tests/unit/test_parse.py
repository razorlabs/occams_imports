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
