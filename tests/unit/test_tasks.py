"""Tests for imports pipelines."""

import pytest

SITEDATA = {
    'site': 'ucsd',
    'pid': '1234',
    'enrollment': '',
    'enrollment_ids': '',
    'visit_cycles': '595(-1)',
    'visit_id': '84',
    'visit_date': '2013-02-05',
    'form_name': 'PatientRegistrationAndDemographics',
    'form_publish_date': '2013-02-25',
    'state': 'complete',
    'collect_date': '2011-01-04',
    'not_done': '0',
    'birthmonth': '6',
    'birthyear': '35',
    'gender': '2',
    'ethn': '2',
    'race_11': '0',
    'race_10': '0',
    'race_1': '0',
    'race_3': '0',
    'race_2': '0',
    'race_5': '0',
    'race_4': '0',
    'race_7': '1',
    'race_6': '0',
    'race_9': '0',
    'race_8': '0',
    'raceotr': 'elf',
    'lang': '1',
    'lanotr': '',
    'hivrisk_1': '1',
    'hivrisk_3': '0',
    'hivrisk_2': '0',
    'hivrisk_5': '0',
    'hivrisk_4': '0',
    'hivrisk_6': '0',
    'hivotr': '4',
    'edu': '5',
    'income': '6',
    'relationship': '5',
    'employment': '1'
}


class TestDirectMappingPipeline:
    """Test Direct Mapping Pipeline."""

    def _call_fut(self, *args, **kw):
        """Function under test."""
        from occams_imports.tasks import get_target_value as view

        return view(*args, **kw)

    def test_get_attributes_value_value(self):
        """Should return the value to be matched."""
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies
        from occams_imports import models

        study = studies.Study(
            name=u'UCSD',
            title=u'UCSD',
            short_title=u'UCSD',
            code=u'001',
            consent_date=date(2015, 01, 01)
        )

        schema = datastore.Schema(
            name=u'PatientRegistrationAndDemographics',
            title=u'PatientRegistrationAndDemographics',
            publish_date=date(2013, 02, 25),
            attributes={
                'birthyear': datastore.Attribute(
                    name=u'birthyear',
                    title=u'birthyear',
                    type=u'number',
                    order=0
                )}
        )

        record = models.SiteData(
            schema=schema,
            study=study,
            data=SITEDATA
        )

        source_variable = u'birthyear'

        choices_mapping = []
        target_value = self._call_fut(choices_mapping, record,
                                      source_variable, schema)

        assert target_value == '35'

    def test_get_attributes_choice_to_value(self):
        """Should return the title of the source choice."""
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies
        from occams_imports import models

        study = studies.Study(
            name=u'UCSD',
            title=u'UCSD',
            short_title='uUCSD',
            code=u'001',
            consent_date=date(2015, 01, 01)
        )

        schema = datastore.Schema(
            name=u'PatientRegistrationAndDemographics',
            title=u'PatientRegistrationAndDemographics',
            publish_date=date(2013, 02, 25),
            attributes={
                'race_1': datastore.Attribute(
                    name=u'race_1',
                    title=u'race_1',
                    type=u'choice',
                    order=0,
                    choices={
                        u'0': datastore.Choice(
                            name=u'0',
                            title=u'elf',
                            order=0
                        ),
                        u'1': datastore.Choice(
                            name=u'1',
                            title=u'halfling',
                            order=1
                        )
                    }
                )}
        )

        record = models.SiteData(
            schema=schema,
            study=study,
            data=SITEDATA
        )

        source_variable = u'race_1'

        choices_mapping = []
        target_value = self._call_fut(choices_mapping, record,
                                      source_variable, schema)

        assert target_value == u'elf'

    def test_get_attributes_choice_to_choice(self):
        """Should return the mapped key of the target variable."""
        from datetime import date

        from occams_datastore import models as datastore
        from occams_studies import models as studies
        from occams_imports import models

        study = studies.Study(
            name='UCSD',
            title='UCSD',
            short_title='UCSD',
            code='001',
            consent_date=date(2015, 01, 01)
        )

        schema = datastore.Schema(
            name='PatientRegistrationAndDemographics',
            title='PatientRegistrationAndDemographics',
            publish_date=date(2013, 02, 25),
            attributes={
                'race_1': datastore.Attribute(
                    name=u'race_1',
                    title=u'race_1',
                    type=u'choice',
                    order=0,
                    choices={
                        u'0': datastore.Choice(
                            name=u'0',
                            title=u'elf',
                            order=0
                        ),
                        u'1': datastore.Choice(
                            name=u'1',
                            title=u'halfling',
                            order=1
                        )
                    }
                )}
        )

        record = models.SiteData(
            schema=schema,
            study=study,
            data=SITEDATA
        )

        source_variable = u'race_1'

        choices_mapping = [{'source': u'0', 'target': u'4'}]
        target_value = self._call_fut(choices_mapping, record,
                                      source_variable, schema)

        assert target_value == u'4'


class TestDirectMappingGetErrors:
    """Test Direct Mapping Pipeline."""

    def _call_fut(self, *args, **kw):
        """Function under test."""
        from occams_imports.tasks import get_errors as view

        return view(*args, **kw)

    def test_get_errors(self, db_session):
        """Should return errors."""
        from datetime import date

        from occams_datastore import models as datastore

        target_schema = datastore.Schema(
            name=u'Demographics',
            title=u'Demographics',
            publish_date=date(2013, 02, 25),
            attributes={
                'yob': datastore.Attribute(
                    name=u'yob',
                    title=u'yob',
                    type=u'number',
                    order=0
                )}
        )

        db_session.add(target_schema)
        db_session.flush()

        target_variable = u'yob'
        target_value = u'test_string'

        errors = self._call_fut(db_session, target_schema,
                                target_variable, target_value)

        assert errors[0] == u'Not a valid decimal value'

    def test_get_errors_empty(self, db_session):
        """Should return no errors."""
        from datetime import date

        from occams_datastore import models as datastore

        target_schema = datastore.Schema(
            name=u'Demographics',
            title=u'Demographics',
            publish_date=date(2013, 02, 25),
            attributes={
                'yob': datastore.Attribute(
                    name=u'yob',
                    title=u'yob',
                    type=u'number',
                    order=0
                )}
        )

        db_session.add(target_schema)
        db_session.flush()

        target_variable = u'yob'
        target_value = u'25'

        errors = self._call_fut(db_session, target_schema,
                                target_variable, target_value)

        assert errors == []
