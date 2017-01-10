# flake8: noqa

def test_groups():
    from occams_imports.models.groups import groups
    assert groups.administrator() == u'administrator'
    assert groups.manager() == u'manager'
    assert groups.reviewer() == u'reviewer'
    assert groups.member() == u'member'
