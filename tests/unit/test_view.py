# flake8: noqa

import pytest


@pytest.yield_fixture
def check_csrf_token(config):
    import mock
    name = 'occams_imports.views.view.check_csrf_token'
    with mock.patch(name) as patch:
        yield patch


class TestIndex:
    def _call_fut(self, *args, **kw):
        from occams_imports.views.view import index as view

        return view(*args, **kw)

    def test_index(self, req):
        response = self._call_fut(None, req)

        assert response == {}


class TestGetSchemas:
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
                    type=u'choice',
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

        schema2 = datastore.Schema(
            name=u'ucsd_demographics',
            title=u'ucsd_demographics',
            publish_date=u'2015-01-01',
            attributes={
                'ucsd_question': datastore.Attribute(
                    name=u'ucsd_question',
                    title=u'ucsd_question',
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
        drsc.schemata.add(schema2)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.view import get_schemas as view

        return view(*args, **kw)

    def test_get_schemas(self, req, db_session):
        """
        Test if mapping is returned from view
        """
        from occams_imports.views.mappings import mappings_direct_map

        req.json = {
            "source_variable": "question",
            "target_schema_publish_date": "2015-01-01",
            "choices_mapping": [{"mapped": "0", "name": "0"},
                                {"mapped": "1", "name": "0"}],
            "source_schema_publish_date": "2015-01-01",
            "target_schema": "ucsd_demographics",
            "target_variable": "ucsd_question",
            "source_schema": "demographics"}

        mappings_direct_map(None, req)

        response = self._call_fut(None, req)

        row = response['rows'][0]

        assert row['study'] == u'DRSC'
        assert row['study_form'] == u'demographics'
        assert row['target_form'] == u'ucsd_demographics'


class TestDeleteMappings:
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
                    type=u'choice',
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

        schema2 = datastore.Schema(
            name=u'ucsd_demographics',
            title=u'ucsd_demographics',
            publish_date=u'2015-01-01',
            attributes={
                'ucsd_question': datastore.Attribute(
                    name=u'ucsd_question',
                    title=u'ucsd_question',
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
        drsc.schemata.add(schema2)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.view import delete_mappings as view

        return view(*args, **kw)

    def test_delete_mappings(self, req, db_session):
        """
        Test if a selected mapping is deleted
        """
        from sqlalchemy.sql import exists

        from occams_imports import models
        from occams_imports.views.mappings import mappings_direct_map

        req.json = {
            "source_variable": "question",
            "target_schema_publish_date": "2015-01-01",
            "choices_mapping": [{"mapped": "0", "name": "0"},
                                {"mapped": "1", "name": "0"}],
            "source_schema_publish_date": "2015-01-01",
            "target_schema": "ucsd_demographics",
            "target_variable": "ucsd_question",
            "source_schema": "demographics"}

        mappings_direct_map(None, req)

        mapping = db_session.query(models.Mapping).one()

        req.json = {
            'mapped_delete':
                [
                    {'deleteRow': True, 'mappedId': mapping.id}
                ]
        }

        self._call_fut(None, req)

        mapping_exists = db_session.query(
            exists().where(models.Mapping.id == mapping.id)).scalar()

        assert mapping_exists is False


class TestGetSchemasMapped:
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
                    type=u'choice',
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

        schema2 = datastore.Schema(
            name=u'ucsd_demographics',
            title=u'ucsd_demographics',
            publish_date=u'2015-01-01',
            attributes={
                'ucsd_question': datastore.Attribute(
                    name=u'ucsd_question',
                    title=u'ucsd_question',
                    type=u'choice',
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
        drsc.schemata.add(schema2)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.view import get_schemas_mapped as view

        return view(*args, **kw)

    def test_get_schemas_mapped(self, req, db_session):
        """
        Test if a inserted map is returned to view
        """
        from occams_imports import models
        from occams_imports.views.mappings import mappings_direct_map

        req.json = {
            "source_variable": "question",
            "target_schema_publish_date": "2015-01-01",
            "choices_mapping": [{"mapped": "0", "name": "0"},
                                {"mapped": "1", "name": "0"}],
            "source_schema_publish_date": "2015-01-01",
            "target_schema": "ucsd_demographics",
            "target_variable": "ucsd_question",
            "source_schema": "demographics"}

        mappings_direct_map(None, req)

        mapping = db_session.query(models.Mapping).one()

        req.params = {'id': mapping.id}

        response = self._call_fut(None, req)

        row = response['mappings_form_rows'][0]

        assert row['description'] == u'question'
        assert row['study'] == u'DRSC'
        assert row['type'] == u'direct'
