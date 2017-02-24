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
        '%s_%s' % (schema_a_upload.schema.name, a.name)
        for a in schema_a_upload.schema.iterleafs()
    ]
    expected_columns += [
        '%s_%s' % (schema_b_upload.schema.name, a.name)
        for a in schema_b_upload.schema.iterleafs()
    ]

    assert set(expected_columns) < set(frame.columns)
