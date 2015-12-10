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
