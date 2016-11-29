"""
Contains long-running tasks that cannot interrupt the user experience.

Tasks in this module will be run in a separate process so the user
can continue to use the application and view the mapping results at a
later time.
"""
import shutil
import tempfile
import json
import six
import uuid

from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_imports import models

from occams_forms.renderers import apply_data
from occams.celery import app, Session, with_transaction


@app.task(name='apply_direct_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_direct_mappings(task):
    # get all the direct mappings for processing
    mappings = (
        Session.query(models.Mapping)
        .filter_by(type=u'direct').all()
    )

    default_state = (
        Session.query(datastore.State)
        .filter_by(name='pending-entry')
        .one()
    )

    redis = app.redis
    total_mappings = len(mappings)

    count = 0

    mappings_id = six.text_type(str(uuid.uuid4()))

    redis.hmset(mappings_id, {
        'count': count,
        'total': total_mappings
    })

    for mapping in mappings:

        source_schema_name = mapping.logic['source_schema']
        source_schema_publish_date = mapping.logic['source_schema_publish_date']
        source_variable = mapping.logic['source_variable']

        target_schema_name = mapping.logic['target_schema']
        target_schema_publish_date = mapping.logic['target_schema_publish_date']
        target_variable = mapping.logic['target_variable']

        # get records that have a matching schema for source schema
        records = (
            Session.query(models.SiteData)
            .filter(
                models.SiteData.data['form_name'].astext == source_schema_name
            )
            .filter(
                models.SiteData.data['form_publish_date'].astext == source_schema_publish_date
            ).all()
        )

        for record in records:
            pid = record.data['pid']
            collect_date = record.data['collect_date']

            patient = (
                Session.query(studies.Patient)
                .filter_by(pid=pid)
                .one()
            )

            target_schema = (
                Session.query(datastore.Schema)
                .filter_by(name=target_schema_name)
                .filter_by(publish_date=target_schema_publish_date)
            ).one()

            # if the target schema already exists we want to add data
            # to the schema rather than creating a new entity
            entity_exists = False
            for item in patient.entities:
                if item.schema.name == target_schema_name and \
                   item.schema.publish_date.isoformat() == \
                   target_schema_publish_date:
                    entity = item
                    entity_exists = True
                    break

            if not entity_exists:
                entity = datastore.Entity(
                    schema=target_schema,
                    collect_date=collect_date,
                    state=default_state
                )

                patient.entities.add(entity)

            if mapping.logic['choices_mapping']:
                # add handling if there is no value to map
                source_key = record.data.get(source_variable)

                payload = {target_variable: source_key}
                upload_dir = tempfile.mkdtemp()
                apply_data(Session, entity, payload, upload_dir)
                shutil.rmtree(upload_dir)

            else:
                # non-choices processing
                source_key = record.data.get(source_variable)
                payload = {target_variable: source_key}
                upload_dir = tempfile.mkdtemp()
                apply_data(Session, entity, payload, upload_dir)
                shutil.rmtree(upload_dir)

        redis.hincrby(mappings_id, 'count')

        data = redis.hgetall(mappings_id)
        # redis-py returns everything as string, so we need to clean it
        for key in ('count', 'total'):
            data[key] = int(data[key])
        redis.publish('direct', json.dumps(data))


@app.task(name='apply_imputation_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_imputation_mappings(task):
    redis = app.redis
    total_mappings = 1000

    count = 0

    mappings_id = six.text_type(str(uuid.uuid4()))

    redis.hmset(mappings_id, {
        'count': count,
        'total': total_mappings
    })

    for i in xrange(1000):

        redis.hincrby(mappings_id, 'count')

        data = redis.hgetall(mappings_id)
        # redis-py returns everything as string, so we need to clean it
        for key in ('count', 'total'):
            data[key] = int(data[key])
        redis.publish('imputation', json.dumps(data))
