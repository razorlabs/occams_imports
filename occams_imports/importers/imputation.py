"""
Applies imputation mappings to source data

Proposed Algorithm:

#. Build a pivot table from the current project dataset

#. Inspect each mapping in the system
#. Process each mapping into a consolidated pivot table
    - This dataset is esseniatially another pivot table with the data
        properly formatted.
    - The consolidated dataset will keep a unique pid/visit combo as
        reference for creating a new record
#. Process each record in the consolidted pivot table and create a new
    eCRF record in the final database


Additional Notes:

    When processing groups, it really only makes sense when mapping to a
    single choice value, since all the groups are basically assertions.

    When mapping raw values, only one group makes sense.

    Each value must be loaded as a (pid, visid, attr, value) tuple so the same
    value can be found in other forms

"""

from functools import reduce
import json
import six
import uuid
import operator

import sqlalchemy as sa
from sqlalchemy import orm

from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_imports import models

PUBLISH_NAME = 'imputation'

DEFAULT_STATE = 'complete'

OPERATORS = {
    'ID': (lambda operand: operand),  # Identity operator
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


def _start(redis, jobid, total):
    redis.hmset(jobid, {'count': 0, 'total': total})


def _progress(redis, jobid):
    redis.hincrby(jobid, 'count')


def _publish(redis, jobid):
    raw = redis.hgetall(jobid)
    # redis-py returns everything as string, so we need to clean it
    data = {'count': int(raw['count']), 'total': int(raw['total'])}
    redis.publish(PUBLISH_NAME, json.dumps(data))


def _log(redis, jobid, mapping, message):
    data = {
        'schema': mapping.logic.get('target_schema'),
        'variable': mapping.logic.get('target_variable'),
        'message': message.format(mappings=mapping)
    }
    redis.publish(PUBLISH_NAME, json.dumps(data))


def _get_default_state(db_session):
    """
    Returns the default state of created entries

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session

    :returns: the default state to assign to new entries
    :rtype: occams_datastore.models.State
    """
    query = db_session.query(datastore.State).filter_by(name=DEFAULT_STATE)
    result = query.one()
    return result


def _query_mappings(db_session):
    """
    Generates a listing of the mappings

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session

    :returns: An iterable query object that contains all of the mappins
    :rtype: sqlalchemy.orm.query.Query[ occams_imports.models.Mapping ]
    """
    return db_session.query(models.Mapping).filter_by(type=u'imputation')


def _get_schema(db_session, schema_name):
    """
    Finds and returns the most recent published form of the given name

    :param db_session: Application database session
    :param schema_name: The name of the form to query
    :type db_session: sqlalchemy.orm.Session
    :type schema_name: str

    :raises: sqlalchemy.orm.NoResultFound: If the result is not found

    :returns: The maching schema
    :rtype: occams_datastore.models.Schema
    """

    # Constructs a window function to rank schemata by their publish date
    # and then get the first element in the window. Using a window function
    # is more efficient as it does not create a subquery

    latest_schemata_query = (
        db_session.query(
            datastore.Schema,
            sa.func.row_number().over(
                partition_by=datastore.Schema.name,
                order_by=models.publish_date.desc().nullslast()
            ).label('row_number')
        )
    )

    query = (
        db_session.query(datastore.Schema)
        .select_entity_from(latest_schemata_query)
        .filter(
            (datastore.Schema.name == schema_name) &
            (latest_schemata_query.c.row_number == 1)
        )
    )

    result = query.one()
    return result


def _get_attribute(db_session, schema_name, attribute_name):
    """
    Finds and returns the most recent published version of an attribute

    :param db_session: Application database session
    :param schema_name: The name of the form that contains the attribute
    :param attribute_name: The name of the attribute to query
    :type db_session: sqlalchemy.orm.Session
    :type schema_name: str
    :type attribute_name: str

    :raises: sqlalchemy.orm.NoResultFound: If the result is not found

    :returns: The maching schema
    :rtype: occams_datastore.models.Attribute

    """

    schema = _get_schema(db_session, schema_name)
    query = (
        db_session.query(datastore.Attribute)
        .options(orm.joinedload('choices'))
        .filter(schema=schema)
    )
    result = query.one()
    return result


def _save_record(db_session, redis, jobid, pid, viscode, value):
    """
    """


def _convert(db_session, redis, jobid, variable, value):
    """
    """


def _load_values(db_session, redis, jobid, variable):
    """
    """


def _apply_conversion():
    """
    """


def _apply_group(db_session, redis, jobid, group, viscode=None):
    """
    """

    return ()


def _apply_mapping(db_session, redis, jobid, mapping):
    """
    Apply a single mapping heuristic

    :param db_session: Application database session
    :param redis: Application redis session for broadcasting events
    :param jobid: Job number assigend to this pipeline
    :param mapping: The current mapping being processed
    :type db_session: sqlalchemy.orm.Session
    :type redis: redis.Redis
    :type jobid: str
    :type mapping: occams_imports.models.Mapping

    """

    target_variable = _get_attribute(
        db_session,
        mapping.logic.get('target_schema'),
        mapping.logic.get('target_variable'),
    )

    target_value = mapping.logic.get('target_choice', {}).get('name') or None
    groups = mapping.logic.get('groups') or []

    # Ensure we're not processing more groups than we need to given the type
    if target_variable.type == 'choice':
        condition = mapping.logic.get('condition') or 'ALL'
    else:
        # Whatever the first group generates will be our target value
        # Non-choice mappings are only processed as one group
        condition = 'ID'
        if len(groups) > 1:
            groups = groups[0]

    operate = OPERATORS[condition]

    # Collate the final resultset to assert
    # Use reduce() because the next group needs to know about the previous
    # group's result
    results = reduce(_apply_group(db_session, redis, jobid, g) for g in groups)

    for group in groups:
        record = _apply_group(db_session, redis, jobid, group)

        if record is None:
            continue

        (pid, viscode, value) = record


    """
    {
        xxx-xxx: [
            (result of g1, result of g2, result of g3)


            ('week-4', 123),
            ('week-12', 8439),
            ('week-35', 3939),
            ...
        ],
        yyy-yyy: [ ... ]
    }
    """

    for pid, records in six.iteritems(results):
        is_acceptable = operate(value for viscode, value in records)

        if not is_acceptable:
            continue

        if target_variable.type != 'choice':
            target_value = records[0][1]

        record = (pid, None, target_value)
        _save_record(db_session, redis, jobid, target_variable, record)


def apply_all(db_session, redis):
    """
    Applies all completed mappings to the currently pending data set

    This public method will apply all completed mappings in the system
    by traversing the current data stored in `occams_imports.models.SiteData`.

    :param db_session: Application database session
    :param redis: Application redis session for broadcasting events
    :type db_session: sqlalchemy.orm.Session
    :type redis: redis.Redis

    """

    jobid = six.text_type(str(uuid.uuid4()))

    mappings = _query_mappings(db_session)
    mappings_count = mappings.count().scalar()

    _start(redis, jobid, mappings_count)

    for mapping in mappings:
        if mapping.status.name == 'completed':
            _apply_mapping(db_session, redis, jobid, mapping)
        else:
            _log(redis, jobid, mapping, 'Not in approved state')

        _progress(redis, jobid)
        _publish(redis, jobid)
