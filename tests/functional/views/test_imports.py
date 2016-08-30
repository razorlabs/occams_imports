import pytest

from occams.testing import USERID, make_environ, get_csrf_token


ADMINISTRATOR = 'administrator'
MANAGER = 'manager'
REVIEWER = 'reviewer'
MEMBER = 'member'


class TestImports:

    @pytest.fixture(autouse=True)
    def populate(self, app, db_session):
        from datetime import date

        import transaction
        from occams_datastore import models as datastore
        from occams_studies import models as studies

        # Any view-dependent data goes here
        with transaction.manager:
            user = datastore.User(key=USERID)
            drsc = studies.Study(
                name=u'drsc',
                title=u'DRSC',
                short_title=u'dr',
                code=u'drs',
                consent_date=date.today(),
                is_randomized=False
            )
            ucsd = studies.Study(
                name=u'ucsd',
                title=u'UCSD',
                short_title=u'ucsd',
                code=u'ucsd',
                consent_date=date.today(),
                is_randomized=False
            )
            db_session.add(user)
            db_session.add(drsc)
            db_session.add(ucsd)
            db_session.flush()

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_imports_occams(self, app, group):
        url = '/imports/codebooks/occams'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_imports_occams_not_allowed(self, app, group):
        url = '/imports/codebooks/occams'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ, expect_errors=True)

        assert response.status_code == 403

    def test_not_authenticated_imports_occams(self, app):
        url = '/imports/codebooks/occams'

        response = app.get(url, expect_errors=True)

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_imports_qds(self, app, group):
        url = '/imports/codebooks/qds'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_imports_qds_not_allowed(self, app, group):
        url = '/imports/codebooks/qds'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ, expect_errors=True)

        assert response.status_code == 403

    def test_not_authenticated_imports_qds(self, app):
        url = '/imports/codebooks/qds'

        response = app.get(url, expect_errors=True)

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_imports_iform(self, app, group):
        url = '/imports/codebooks/iform'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_imports_iform_not_allowed(self, app, group):
        url = '/imports/codebooks/iform'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ, expect_errors=True)

        assert response.status_code == 403

    def test_not_authenticated_imports_iform(self, app):
        url = '/imports/codebooks/iform'

        response = app.get(url, expect_errors=True)

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_iform_upload(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'study': u'DRSC'
        }

        iform = open(
            resource_filename('tests.fixtures', 'iform_input_fixture.json'))
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

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_iform_upload_not_allowed(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/iform/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'study': u'DRSC'
        }

        iform = open(resource_filename(
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

        assert response.status_code == 403

    def test_not_authenticated_imports_iform_upload(self, app):
        url = '/imports/codebooks/iform/status'

        response = app.post(
            url,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_occams_upload(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
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

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_occams_upload_not_allowed(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/occams/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
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

        assert response.status_code == 403

    def test_not_authenticated_imports_occams_upload(self, app):
        url = '/imports/codebooks/occams/status'

        response = app.post(
            url,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR])
    def test_qds_upload_codebook(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
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

    @pytest.mark.parametrize('group', [MANAGER, REVIEWER, MEMBER])
    def test_qds_upload_codebook_not_allowed(self, app, group):
        from pkg_resources import resource_filename

        url = '/imports/codebooks/qds/status'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mode': u'dry',
            'delimiter': u'comma',
            'study': u'DRSC'
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

        assert response.status_code == 403

    def test_qds_not_authenticated_codebook_upload(self, app):
        url = '/imports/codebooks/qds/status'

        response = app.post(
            url,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER])
    def test_mappings_delete_allowed(self, app, group):
        url = '/imports/mappings/delete'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mapped_delete': []
        }

        response = app.delete_json(
            url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params=data)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [REVIEWER, MEMBER])
    def test_mappings_delete_not_allowed(self, app, group):
        url = '/imports/mappings/delete'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        data = {
            'mapped_delete': []
        }

        response = app.delete_json(
            url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params=data)

        assert response.status_code == 403

    def test_mappings_delete_not_authenticated(self, app):
        url = '/imports/mappings/delete'

        response = app.delete(
            url,
            xhr=True,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER, REVIEWER, MEMBER])
    def test_cytoscape_demo_allowed(self, app, group):
        url = '/imports/demos/cytoscapejs'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    def test_cytoscape_demo_not_authenticated(self, app):
        url = '/imports/demos/cytoscapejs'

        response = app.get(
            url,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER])
    def test_imports_mappings_direct(self, app, group):
        url = '/imports/mappings/direct'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [REVIEWER, MEMBER])
    def test_imports_mappings_direct_not_allowed(self, app, group):
        url = '/imports/mappings/direct'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ, expect_errors=True)

        assert response.status_code == 403

    def test_imports_mapping_direct_not_authenticated(self, app):
        url = '/imports/mappings/direct'

        response = app.get(url, expect_errors=True)

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER])
    def test_imports_mappings_imputation(self, app, group):
        url = '/imports/mappings/direct'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ)

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [REVIEWER, MEMBER])
    def test_imports_mappings_imputation_not_allowed(self, app, group):
        url = '/imports/mappings/direct'

        environ = make_environ(userid=USERID, groups=[group])
        response = app.get(url, extra_environ=environ, expect_errors=True)

        assert response.status_code == 403

    def test_imports_mapping_imputation_not_authenticated(self, app):
        url = '/imports/mappings/direct'

        response = app.get(url, expect_errors=True)

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER, REVIEWER])
    def test_get_schemas(self, app, group):
        url = '/imports/mappings/view'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        response = app.get(
            url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params={})

        assert response.status_code == 200


    def test_get_schemas_not_authenticated(self, app):
        url = '/imports/mappings/view'

        response = app.get(
            url,
            xhr=True,
            status='*')

        assert response.status_code == 401

    @pytest.mark.parametrize('group', [ADMINISTRATOR, MANAGER])
    def test_get_all_schemas(self, app, group):
        url = '/imports/schemas'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        response = app.get(
            url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params={})

        assert response.status_code == 200

    @pytest.mark.parametrize('group', [REVIEWER, MEMBER])
    def test_get_all_schemas_not_allowed(self, app, group):
        url = '/imports/schemas'

        environ = make_environ(userid=USERID, groups=[group])
        csrf_token = get_csrf_token(app, environ)

        response = app.get(
            url,
            extra_environ=environ,
            status='*',
            headers={
                'X-CSRF-Token': csrf_token,
                'X-REQUESTED-WITH': str('XMLHttpRequest')
            },
            params={})

        assert response.status_code == 403

    def test_get_all_schemas_not_authenticated(self, app):
        url = '/imports/schemas'

        response = app.get(
            url,
            xhr=True,
            status='*')

        assert response.status_code == 401
