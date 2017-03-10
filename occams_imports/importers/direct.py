"""
Contains long-running tasks that cannot interrupt the user experience.

Tasks in this module will be run in a separate process so the user
can continue to use the application and view the mapping results at a
later time.
"""

import numpy as np

from occams_imports import models

from .utils.pivot import \
    DEFAULT_PID_COLUMN, DEFAULT_VISIT_COLUMN, DEFAULT_COLLECT_DATE_COLUMN


def apply_all(
        db_session,
        redis,
        jobid,
        source_project_name,
        target_project_name,
        frame,
        pid_column=DEFAULT_PID_COLUMN,
        visit_column=DEFAULT_VISIT_COLUMN,
        collect_date_column=DEFAULT_COLLECT_DATE_COLUMN,
        ):
    """
    Applies all completed DIRECT mappings to the queued data set

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param redis: Application redis session for broadcasting events
    :type redis: redis.Redis
    :param project_name: Apply impuations only for the specified project
    :type project_name: str
    :param frame: The current data frame for the project
    :type frame: pandas.DataFrame

    :returns: the mutated frame
    :rtype: pandas.DataFrame
    """

    mappings = (
        db_session.query(models.Mapping)
        .filter(
            (models.Mapping.study.has(name=source_project_name)) &
            (models.Mapping.type == 'direct') &
            (models.Mapping.status.has(name='approved'))
        )
    )

    for mapping in mappings:

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

        choices_mapping = mapping.logic.get('choices_mapping') or []

        # TODO: Regresssion, we need to fetch the target attribute label
        #       to use as the value for a choice -> value direct mapping

        if source_column not in frame:
            frame[source_column] = np.nan
        elif choices_mapping:
            value_map = {
                choice_mapping['source']: choice_mapping['target']
                for choice_mapping in choices_mapping
                if choice_mapping['source']
            }
            frame[target_column] = frame[source_column].map(value_map)
        else:
            frame[target_column] = frame[source_column]

    return frame
