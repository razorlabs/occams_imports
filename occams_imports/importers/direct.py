"""
Contains long-running tasks that cannot interrupt the user experience.

Tasks in this module will be run in a separate process so the user
can continue to use the application and view the mapping results at a
later time.
"""

import numpy as np
import sqlalchemy as sa

from occams_datastore import models as datastore

from .utils.pivot import \
    DEFAULT_PID_COLUMN, DEFAULT_VISIT_COLUMN, DEFAULT_COLLECT_DATE_COLUMN


def _get_choices(db_session, schema_name, attribute_name):
    """
    Returns the most recent version of every choice ever used for the attribute
    """

    recent_choices_query = (
        db_session.query(datastore.Choice)
        .join(datastore.Choice.attribute)
        .join(datastore.Attribute.schema)
        .add_column(
            sa.func.row_number().over(
                partition_by=datastore.Choice.name,
                order_by=datastore.Schema.publish_date.desc().nullslast()
            ).label('row_number')
        )
        .filter(
            (datastore.Schema.name == schema_name) &
            (datastore.Attribute.name == attribute_name) &
            (datastore.Schema.publish_date != sa.null())
        )
        .subquery()
    )

    query = (
        db_session.query(datastore.Choice)
        .select_entity_from(recent_choices_query)
        .filter(recent_choices_query.c.row_number == 1)
    )

    choices = query.all()

    return choices


def _is_choice(db_session, schema_name, attribute_name):
    """
    Checks if an attribute was ever a choice
    """

    exists_query = (
        db_session.query(datastore.Attribute)
        .join(datastore.Schema)
        .filter(
            (datastore.Schema.name == schema_name) &
            (datastore.Attribute.name == attribute_name) &
            (datastore.Attribute.type == 'choice')
        )
    )

    exists = db_session.query(exists_query.exists()).scalar()

    return exists


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
    Applies all completed DIRECT mappings to the queued data set

    There are currently three supported scenarios when applying mappings:

        1) Mapping is choice-to-choice

            Values will be directly mapped according to the lookup table

        2) Mapping is choice-to-value

            Labels of the source attribute choices will be used as values

        3) Mapping is value-to-value

            Values of source attribute will be used as values for the target

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param channel: Application redis session for broadcasting events
    :type channel: occams_imports.importers.utils.pubsub.ImportStatusChannel
    :param project_name: Apply impuations only for the specified project
    :type project_name: str
    :param frame: The current data frame for the project
    :type frame: pandas.DataFrame

    :returns: the mutated frame
    :rtype: pandas.DataFrame
    """

    source_schema_name = mapping.logic['source_schema']
    source_variable = mapping.logic['source_variable']
    source_column = '_'.join([
        source_project_name, source_schema_name, source_variable
    ])
    source_collect_date = '_'.join([
        source_project_name, source_schema_name, collect_date_column
    ])

    target_schema_name = mapping.logic['target_schema']
    target_variable = mapping.logic['target_variable']
    target_column = '_'.join([
        target_project_name, target_schema_name, target_variable
    ])
    target_collect_date = '_'.join([
        target_project_name, target_schema_name, collect_date_column
    ])

    if source_collect_date in frame and target_collect_date not in frame:
        frame[target_collect_date] = frame[source_collect_date]

    if source_column not in frame:
        frame[source_column] = np.nan
        return frame

    choices_mapping = mapping.logic.get('choices_mapping') or []
    source_is_choice = _is_choice(
        db_session,
        source_schema_name,
        source_variable
    )
    target_is_choice = _is_choice(
        db_session,
        target_schema_name,
        target_variable
    )

    if choices_mapping:
        value_map = {
            choice_mapping['source']: choice_mapping['target']
            for choice_mapping in choices_mapping
            if choice_mapping['source']
        }
    elif source_is_choice and not target_is_choice:
        source_choices = _get_choices(
            db_session,
            source_schema_name,
            source_variable
        )

        value_map = {c.name: c.title for c in source_choices}

    else:
        value_map = {}

    if value_map:
        frame[target_column] = frame[source_column].map(value_map)
    else:
        frame[target_column] = frame[source_column]

    return frame
