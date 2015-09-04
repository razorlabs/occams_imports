import pytest

from tests.conftest import make_environ, USERID, get_csrf_token


ALLOWED = ['administrator', 'manager']


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_occams(group, config, app):
    url = '/imports/codebooks/occams'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_qds(group, config, app):
    url = '/imports/codebooks/qds'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_iform(group, config, app):
    url = '/imports/codebooks/iform'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200
