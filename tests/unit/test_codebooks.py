import pytest

from tests.conftest import make_environ, USERID, get_csrf_token


@pytest.mark.parametrize('group', ['administrator'])
def test_qds_upload_codebook_validate(group, config, app):
    url = '/imports/codebooks/qds/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }

    qds = open('qds_input_fixture.csv', 'rb')
    qds_data = qds.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.csv', qds_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    qds.close()

    assert response.status_code == 200
    assert u'Test_Schema_Title' in response.body
    assert u'Test Schema Title' in response.body
    assert u'Codebook Import Status' in response.body
    assert u'2015-08-11' in response.body
    assert u'Fields evaluated' in response.body


@pytest.mark.parametrize('group', ['administrator'])
def test_occams_upload_validate(group, config, app):
    url = '/imports/codebooks/occams/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma'
    }

    codebook = open('codebook.csv', 'rb')
    csv_data = codebook.read()

    response = app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.csv', csv_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    codebook.close()

    assert response.status_code == 200
    assert u'ClinicalAssessment595vitd' in response.body
    assert u"{'name': u'This field is required.'}" in response.body
    assert u'Codebook Import Status' in response.body
    assert u'2014-10-23' in response.body
    assert u'Fields evaluated' in response.body


@pytest.mark.parametrize('group', ['administrator'])
def test_iform_upload(group, config, app):
    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry'
    }

    iform = open('iform_input_fixture.json', 'r')
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
    assert u'test_595_hiv_test_v04' in response.body
    assert u'Codebook Import Status' in response.body
    assert u'2013-10-21' in response.body
    assert u'Fields evaluated' in response.body
