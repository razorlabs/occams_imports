import pytest
import mock

from occams.testing import USERID, make_environ, get_csrf_token


class TestCodebooks:

    @pytest.fixture(autouse=True)
    def populate(self, app, db_session):
        import transaction
        from occams_datastore import models as datastore
        from occams_studies import models as studies

        # Any view-dependent data goes here
        with transaction.manager:
            user = datastore.User(key=USERID)
            drsc = studies.Site(name=u'drsc', title=u'DRSC')
            ucsd = studies.Site(name=u'ucsd', title=u'UCSD')
            ucla = studies.Site(name=u'ucla', title=u'UCLA')
            ebac = studies.Site(name=u'ebac', title=u'EBAC')
            lac = studies.Site(name=u'lac', title=u'LAC')
            db_session.add(user)
            db_session.add(drsc)
            db_session.add(ucsd)
            db_session.add(ucla)
            db_session.add(ebac)
            db_session.add(lac)
            db_session.flush()

    @pytest.mark.parametrize('group', ['administrator'])
    def test_qds_upload_validate(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'site': u'DRSC'
        }

        qds = open(
            resource_filename('tests.fixtures', 'qds_input_fixture.csv'), 'rb')
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
    def test_occams_upload_validate(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'site': u'DRSC'
        }

        codebook = open(
            resource_filename('tests.fixtures', 'codebook.csv'), 'rb')
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
    def test_iform_upload_validate(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'site': u'DRSC'
        }

        iform = open(
            resource_filename(
                'tests.fixtures', 'iform_input_fixture.json'), 'r')
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
    def test_qds_insert(self, app, db_session, group):
        import datetime
        from pkg_resources import resource_filename
        from occams_datastore import models as datastore

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'site': u'DRSC',
            'delimiter': u'comma'
        }

        qds = open(
            resource_filename('tests.fixtures', 'qds_input_fixture.csv'), 'rb')
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

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
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
    def test_occams_codebook_insert(self, app, db_session, group):
        import datetime
        from pkg_resources import resource_filename
        from occams_datastore import models as datastore

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'site': u'DRSC',
            'delimiter': u'comma'
        }

        codebook = open(resource_filename('tests.fixtures', 'codebook.csv'), 'rb')
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

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
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
    def test_iform_insert(self, app, db_session, group):
        import datetime
        from pkg_resources import resource_filename
        from occams_datastore import models as datastore

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'site': u'DRSC'
        }

        iform = open(
            resource_filename('tests.fixtures', 'iform_input_fixture.json'), 'r')
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

        form = db_session.query(datastore.Schema).one()
        attributes = db_session.query(datastore.Attribute).filter(
            datastore.Schema.id == form.id).order_by(
            datastore.Attribute.name).all()

        assert form.name == u'test_595_hiv_test_v04'
        assert form.title == u'test_595_hiv_test_v04'
        assert form.publish_date == datetime.date(2013, 10, 21)
        assert attributes[0].choices['2'].name == u'2'
        assert attributes[0].choices['2'].title == u'Dont know'
        assert attributes[0].choices['2'].order == 2

    @pytest.mark.parametrize('group', ['administrator'])
    def test_iform_insert_import_table(self, app, db_session, group):
        from pkg_resources import resource_filename
        from occams_imports import models

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': None,
            'site': u'DRSC'
        }

        iform = open(
            resource_filename(
                'tests.fixtures', 'iform_input_fixture.json'), 'r')
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

        import_data = db_session.query(models.Import).one()

        assert import_data.site.title == u'DRSC'
        assert import_data.schema.name == u'test_595_hiv_test_v04'

    def test_process_import(self, db_session):
        import datetime

        from occams_datastore import models as datastore
        from occams_studies import models as studies
        from occams_imports import models
        from occams_imports.views.codebooks import process_import

        attr_dict = {}

        schema = datastore.Schema(
            name=u'test_name',
            title=u'test_title',
            publish_date=datetime.date.today()
        )

        site = studies.Site(
            name=u'test_site', title=u'test_title'
        )

        process_import(schema, attr_dict, site, db_session)

        imported = (
            db_session.query(models.Import)
            .filter(models.Import.site == site)
            .one())

        assert imported.site.name == site.name


def test_validate_populate_imports(monkeypatch):
    import datetime

    from occams_imports.views.codebooks import validate_populate_imports

    record = {
        'schema_name': u'test_schema_name',
        'schema_title': u'test_schema_title',
        'publish_date': datetime.date.today(),
        'name': u'test_name',
        'title': u'test_title',
        'description': u'',
        'is_required': False,
        'is_collection': False,
        'is_private': False,
        'type': u'number',
        'order': 0,
        'choices': []
    }

    mock_validate = mock.MagicMock()
    mock_validate.return_value = True
    mock_field_form = mock.MagicMock()
    mock_field_form.from_json.return_value = mock_validate

    monkeypatch.setattr(
        'occams_imports.views.codebooks.FieldFormFactory',
        lambda **x: mock_field_form)

    errors, imports, forms = validate_populate_imports(None, [record])

    assert errors == []
    assert len(imports) == 1
    assert len(forms) == 1
    assert forms[0]['name'] == u'test_schema_name'
    assert forms[0]['title'] == u'test_schema_title'
    assert imports[0][0].name == u'test_name'
    assert imports[0][1].name == u'test_schema_name'


def test_log_errors():
    from occams_imports.views.codebooks import log_errors
    errors = {
        'error': 'something is broken'
    }

    record = {
        'schema_name': u'test_schema_name',
        'schema_title': u'test_schema_title',
        'name': u'test_name',
        'title': u'test_title'
    }

    output = log_errors(errors, record)

    assert output['errors'] == errors
    assert output['name'] == record['name']


def test_group_imports_by_schema():
    import datetime

    from occams_datastore import models as datastore
    from occams_imports.views.codebooks import group_imports_by_schema

    with mock.patch('occams_imports.views.codebooks.process_import') \
        as mock_process_import:

        db_session = None
        site = u'UCSD'
        attribute = datastore.Attribute(
            name=u'test_attr_name',
            title=u'test_title'
        )
        attribute2 = datastore.Attribute(
            name=u'test_attr_name2',
            title=u'test_title2'
        )

        schema = datastore.Schema(
            name=u'test_schema_name',
            title=u'test_schema_title',
            publish_date=datetime.date.today())

        schema2 = datastore.Schema(
            name=u'test_schema_name2',
            title=u'test_schema_title2',
            publish_date=datetime.date.today())

        imports = [(attribute, schema), (attribute2, schema2)]

        response = group_imports_by_schema(imports, site, db_session)

        mock_process_import.assert_any_call(
            imports[0][1], {u'test_attr_name': imports[0][0]}, u'UCSD', None)

        mock_process_import.assert_any_call(
            imports[1][1], {u'test_attr_name2': imports[1][0]}, u'UCSD', None)

        assert mock_process_import.call_count == 2
        assert response == 2
