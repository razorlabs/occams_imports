import pytest


@pytest.yield_fixture
def check_csrf_token(config):
    import mock
    name = 'occams_imports.views.mappings.check_csrf_token'
    with mock.patch(name) as patch:
        yield patch


class TestGetAllSchemas:
    @pytest.fixture(autouse=True)
    def populate(self, db_session):
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies

        drsc = studies.Study(
            name=u'drsc',
            title=u'DRSC',
            short_title=u'dr',
            code=u'drs',
            consent_date=date.today(),
            start_date=date.today(),
            is_randomized=False
        )
        ucsd = studies.Study(
            name=u'ucsd',
            title=u'UCSD',
            short_title=u'ucsd',
            code=u'ucsd',
            consent_date=date.today(),
            start_date=date.today(),
            is_randomized=False
        )

        schema1 = datastore.Schema(
            name=u'test_schema1',
            title=u'test_schema1',
            publish_date=u'2015-01-01'
        )
        drsc.schemata.add(schema1)
        ucsd.schemata.add(schema1)
        db_session.add(drsc)
        db_session.add(ucsd)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mappings import get_all_schemas as view

        return view(*args, **kw)

    def test_get_all_schemas(self, req, db_session):
        """
        Only one schema should be returned eventhough multiple studies have
        the same schema associated
        """
        response = self._call_fut(None, req)

        assert len(response['forms']) == 1
        assert response['forms'][0]['name'] == u'test_schema1'


class TestSchemasSearchTerm:
    @pytest.fixture(autouse=True)
    def populate(self, db_session):
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies

        drsc = studies.Study(
            name=u'drsc',
            title=u'DRSC',
            short_title=u'dr',
            code=u'drs',
            consent_date=date.today(),
            start_date=date.today(),
            is_randomized=False
        )

        schema1 = datastore.Schema(
            name=u'test_schema1',
            title=u'test_schema1',
            publish_date=u'2015-01-01'
        )

        schema2 = datastore.Schema(
            name=u'demographics',
            title=u'demographics',
            publish_date=u'2015-01-01'
        )
        drsc.schemata.add(schema1)
        drsc.schemata.add(schema2)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mappings import get_schemas as view

        return view(*args, **kw)

    def test_get_schemas(self, req, db_session):
        """
        Only schema with matching search terms should be returned
        """
        from webob.multidict import MultiDict

        req.GET = MultiDict([('term', u'demo')])
        response = self._call_fut(None, req)

        assert len(response['schemata']) == 1
        assert response['schemata'][0]['name'] == u'demographics'


class TestAttributesSearchTerm:
    @pytest.fixture(autouse=True)
    def populate(self, db_session):
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies

        drsc = studies.Study(
            name=u'drsc',
            title=u'DRSC',
            short_title=u'dr',
            code=u'drs',
            consent_date=date.today(),
            start_date=date.today(),
            is_randomized=False
        )

        schema1 = datastore.Schema(
            name=u'demographics',
            title=u'demographics',
            publish_date=u'2015-01-01',
            attributes={
                'myfield': datastore.Attribute(
                    name=u'myfield',
                    title=u'My Field',
                    type=u'string',
                    order=0),
                'question': datastore.Attribute(
                    name=u'question',
                    title=u'question',
                    type=u'string',
                    order=0)}
        )
        drsc.schemata.add(schema1)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mappings import get_attributes as view

        return view(*args, **kw)

    def test_get_attributes(self, req, db_session):
        """
        Get attributes for schema
        """
        from webob.multidict import MultiDict

        req.GET = MultiDict([('term', u'quest'), ('schema', u'demographics')])
        response = self._call_fut(None, req)

        assert len(response['attributes']) == 1
        assert response['attributes'][0]['name'] == u'question'


class TestChoicesSearchTerm:
    @pytest.fixture(autouse=True)
    def populate(self, db_session):
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies

        drsc = studies.Study(
            name=u'drsc',
            title=u'DRSC',
            short_title=u'dr',
            code=u'drs',
            consent_date=date.today(),
            start_date=date.today(),
            is_randomized=False
        )

        schema1 = datastore.Schema(
            name=u'demographics',
            title=u'demographics',
            publish_date=u'2015-01-01',
            attributes={
                'question': datastore.Attribute(
                    name=u'question',
                    title=u'question',
                    type=u'string',
                    order=0,
                    choices={
                        u'0': datastore.Choice(
                            name=u'0',
                            title=u'always',
                            order=0
                        ),
                        u'1': datastore.Choice(
                            name=u'1',
                            title=u'never',
                            order=1
                        )
                    })}
        )
        drsc.schemata.add(schema1)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mappings import get_choices as view

        return view(*args, **kw)

    def test_get_choices(self, req, db_session):
        """
        Get choices for attribute
        """
        from webob.multidict import MultiDict

        req.GET = MultiDict(
            [('term', u'never'),
             ('attribute', u'question'),
             ('schema', u'demographics')])

        response = self._call_fut(None, req)

        assert len(response['choices']) == 1
        assert response['choices'][0]['title'] == u'never'
