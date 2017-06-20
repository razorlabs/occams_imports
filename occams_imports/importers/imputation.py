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

import operator as py

import pandas as pd
import numpy as np

import sqlalchemy as sa
from sqlalchemy import orm

from occams_datastore import models as datastore

from .utils.pivot import \
    DEFAULT_PID_COLUMN, DEFAULT_VISIT_COLUMN, DEFAULT_COLLECT_DATE_COLUMN


OPERATORS = {
    'EQ': py.eq,
    'NE': py.ne,
    'LT': py.lt,
    'LTE': py.le,
    'GT': py.gt,
    'GTE': py.ge,
    'ADD': py.add,
    'SUB': py.sub,
    'MUL': py.mul,
    'DIV': py.div,
    'ANY': any,
    'ALL': all,
    'ID': (lambda operand: next(operand)),  # Identity operator
}


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
                order_by=datastore.Schema.publish_date.desc().nullslast()
            ).label('row_number')
        )
        .subquery()
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
        .filter_by(schema=schema, name=attribute_name)
    )
    result = query.one()
    return result


def _operate(operator, *args):
    operator_func = OPERATORS[operator]
    result = operator_func(*args)
    return result


def _extract_value(project_name, conversion, row):
    """
    Extracts a value from the row based on the conversion specification

    A conversion for a variable is structured as follows:

        {
            'byVariable': True,
            'value': {
                'schema': {'name': str},
                'attribute': {'name': str, 'type': enum}
            }
            'operator': scalar operator token
        }

    A conversion for a value is structured as follows:

        {
            'byValue': True,
            'value': scalar
            'operator': scalar operator token
        }

    .. note:: The operator in the first conversion is ignored since there is
              nothing to evaluate

    :param conversion: A conversion specification
    :type conversion: dict
    :param row: The current row in the data frame being processed
    :type row: pandas.Series

    :returns: value from the frame if by variable, the scalar value in the
                conversion if by value, otherwise `pd.nan`
    :rtype: int or `pd.nan`
    """

    value = np.nan

    if conversion.get('byVariable'):
        schema_name = conversion.get('value', {}).get('schema', {}).get('name')
        attribute = conversion.get('value', {}).get('attribute', {})
        attribute_name = attribute.get('name')
        source_column_name = \
            '_'.join([project_name, schema_name, attribute_name])
        if source_column_name in row:
            value = row[source_column_name]

    elif conversion.get('byValue'):
        # XXX: Making an assumption that all conversions are by integer
        #      values as that is the the UI currently allows
        value = int(conversion.get('value'))

    if pd.isnull(value):
        raise HasNan

    return value


class HasNan(Exception):
    pass


def _impute_group(project_name, group, row):
    """
    Processes an individual group in a logic mapping

    A group specification is structured as follows:

        {
            "conversions": conversion[]
            "logic": {
                "operator": "ALL" or "ANY"
                "imputations": operation[]
            }
        }


    :param group: The group structure to evaluate
    :type group: dict
    :param row: The current row in the data frame being processed
    :type row: pandas.Series

    :returns: The reduced group by the specified operator in the logic
    :rtype: Truish or Falseish value, otherwise `pd.nan` if unable to be
            evaluated

    .. seealso::

        :func:`_extract_value` - conversion specification
        :func:`_operate` - operation specification

    """

    conversions = group.get('conversions')

    if not conversions:
        return np.nan

    current_value = _extract_value(project_name, conversions[0], row)

    for conversion in conversions[1:]:
        operator = conversion.get('operator')
        next_value = _extract_value(project_name, conversion, row)
        current_value = _operate(operator, current_value, next_value)

    logic = group.get('logic') or {}
    condition = logic.get('operator') or 'ALL'
    imputations = logic.get('imputations')

    if not imputations:
        return current_value

    def impute(imputation, candidate):
        condition = imputation.get('operator')
        check = imputation.get('value')
        result = _operate(condition, candidate, check)
        return result

    clauses = iter(impute(i, current_value) for i in imputations)
    imputed = _operate(condition, clauses)

    return imputed


def _compile_imputation(
        project_name,
        condition,
        target_column_name,
        target_value,
        groups
        ):
    """
    Compiles impuation to process a dataframe row into a new column
    """

    def _process_row(row):

        try:
            existing_value = row[target_column_name]
        except KeyError:
            pass
        else:
            if not pd.isnull(existing_value):
                return existing_value

        imputed_groups = iter(
            _impute_group(project_name, g, row) for g in groups
        )

        try:
            result = _operate(condition, imputed_groups)
        except HasNan:
            return np.nan

        # ALL/ANY coerce to a boolean so we need to return the desired value
        if condition in ('ANY', 'ALL'):
            if result:
                return target_value
            else:
                return np.nan
        else:
            return result

    return _process_row


def apply_mapping(
        db_session,
        channel,
        source_project_name,
        target_project_name,
        frame,
        mapping,
        pid_column=DEFAULT_PID_COLUMN,
        visit_column=DEFAULT_VISIT_COLUMN,
        collect_date_column=DEFAULT_COLLECT_DATE_COLUMN,
        ):
    """
    Apply a single mapping heuristic.

    Imputation mapping logic is structured as follows:

    {"target_schema": {"name": str, "title": str},
    "target_variable": {"name": str, "title": str},
    "target_choice": None or {"name": str, "title": str},
    "condition": "ANY" or "ALL",
    "groups": group[],
    "forms": [ [str, str] ]}

    To the set the collect date in the target form, the earliest
    collect date in the source forms are used. To avoid situations
    where difference source forms are used for different target fields,
    the existing target collect date is also used as a candidate for
    determining the earliest collect date.

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param channel: Application redis session for broadcasting events
    :type channel: occams_imports.importers.utils.pubsub.ImportStatusChannel
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

    target_choice = mapping.logic.get('target_choice') or {}
    target_value = target_choice.get('name') or None
    target_column_name = '_'.join([
        target_project_name, target_schema_name, target_attribute_name
    ])
    target_collect_date = '_'.join([
        target_project_name, target_schema_name, collect_date_column
    ])

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

    # XXX: In hindsight, this should have built a pandas filter query to
    # efficiently seek out matching rows and only set the target value on
    # those rows.

    imputation = _compile_imputation(
        mapping.study.name,
        condition,
        target_column_name,
        target_value,
        groups
    )
    frame[target_column_name] = frame.apply(imputation, axis=1)

    # Re-calculate the collect dates (including the current one)
    # to use the earliest collect_date
    collect_date_columns = [
        '_'.join([
            source_project_name, schema_name, collect_date_column
        ])
        for schema_name, attribute_name in (mapping.logic.get('forms') or [])
    ]

    if target_collect_date in frame:
        collect_date_columns.append(target_collect_date)

    frame[target_collect_date] = frame.loc[:, collect_date_columns].min(axis=1)
