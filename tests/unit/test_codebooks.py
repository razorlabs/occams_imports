import pytest

from tests.conftest import make_environ, USERID, get_csrf_token


@pytest.mark.parametrize('group', ['administrator'])
def test_qds_upload_validate(group, config, app):
    from pkg_resources import resource_filename

    url = '/imports/codebooks/qds/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma',
        'site': u'DRSC'
    }

    qds = open(resource_filename('tests', 'qds_input_fixture.csv'), 'rb')
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
    from pkg_resources import resource_filename

    url = '/imports/codebooks/occams/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'delimiter': u'comma',
        'site': u'DRSC'
    }

    codebook = open(resource_filename('tests', 'codebook.csv'), 'rb')
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
    assert u'Codebook Import Status' in response.body
    assert u'2014-10-23' in response.body
    assert u'Fields evaluated' in response.body


@pytest.mark.parametrize('group', ['administrator'])
def test_iform_upload_validate(group, config, app):
    from pkg_resources import resource_filename

    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': u'dry',
        'site': u'DRSC'
    }

    iform = open(resource_filename('tests', 'iform_input_fixture.json'), 'r')
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

    assert u'test_595_hiv_test_v04' in response.body
    assert u'Codebook Import Status' in response.body
    assert u'2013-10-21' in response.body
    assert u'Fields evaluated' in response.body


@pytest.mark.parametrize('group', ['administrator'])
def test_qds_insert(group, config, app):
    import datetime
    from pkg_resources import resource_filename
    from occams import Session
    from occams_datastore import models as datastore

    url = '/imports/codebooks/qds/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': None,
        'site': u'DRSC',
        'delimiter': u'comma'
    }

    qds = open(resource_filename('tests', 'qds_input_fixture.csv'), 'rb')
    qds_data = qds.read()

    app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.csv', qds_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    qds.close()

    form = Session.query(datastore.Schema).one()
    attributes = Session.query(datastore.Attribute).filter(
        datastore.Schema.id == form.id).order_by(
        datastore.Attribute.name).all()

    assert form.name == u'Test_Schema_Title'
    assert form.title == u'Test Schema Title'
    assert form.publish_date == datetime.date(2015, 8, 11)
    assert attributes[0].name == u'BIRTHSEX'
    assert attributes[1].name == u'GENDER'
    assert attributes[2].name == u'TODAY'
    assert attributes[0].type == u'choice'
    assert attributes[1].type == u'choice'
    assert attributes[2].type == u'string'


@pytest.mark.parametrize('group', ['administrator'])
def test_occams_codebook_insert(group, config, app):
    import datetime
    from pkg_resources import resource_filename
    from occams import Session
    from occams_datastore import models as datastore

    url = '/imports/codebooks/occams/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': None,
        'site': u'DRSC',
        'delimiter': u'comma'
    }

    codebook = open(resource_filename('tests', 'codebook.csv'), 'rb')
    csv_data = codebook.read()

    app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.csv', csv_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    codebook.close()

    form = Session.query(datastore.Schema).one()
    attributes = Session.query(datastore.Attribute).filter(
        datastore.Schema.id == form.id).order_by(
        datastore.Attribute.name).all()

    assert form.name == u'ClinicalAssessment595vitd'
    assert form.title == u'595 Vitamin D - Clinical Assessment'
    assert form.publish_date == datetime.date(2014, 10, 23)
    assert attributes[0].name == u'cont'
    assert attributes[2].name == u'frac'

    expected_title = u'Has the subject had any fractures since the visit?'
    assert attributes[2].title == expected_title

    assert attributes[2].choices['0'].title == u'No'


@pytest.mark.parametrize('group', ['administrator'])
def test_iform_insert(group, config, app):
    import datetime
    from pkg_resources import resource_filename
    from occams import Session
    from occams_datastore import models as datastore

    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': None,
        'site': u'DRSC'
    }

    iform = open(resource_filename('tests', 'iform_input_fixture.json'), 'r')
    json_data = iform.read()

    app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', json_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    iform.close()

    form = Session.query(datastore.Schema).one()
    attributes = Session.query(datastore.Attribute).filter(
        datastore.Schema.id == form.id).order_by(
        datastore.Attribute.name).all()

    assert form.name == u'test_595_hiv_test_v04'
    assert form.title == u'test_595_hiv_test_v04'
    assert form.publish_date == datetime.date(2013, 10, 21)
    assert attributes[0].choices['2'].name == u'2'
    assert attributes[0].choices['2'].title == u'Dont know'
    assert attributes[0].choices['2'].order == 2


@pytest.mark.parametrize('group', ['administrator'])
def test_iform_insert_import_table(group, config, app):
    from pkg_resources import resource_filename
    from occams import Session
    from occams_imports import models

    url = '/imports/codebooks/iform/status'

    environ = make_environ(userid=USERID, groups=[group])
    csrf_token = get_csrf_token(app, environ)

    data = {
        'mode': None,
        'site': u'DRSC'
    }

    iform = open(resource_filename('tests', 'iform_input_fixture.json'), 'r')
    json_data = iform.read()

    app.post(
        url,
        extra_environ=environ,
        expect_errors=True,
        upload_files=[('codebook', 'test.json', json_data)],
        headers={
            'X-CSRF-Token': csrf_token,
        },
        params=data)

    iform.close()

    import_data = Session.query(models.Import).one()

    assert import_data.site == u'DRSC'
    assert import_data.schema.name == u'test_595_hiv_test_v04'
