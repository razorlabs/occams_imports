"""
Toolset for creating a pivot table from project data files
"""

import pandas as pd
import io

from ... import models


DEFAULT_PID_COLUMN = 'pid'
DEFAULT_VISIT_COLUMN = 'visit'
DEFAULT_COLLECT_DATE_COLUMN = 'collect_date'


def get_uploads(db_session, project_name):
    """
    Returns a listing of the uploads for a given project

    :param db_session: Current database transaction session
    :type db_session: sqlalchemy.orm.session.Session
    :param project_name: Project that contains the desired upload files
    :type project_name: str

    :returns: a iterable containing the project uploads
    :rtype: iter(occams_import.models.Upload)
    """

    uploads = (
        db_session.query(models.Upload)
        .filter(models.Upload.study.has(name=project_name))
    )

    return uploads


def load_schema_frame(
        schema,
        buffer_,
        pid_column=DEFAULT_PID_COLUMN,
        visit_column=DEFAULT_VISIT_COLUMN,
        collect_date_column=DEFAULT_COLLECT_DATE_COLUMN,
        ):
    """
    Generates a data frame containing the data for the specified schema

    This method will also rename the data columns to remain unique across
    all data files in the project by concatenating the schema name to
    the column name.

    :param schema: Schame to be used as a data dictionary for the the data file
    :type schema: occams_datastore.models.Schema
    :param buffer_: Data file stream (in csv-format)
    :type buffer_: File-like object
    :param pid_column: (optional) Column name that contains the PID
    :type pid_column: str
    :param visit_column: (optional) Column name that contains the VISIT code
    :type visit_column: str
    :param collect_date_column: (optional) Column name that contains
                                the collect_date
    :type collect_date_column: str

    :returns: data frame containing the the uploaded schema data file
    :rtype: pandas.DataFrame

    """

    frame = pd.read_csv(buffer_)

    index_columns = [pid_column, visit_column, collect_date_column]
    variable_columns = [a.name for a in schema.iterleafs()]

    frame = frame[index_columns + variable_columns]

    renamed_columns = {c: schema.name + '_' + c for c in variable_columns}
    renamed_columns[collect_date_column] = \
        schema.name + '_' + collect_date_column

    frame.rename(columns=renamed_columns, inplace=True)

    return frame


def load_project_frame(
        db_session,
        project_name,
        pid_column=DEFAULT_PID_COLUMN,
        visit_column=DEFAULT_VISIT_COLUMN,
        collect_date_column=DEFAULT_COLLECT_DATE_COLUMN,
        ):
    """
    Generates a data frame for all of the uploaded files for a given project

    This function uses an "outer" join on pid/visit to merge multiple data
    file uploads for a project into a unified project data frame for easy
    lookup when performing imputations.

    The goal of unified the dataset is so that context is retained across
    all visits, thus allowing the impuation mapper to distinguish between
    already created record from one visit to another. This also has the added
    benefit that additional metadata can be attached to the dataframe to
    allow gradual build of the final mapped data-set.

    :param db_session: Current database transaction session
    :type db_session: sqlalchemy.orm.session.Session
    :param project_name: Project that contains the desired upload files
    :type project_name: str
    :param pid_column: (optional) Column name that contains the PID
    :type pid_column: str
    :param visit_column: (optional) Column name that contains the VISIT code
    :type visit_column: str
    :param collect_date_column: (optional) Column name that contains
                                the collect_date
    :type collect_date_column: str

    :returns: data frame containing the merged data upload tables
    :rtype: pandas.DataFrame
    """

    uploads = get_uploads(db_session, project_name)

    subframes = iter(
        load_schema_frame(
            upload.schema,
            io.BytesIO(upload.project_file),
            pid_column=pid_column,
            visit_column=visit_column,
            collect_date_column=collect_date_column
        )
        for upload in uploads
    )

    frame = next(subframes)

    for sub in subframes:
        frame = frame.merge(sub, on=['pid', 'visit'], how='outer')

    return frame
