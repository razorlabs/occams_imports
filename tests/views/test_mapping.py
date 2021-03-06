# flake8: noqa

import pytest


@pytest.yield_fixture
def check_csrf_token(config):
    import mock
    name = 'occams_imports.views.mapping.check_csrf_token'
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
            is_randomized=False
        )

        schema1 = datastore.Schema(
            name=u'demographics',
            title=u'demographics',
            publish_date=date.today(),
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
            name=u'demographics2',
            title=u'demographics2',
            publish_date=date.today(),
            attributes={
                'question': datastore.Attribute(
                    name=u'question',
                    title=u'question',
                    type=u'string',
                    order=0)
            }
        )
        drsc.schemata.add(schema1)
        drsc.schemata.add(schema2)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mapping import get_all_schemas as view

        return view(*args, **kw)

    def test_get_all_schemas(self, req, db_session):
        """
        Only one schema should be returned eventhough multiple studies have
        the same schema associated
        """
        response = self._call_fut(None, req)

        assert len(response['forms']) == 2
        assert response['forms'][0]['name'] == u'demographics'


class TestOccamsDirect:
    def _call_fut(self, *args, **kw):
        from occams_imports.views.mapping import occams_direct as view

        return view(*args, **kw)

    def test_occams_direct(self, req):
        response = self._call_fut(None, req)

        assert response == {}


class TestOccamsImputation:
    def _call_fut(self, *args, **kw):
        from occams_imports.views.mapping import occams_imputation as view

        return view(*args, **kw)

    def test_occams_imputation(self, req):
        response = self._call_fut(None, req)

        assert response == {}


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
        from occams_imports.views.mapping import schemas as view

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
        from occams_imports.views.mapping import get_attributes as view

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
        drsc.schemata.add(schema1)
        db_session.add(drsc)
        db_session.flush()

    def _call_fut(self, *args, **kw):
        from occams_imports.views.mapping import get_choices as view

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


class TestDirectMapping:
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
        from occams_imports.views.mapping import mappings_direct_map as view

        return view(*args, **kw)

    def test_mappings_direct_map(self, req, db_session):
        """
        Test Direct Mapping
        """
        from occams_imports import models
        req.json = {
            "source_variable": "question",
            "target_schema_publish_date": "2015-01-01",
            "choices_mapping": [{"mapped": "0", "name": "0"},
                                {"mapped": "1", "name": "0"}],
            "source_schema_publish_date": "2015-01-01",
            "target_schema": "ucsd_demographics",
            "target_variable": "ucsd_question",
            "source_schema": "demographics"}

        response = self._call_fut(None, req)

        assert u'id' in response

        mapping = db_session.query(models.Mapping).one()

        assert mapping.type == u'direct'
        assert mapping.study.name == u'drsc'
        assert mapping.logic['target_variable'] == u'ucsd_question'
        assert mapping.logic['source_variable'] == u'question'


class TestImputationMapping:
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
        from occams_imports.views.mapping import mappings_imputations_map as view

        return view(*args, **kw)

    def test_mappings_imputation_map(self, req, db_session):
        """
        Test Imputations Mapping
        """
        from occams_imports import models
        import mock

        req.json = {u'condition': u'ALL',
                    u'confidence': u'1',
                    u'description': u'Test Description',
                    u'groups': [{u'conversions': [{u'byValue': False,
                                                   u'byVariable': True,
                                                   u'value': {u'attribute': {u'hasChoices': True,
                                                                             u'name': u'question',
                                                                             u'title': u'question',
                                                                             u'type': u'choice'},
                                                              u'schema': {u'name': u'demographics',
                                                                          u'publish_date': u'2015-01-01'}}},
                                {u'byValue': True,
                                 u'byVariable': False,
                                 u'operator': u'MUL',
                                 u'value': u'100'}],
                                 u'conversionsLength': 2,
                                 u'hasMultipleConversions': True,
                                 u'logic': {u'hasImputations': True,
                                            u'hasMultipleImputations': False,
                                            u'imputations': [{u'operator': u'',
                                                              u'value': u'100'}],
                                            u'imputationsLength': 1}}],
                    u'groupsLength': 1,
                    u'hasMultipleGroups': False,
                    u'target': {u'attribute': {u'hasChoices': True,
                                               u'name': u'ucsd_question',
                                               u'title': u'ucsd_question',
                                               u'type': u'choice'},
                                u'schema': {u'name': u'ucsd_demographics',
                                            u'publish_date': u'2015-01-01'}},
                    u'targetChoice': {u'name': u'1', u'title': u'never', u'toString': u'1 - never'}}

        req.route_path = mock.MagicMock(return_value=u'test_path')

        self._call_fut(None, req)

        imputation = db_session.query(models.Mapping).one()

        assert imputation.study.title == u'DRSC'
        assert imputation.type == u'imputation'
        assert imputation.description == u'Test Description'
        assert imputation.logic['forms'] == [[u'demographics', u'question']]


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
        from occams_imports.views.mapping import mappings as view
        return view(*args, **kw)

    def test_get_schemas(self, config, req, db_session):
        """
        Test if mapping is returned from view
        """
        from occams_imports.views.mapping import mappings_direct_map

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

        config.testing_securitypolicy(permissive=False)
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
        from occams_imports.views.mapping import delete_mappings as view

        return view(*args, **kw)

    def test_delete_mappings(self, req, db_session):
        """
        Test if a selected mapping is deleted
        """
        from sqlalchemy.sql import exists

        from occams_imports import models
        from occams_imports.views.mapping import mappings_direct_map

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
        from occams_imports.views.mapping import get_schemas_mapped as view

        return view(*args, **kw)

    def test_get_schemas_mapped(self, req, db_session):
        """
        Test if a inserted map is returned to view
        """
        from occams_imports import models
        from occams_imports.views.mapping import mappings_direct_map

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

        req.matchdict['mapping'] = mapping.id

        response = self._call_fut(None, req)

        row = response['mappings_form_rows'][0]

        assert row['description'] == u'question'
        assert row['study'] == u'DRSC'
        assert row['type'] == u'direct'


def test_convert_logic(db_session, schema_factory, attribute_factory):
    """
    Test if logic converts from server side to client-side
    """
    import datetime
    from occams_imports.views.mapping import convert_logic

    target_schema = schema_factory.create(
        name=u'ARVLog',
        publish_date=datetime.date(2014,07,13)
    )

    attribute_factory.create(
        schema=target_schema,
        name=u'arvname',
        title=u'ARV',
        type=u'choice'
    )

    server_logic = {
        u'condition': u'ALL',


        u'forms': [[u'Demographics', u'employment']],


        u'groups': [{u'conversions': [{u'byValue': False,
                                       u'byVariable': True,
                                       u'value': {u'attribute': {u'hasChoices': True,
                                                                 u'name': u'employment',
                                                                 u'title': u'Employment',
                                                                 u'type': u'choice'},
                                                  u'schema': {u'name': u'Demographics',
                                                              u'publish_date': u'2015-10-01'}}}],
                      u'conversionsLength': 1,
                      u'hasMultipleConversions': False,
                      u'logic': {u'hasImputations': True,
                                 u'hasMultipleImputations': False,
                                 u'imputations': [{u'operator': u'EQ',
                                                   u'value': u'1'}],
                                 u'imputationsLength': 1}}],

        u'target_choice': {u'name': u'1',
                            u'title': u'Retrovir',
                            u'toString': u'1 - Retrovir'},

        u'target_schema': u'ARVLog',

        u'target_variable': u'arvname'
    }

    expected_logic = {

         u'condition': u'ALL',
         u'description': u'',
         u'groups': [{u'conversions': [{u'byValue': False,
                                        u'byVariable': True,
                                        u'value': {u'attribute': {u'hasChoices': True,
                                                                  u'name': u'employment',
                                                                  u'title': u'Employment',
                                                                  u'type': u'choice'},
                                                   u'schema': {u'name': u'Demographics',
                                                               u'publish_date': u'2015-10-01'}}}],
                      u'conversionsLength': 1,
                      u'hasMultipleConversions': False,
                      u'logic': {u'hasImputations': True,
                                 u'hasMultipleImputations': False,
                                 u'imputations': [{u'operator': u'EQ',
                                                   u'value': u'1'}],
                                 u'imputationsLength': 1}}],
         u'groupsLength': 1,
         u'hasMultipleGroups': False,


         u'target': {u'attribute': {u'hasChoices': True,
                                    u'name': u'arvname',
                                    u'title': u'ARV',
                                    u'type': u'choice'},
                     u'schema': {u'name': u'ARVLog', u'publish_date': u'2014-07-13'}},

         u'targetChoice': {u'name': u'1',
                           u'title': u'Retrovir',
                           u'toString': u'1 - Retrovir'}
    }

    logic = convert_logic(db_session, server_logic)

    assert logic == expected_logic
