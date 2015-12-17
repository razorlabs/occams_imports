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
        from occams_imports.views.mappings import get_all_schemas as view

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
        from occams_imports.views.mappings import occams_direct as view

        return view(*args, **kw)

    def test_occams_direct(self, req):
        response = self._call_fut(None, req)

        assert response == {}


class TestOccamsImputation:
    def _call_fut(self, *args, **kw):
        from occams_imports.views.mappings import occams_imputation as view

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
        from occams_imports.views.mappings import mappings_direct_map as view

        return view(*args, **kw)

    def test_mappings_direct_map(self, req, db_session):
        """
        Test Direct Mapping
        """
        from occams_imports import models
        req.json = {
            u'confidence': 1,
            u'selected': {u'label': u'',
                          u'variable': u'question'},
            u'selected_target': {u'choices': [{u'label': u'Always',
                                               u'mapped': u'0',
                                               u'name': u'0'},
                                              {u'label': u'Never',
                                               u'mapped': u'1',
                                               u'name': u'1'}],
                                 u'label': u'',
                                 u'variable': u'ucsd_question'},
            u'site': {u'name': u'demographics',
                      u'publish_date': u'2015-01-01'},
            u'target': {u'name': u'ucsd_demographics',
                        u'publish_date': u'2015-01-01'}
        }

        response = self._call_fut(None, req)

        assert u'id' in response

        mapping = db_session.query(models.Mapping).one()

        assert mapping.confidence == 1
        assert mapping.type == u'direct'
        assert mapping.study.name == u'drsc'
        assert mapping.mapped_attribute.name == u'ucsd_question'
        assert mapping.logic['source_attribute'] == u'question'


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
        from occams_imports.views.mappings import mappings_imputations_map as view

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
        assert imputation.confidence == 1
        assert imputation.description == u'Test Description'
        assert imputation.mapped_attribute.name == u'ucsd_question'
        assert imputation.logic['forms'] == [[u'demographics', u'question']]
