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

import json
import operator

import numpy as np

import sqlalchemy as sa
from sqlalchemy import orm

from occams_datastore import models as datastore
from occams_imports import models

PUBLISH_NAME = 'imputation'

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


def _query_mappings(db_session):
    """
    Generates a listing of the mappings

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session

    :returns: An iterable query object that contains all of the mappins
    :rtype: sqlalchemy.orm.query.Query[ occams_imports.models.Mapping ]
    """
    return db_session.query(models.Mapping).filter_by(type=u'imputation')


def _count_mappings(mappings):
    """
    """
    return mappings.count().scalar()


def _get_schema(db_session, schema_name):
    """
    Finds and returns the most recent published form of the given name

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param schema_name: The name of the form to query
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
    :type db_session: sqlalchemy.orm.Session
    :param schema_name: The name of the form that contains the attribute
    :type schema_name: str
    :param attribute_name: The name of the attribute to query
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


def _operate(operator, *args):
    operator_func = OPERATORS[operator]
    result = operator_func(*args)
    return result


def _extract_value(conversion, row):
    """
    Extracts a value from the row based on the conversion specification

    A conversion for a variable is structured as follows:

        {
            'byVariable': True,
            'schema': {'name': str},
            'attribute': {'name': str, 'type': enum}
        }

    A conversion for a value is structured as follows:

        {
            'byValue': True,
            'value': scalar
        }

    :param conversion: A conversion specification
    :type conversion: dict


    ""
    """

    # TODO: might need type casting?

    if conversion.get('byVariable'):
        schema_name = conversion.get('schema', {}).get('name')
        attribute = conversion.get('attribute', {})
        attribute_name = attribute.get('name')
        source_column_name = '%s_%s' % (schema_name, attribute_name)
        source_value = row[source_column_name]
        return source_value

    elif conversion.get('byValue'):
        return conversion.get('value')

    else:
        return np.nan


def _impute_group(group, row):
    """
    """

    conversions = group.get('conversions')

    if not conversions:
        return np.nan

    current_value = _extract_value(conversions[0], row)

    for conversion in conversions[1:]:
        operator = conversion.get('operator')
        next_value = _extract_value(conversion, row)
        current_value = _operate(operator, current_value, next_value)

    logic = group.get('logic')

    if not logic:
        return np.nan

    imputations = logic.get('imputations')

    if not imputations:
        return np.nan

    condition = logic.get('operator') or 'ALL'
    clauses = iter(_operate(i, current_value) for i in imputations)
    imputed = _operate(condition, clauses)

    return imputed


def _compile_imputation(condition, target_value, groups):
    """
    Compiles impuation to process a dataframe row into a new column
    """

    def _process_row(row):
        imputed_groups = iter(_impute_group(g, row) for g in groups)
        result = _operate(condition, imputed_groups)

        if result is True:
            if target_value is None:
                return result
            else:
                return target_value
        else:
            return np.nan

    return _process_row


def _apply_mapping(db_session, redis, jobid, frame, mapping):
    """
    Apply a single mapping heuristic

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param redis: Application redis session for broadcasting events
    :type redis: redis.Redis
    :param jobid: Job number assigend to this pipeline
    :type jobid: str
    :param mapping: The current mapping being processed
    :type mapping: occams_imports.models.Mapping
    """

    target_schema_name = mapping.logic.get('target_schema')
    target_attribute_name = mapping.logic.get('target_variable')
    target_attribute = _get_attribute(
        db_session,
        target_schema_name,
        target_attribute_name,
    )
    target_value = mapping.logic.get('target_choice', {}).get('name') or None
    target_column_name = '%s_%s' % (target_schema_name, target_attribute_name)

    groups = mapping.logic.get('groups') or []

    # Ensure we're not processing more groups than we need to given the type
    if target_attribute.type == 'choice':
        condition = mapping.logic.get('condition') or 'ALL'
    else:
        # Whatever the first group generates will be our target value
        # Non-choice mappings are only processed as one group
        condition = 'ID'
        if len(groups) > 1:
            groups = groups[0]

    imputation = _compile_imputation(condition, target_value, groups)

    frame[target_column_name] = frame.apply(imputation)


def apply_all(db_session, redis, jobid, project_name, frame):
    """
    Applies all completed mappings to the currently pending data set

    This public method will apply all completed mappings in the system
    by traversing the current data stored in `occams_imports.models.SiteData`.

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param redis: Application redis session for broadcasting events
    :type redis: redis.Redis
    :param project_name: Apply impuations only for the specified project
    :type project_name: str
    :param frame: The current data frame for the project
    :type frame: pandas.DataFrame
    """

    mappings = _query_mappings(db_session)
    mappings_count = _count_mappings(mappings)

    _start(redis, jobid, mappings_count)

    for mapping in mappings:

        if mapping.status.name == 'completed':
            _apply_mapping(db_session, redis, jobid, frame, mapping)
        else:
            _log(redis, jobid, mapping, 'Not in approved state')

        _progress(redis, jobid)
        _publish(redis, jobid)

    return frame
