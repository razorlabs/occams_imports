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
import operator

from sqlalchemy import asc

from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_imports import models

from occams_forms.renderers import apply_data
from occams.celery import app, Session, with_transaction
from celery.contrib import rdb


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

    operators_map = {
        'EQ': operator.eq,
        'NE': operator.ne,
        'LT': operator.lt,
        'LTE': operator.le,
        'GT': operator.gt,
        'GTE': operator.ge,
        'ADD': operator.add,
        'SUB': operator.sub,
        'MUL': operator.mul,
        'DIV': operator.div,
        'ANY': any,
        'ALL': all
    }

    log = []

    mappings_id = six.text_type(str(uuid.uuid4()))

    # get all the imputation mappings for processing
    mappings = (
        Session.query(models.Mapping)
        .filter_by(type=u'imputation').all()
    )

    total_mappings = len(mappings)
    count = 0

    redis.hmset(mappings_id, {
        'count': count,
        'total': total_mappings
    })

    for mapping in mappings:
        # change this to complete later
        # we are only processing items in a complete state
        if mapping.status.name == 'review':
            target_schema_name = mapping.logic['target_schema']
            target_variable = mapping.logic['target_variable']

            target_schema = (
                Session.query(datastore.Schema)
                .filter_by(name=target_schema_name)
            ).one()

            conversion_count = 0

            available_entities = True
            for group in mapping.logic['groups']:
                if available_entities:
                    match_rule = group['logic']

                else:
                    break

                for conversion in group['conversions']:
                    if conversion['byVariable']:
                        schema_name = conversion['value']['schema']['name']
                        schema_publish_date = conversion['value']['schema']['publish_date']
                        attribute = conversion['value']['attribute']['name']
                        attribute_type = conversion['value']['attribute']['type']

                        source_schema = (
                            Session.query(datastore.Schema)
                            .filter_by(name=schema_name)
                            .filter_by(publish_date=schema_publish_date)
                        ).one()

                        # get matching source schema records
                        records = (
                            Session.query(models.SiteData)
                            .filter(
                                models.SiteData.data['form_name'].astext == schema_name
                            )
                            .filter(
                                models.SiteData.data['form_publish_date'].astext == schema_publish_date
                            ).all()
                        )

                        if not records:
                            log.append({
                                'DRSC Variable': target_schema_name,
                                'Message': u'No patient entities available for schema: {}'.format(schema_name)
                            })

                            available_entities = False
                            break

                        running_totals = {}
                        for record in records:
                            pid = record.data['pid']
                            collect_date = record.data['collect_date']

                            running_totals[pid] = {
                                'total': int(record.data[attribute]),
                                'collect_date': collect_date
                            }

                        conversion_count += 1

                    else:
                        conversion_operator = conversion['operator']
                        conversion_operand = conversion['value']

                        for record in records:
                            pid = record.data['pid']
                            collect_date = record.data['collect_date']

                            running_totals[pid] = {
                                'total': operators_map[conversion_operator](running_totals[pid]['total'], int(conversion_operand)),
                                'collect_date': collect_date
                            }

                        conversion_count += 1

                # apply the match rules
                for pid, data in running_totals.iteritems():
                    rules_results = []

                    # default operator is ALL
                    if 'operator' not in match_rule:
                        match_rule['operator'] = u'ALL'

                    for imputation in match_rule['imputations']:
                        rules_results.append(operators_map[imputation['operator']](data['total'], int(imputation['value'])))

                    # test any or all for the results of the group match rules
                    # the below code runs if the match rules pass
                    if operators_map[match_rule['operator']](rules_results):

                        patient = (
                            Session.query(studies.Patient)
                            .filter_by(pid=pid)
                            .one()
                        )

                        default_state = (
                            Session.query(datastore.State)
                            .filter_by(name='pending-entry')
                            .one()
                        )

                        # schema with most recent publish date
                        target_schema = (
                            Session.query(datastore.Schema)
                            .filter_by(name=target_schema_name)
                            .order_by(asc(datastore.Schema.publish_date))
                        ).limit(1).one()

                        # if the target schema already exists we want to add data
                        # to the schema rather than creating a new entity
                        entity_exists = False
                        for item in patient.entities:
                            if item.schema.name == target_schema_name:
                                entity = item
                                entity_exists = True
                                break

                        if not entity_exists:
                            entity = datastore.Entity(
                                schema=target_schema,
                                collect_date=data['collect_date'],
                                state=default_state
                            )

                            patient.entities.add(entity)

                        # if we are mapping to a choice, the payload is the name
                        # of the selected choice
                        if mapping.logic['target_choice']:
                            payload = {target_variable: mapping.logic['target_choice']['name']}
                        # if it is not a choice
                        else:
                            payload = {target_variable: data['total']}

                        upload_dir = tempfile.mkdtemp()
                        apply_data(Session, entity, payload, upload_dir)
                        shutil.rmtree(upload_dir)

        else:
            log.append({
                'DRSC Variable': target_schema_name,
                'Message': u'DRSC variable/mapping is not in an approved state'
            })

        redis.hincrby(mappings_id, 'count')

        data = redis.hgetall(mappings_id)
        # redis-py returns everything as string, so we need to clean it
        for key in ('count', 'total'):
            data[key] = int(data[key])
        redis.publish('imputation', json.dumps(data))
