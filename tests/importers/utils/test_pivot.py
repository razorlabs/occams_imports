import factory


CONTEXT_COLUMNS = ['pid', 'visit', 'collect_date']
DUMMY_VISIT_TYPES = ['wk1', 'wk2', 'wk3', 'wk5']


class AssessmentTypeARecord(factory.Factory):
    pid = factory.Faker('uuid4')
    visit = factory.Faker('random_element', elements=DUMMY_VISIT_TYPES)
    collect_date = factory.Faker('date_time_this_year')
    foo = factory.Faker('word')
    bar = factory.Faker('pyint')


class AssessmentTypeBRecord(factory.Factory):
    pid = factory.Faker('uuid4')
    visit = factory.Faker('random_element', elements=DUMMY_VISIT_TYPES)
    collect_date = factory.Faker('date_time_this_year')
    baz = factory.Faker('word')
    caz = factory.Faker('pyint')


def populate_upload(upload, factory_class):
    """
    Generates a single dummy column from the upload file
    """

    import unicodecsv as csv
    import io

    with io.BytesIO() as buffer:
        fieldnames = CONTEXT_COLUMNS + upload.schema.attributes.keys()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(factory.build(dict, FACTORY_CLASS=factory_class))
        upload.project_file = buffer.getvalue()


def test_dummy(
        db_session,
        schema_factory,
        attribute_factory,
        study_factory,
        upload_factory
        ):
    """
    It should be able to join two uploads into a single data frame
    """

    from occams_imports.importers.utils.pivot import load_project_frame

    study = study_factory()

    schema_a_upload = upload_factory.create(
        study=study,
        schema__attributes={
            'foo': attribute_factory.create(name='foo', type='string'),
            'bar': attribute_factory.create(name='bar', type='number'),
        }
    )

    schema_b_upload = upload_factory.create(
        study=study,
        schema__attributes={
            'baz': attribute_factory.create(name='baz', type='string'),
            'caz': attribute_factory.create(name='caz', type='number'),
        }
    )

    populate_upload(schema_a_upload, AssessmentTypeARecord)
    populate_upload(schema_b_upload, AssessmentTypeBRecord)
    db_session.flush()

    frame = load_project_frame(db_session, study.name)

    expected_columns = [
        '_'.join([study.name, schema_a_upload.schema.name, a.name])
        for a in schema_a_upload.schema.iterleafs()
    ]
    expected_columns += [
        '_'.join([study.name, schema_b_upload.schema.name, a.name])
        for a in schema_b_upload.schema.iterleafs()
    ]
    assert set(expected_columns) < set(frame.columns)


def test_populate_project(
        db_session,
        study_factory,
        schema_factory,
        patient_factory,
        attribute_factory,
        site_factory):

    import pandas as pd
    import numpy as np

    from occams_studies import models as studies
    from occams_imports.importers.utils.pivot import populate_project

    target_project = study_factory()
    target_site = site_factory(name=target_project.name)

    target_schema = schema_factory()

    target_schema = schema_factory.create(
        attributes={
            'gender': attribute_factory.create(name='gender', type='number'),
            'collect_date': attribute_factory.create(
                name='collect_date', type='date'),
        }
    )

    target_project.schemata.add(target_schema)

    pid1 = patient_factory(site=target_site)
    pid2 = patient_factory(site=target_site)
    pid3 = patient_factory(site=target_site)

    data_dict = {
        'pid': [
            pid1.pid,
            pid2.pid,
            pid3.pid
        ],
        'visit': ['week4', 'week5', 'week6']
    }

    target_demographics = '{}_{}_gender'.format(
        target_project.name, target_schema.name)
    target_collecy_date = '{}_{}_collect_date'.format(
        target_project.name, target_schema.name)

    data_dict[target_demographics] = [0, 1, np.nan]
    data_dict[target_collecy_date] = ['2017-01-01', '2017-01-02', '2017-01-01']

    consolidated_frame = pd.DataFrame(data_dict)

    populate_project(
        db_session,
        target_project.name,
        consolidated_frame
    )

    patient1 = (
        db_session.query(studies.Patient)
        .filter_by(pid=pid1.pid)
        .one()
    )

    patient2 = (
        db_session.query(studies.Patient)
        .filter_by(pid=pid2.pid)
        .one()
    )

    patient3 = (
        db_session.query(studies.Patient)
        .filter_by(pid=pid3.pid)
        .one()
    )

    assert len(patient1.entities) == 1
    for entity in patient1.entities:
        assert entity['gender'] == 0
        assert entity['collect_date'] == '2017-01-01'

    assert len(patient2.entities) == 1
    for entity in patient2.entities:
        assert entity['gender'] == 1
        assert entity['collect_date'] == '2017-01-02'

    assert len(patient3.entities) == 1
    for entity in patient3.entities:
        assert entity['gender'] is None
        assert entity['collect_date'] == '2017-01-01'
