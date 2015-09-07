import pytest

from tests.conftest import make_environ, USERID, get_csrf_token


ALLOWED = ['administrator', 'manager']
NOT_ALLOWED = ['editor', 'reviewer']


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_occams(group, config, app):
    url = '/imports/codebooks/occams'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_imports_occams_not_allowed(group, config, app):
    url = '/imports/codebooks/occams'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ, expect_errors=True)

    assert response.status_code == 403


def test_not_authenticated_imports_occams(app):
    url = '/imports/codebooks/occams'

    response = app.get(url, expect_errors=True)

    assert response.status_code == 401


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_qds(group, config, app):
    url = '/imports/codebooks/qds'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_imports_qds_not_allowed(group, config, app):
    url = '/imports/codebooks/qds'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ, expect_errors=True)

    assert response.status_code == 403


def test_not_authenticated_imports_qds(app):
    url = '/imports/codebooks/qds'

    response = app.get(url, expect_errors=True)

    assert response.status_code == 401


@pytest.mark.parametrize('group', ALLOWED)
def test_imports_iform(group, config, app):
    url = '/imports/codebooks/iform'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ)

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_imports_iform_not_allowed(group, config, app):
    url = '/imports/codebooks/iform'

    environ = make_environ(userid=USERID, groups=[group])
    response = app.get(url, extra_environ=environ, expect_errors=True)

    assert response.status_code == 403


def test_not_authenticated_imports_iform(app):
    url = '/imports/codebooks/iform'

    response = app.get(url, expect_errors=True)

    assert response.status_code == 401


@pytest.mark.parametrize('group', ALLOWED)
def test_iform_upload(group, config, app):
    import os

    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'iform_input_fixture.json')
    iform = open(filepath, 'r')
    json_data = iform.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', json_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    iform.close()

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_iform_upload_not_allowed(group, config, app):
    import os

    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'iform_input_fixture.json')
    iform = open(filepath, 'r')
    json_data = iform.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', json_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    iform.close()

    assert response.status_code == 403


def test_not_authenticated_imports_iform_upload(app):
    url = '/imports/codebooks/iform/status'

    response = app.post(
        url,
        status='*')

    assert response.status_code == 401


@pytest.mark.parametrize('group', ALLOWED)
def test_occams_upload(group, config, app):
    import os

    url = '/imports/codebooks/occams/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'codebook.csv')
    codebook = open(filepath, 'rb')
    csv_data = codebook.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', csv_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    codebook.close()

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_occams_upload_not_allowed(group, config, app):
    import os

    url = '/imports/codebooks/occams/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'codebook.csv')
    codebook = open(filepath, 'rb')
    csv_data = codebook.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', csv_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    codebook.close()

    assert response.status_code == 403


def test_not_authenticated_imports_occams_upload(app):
    url = '/imports/codebooks/occams/status'

    response = app.post(
        url,
        status='*')

    assert response.status_code == 401


@pytest.mark.parametrize('group', ALLOWED)
def test_qds_upload_codebook(group, config, app):
    import os

    url = '/imports/codebooks/qds/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'qds_input_fixture.csv')
    qds = open(filepath, 'rb')
    qds_data = qds.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', qds_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    qds.close()

    assert response.status_code == 200


@pytest.mark.parametrize('group', NOT_ALLOWED)
def test_qds_upload_codebook_not_allowed(group, config, app):
    import os

    url = '/imports/codebooks/qds/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }
    base = os.path.abspath('../../unit')

    filepath = os.path.join(base, 'qds_input_fixture.csv')
    qds = open(filepath, 'rb')
    qds_data = qds.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', qds_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    qds.close()

    assert response.status_code == 403


def test_qds_not_authenticated_codebook_upload(app):
    url = '/imports/codebooks/qds/status'

    response = app.post(
        url,
        status='*')

    assert response.status_code == 401
