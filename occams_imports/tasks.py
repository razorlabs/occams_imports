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

from webob.multidict import MultiDict

from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_imports import models

from occams_forms.renderers import apply_data, make_form
from occams.celery import app, Session, with_transaction

from .importers import imputation


def get_target_value(choices_mapping, record, source_variable, source_schema):
    """Return the target value to be mapped.

    :param choices_mapping: a list of mapping dicts ({'source': 2 'target': 3})
    :param record: an occams_imports SiteData object
    :param source_variable: string name of the source variable
    :param source_schema: an occams Schema Object

    rtype: the key to be mapped if a choice to choice map or a value for all
           other mappings
    """
    target_value = None
    # Source choice to target choice mapping.
    # The target value is the key/name of the source choice
    if choices_mapping:
        source_key = record.data.get(source_variable)

        for logic in choices_mapping:
            if logic['source'] == source_key:
                target_value = logic['target']
                break

    else:
        # Source choice to target value mapping.
        # We need to query for the source attribute to obtain the
        # title of the source choice.  This is because the title of the
        # choice does not exist in the mapped data on the server.
        source_attribute = source_schema.attributes[source_variable]

        if source_attribute.type == 'choice':
            source_key = record.data.get(source_variable)
            target_value = source_attribute.choices[source_key].title

        # Source value to target value mapping
        else:
            target_value = record.data.get(source_variable)

    return target_value


def get_errors(db_session, target_schema,
               target_variable, target_value):
    """Return wtforms errors.

    :param db_session: SQL Alchemy session
    :param target_schema: an occams Schema object
    :param target_variable: string name of the target variable
    :rtype: list of wtforms errors
    """
    Form = make_form(db_session, target_schema)
    validate_form = \
        Form(MultiDict([(target_variable, target_value)]))
    validate_form.validate()
    # We only need the validation for just the target variable
    target_has_errors = getattr(
        validate_form, target_variable
    ).errors

    return target_has_errors


def add_drsc_entity(db_session, patient, target_schema_name,
                    target_schema, collect_date):
    """Add DRSC entity if required.

    If the target schema entity exists we want to add mapped data
    to the exisiting entity rather than create a new entity
    Need a default state to retrieve OCCAMS entities

    :param db_session: SQLAlchemy session object
    :param patient: patient mapping will be applied to
    :param target_schema_name: name of the target schema
    :param target_schema: occams Schema object of the target schema
    :collect_date: collect date of the entity in iso format
    :rtype: Entity
    """
    entity_exists = False
    for item in patient.entities:
        if item.schema.name == target_schema_name:
            entity = item
            entity_exists = True
            return entity

    if not entity_exists:
        default_state = (
            db_session.query(datastore.State)
            .filter_by(name='complete')
            .one()
        )
        entity = datastore.Entity(
            schema=target_schema,
            collect_date=collect_date,
            state=default_state
        )

        patient.entities.add(entity)

        return entity


@app.task(name='apply_direct_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_direct_mappings(task):
    """ Direct mappings pipeline.

    From a high level, this function walks the approved mappings from the
    mappings table, gets patient records matching the source schema, for
    each patient record determines if the target schema exists, applies the
    mapping, validates the mapping, and inserts the mapped data into
    the target variable/schema.

    If the source value is not valid with the target attribute wtforms
    validator, the entry is logged and the mapping does not occur.  If no
    target choice is found in the choices mapping, the entry is logged and
    the mapping does not occur.

    If a schema already exists, the variable will be overwritten.  An
    improvement may be to log the entry if the variable has been mapped
    and do not overwrite.

    Currently the method supports 3 direct mappings types:

    * Source Choice to Target Choice
    * Source Choice to Target Value
    * Source Value to Target Value

    :param task: celery task object
    :rtype: count and total is broadcast to the 'direct' redis channel,
    currently the logs are not returned
    """
    # Retrieve mappings in 'approved' status

    # TODO filter by a particular project
    mappings = (
        Session.query(models.Mapping)
        .filter_by(type=u'direct')
        .filter_by(status_id=3).all()
    )

    redis = app.redis

    total_mappings = len(mappings)
    count = 0
    log = []

    mappings_id = six.text_type(str(uuid.uuid4()))

    # Set initial values for the redis hash
    redis.hmset(mappings_id, {
        'count': count,
        'total': total_mappings
    })

    for mapping in mappings:

        source_schema_name = mapping.logic['source_schema']
        source_schema_publish_date = \
            mapping.logic['source_schema_publish_date']
        source_variable = mapping.logic['source_variable']

        target_schema_name = mapping.logic['target_schema']
        target_schema_publish_date = \
            mapping.logic['target_schema_publish_date']
        target_variable = mapping.logic['target_variable']

        # Get patient sitedata records matching the source schema
        records = (
            Session.query(models.SiteData)
            .filter(
                models.SiteData.data['form_name'].astext == source_schema_name
            )
            .filter(
                models.SiteData.data['form_publish_date'].astext ==
                source_schema_publish_date
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

            source_schema = (
                Session.query(datastore.Schema)
                .filter_by(name=source_schema_name)
                .filter_by(publish_date=source_schema_publish_date)
            ).one()

            entity = add_drsc_entity(Session, patient, target_schema_name,
                                     target_schema, collect_date)

            target_value = get_target_value(mapping.logic['choices_mapping'],
                                            record, source_variable,
                                            source_schema)

            if target_value:
                target_has_errors = get_errors(Session, target_schema,
                                               target_variable, target_value)

                if target_has_errors:
                    log.append({
                        'DRSC Variable': target_variable,
                        'Message': ', '.join(target_has_errors)
                    })

                else:
                    payload = {target_variable: target_value}
                    upload_dir = tempfile.mkdtemp()
                    apply_data(Session, entity, payload, upload_dir)
                    shutil.rmtree(upload_dir)

            # No target value. This occurs if there is no target choice
            # in the source choice to target choice mapping.
            else:
                log.append({
                    'DRSC Variable': target_variable,
                    'Message': u'No matching mapping in choices_mapping'
                })

        redis.hincrby(mappings_id, 'count')

        data = redis.hgetall(mappings_id)
        # redis-py returns everything as string, so we need to clean it
        for key in ('count', 'total'):
            data[key] = int(data[key])
        redis.publish('direct', json.dumps(data))


@app.task(name='apply_imputation_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_imputation_mappings(task):
    imputation.apply_all(Session, app.redis)
