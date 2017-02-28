"""
Toolset for creating a pivot table from project data files
"""

import pandas as pd
import numpy as np
import math
import io
import datetime
import shutil
import tempfile

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from occams_studies import models as studies
from occams_datastore import models as datastore
from occams_forms.renderers import apply_data
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


def filter_schemas(row, target_project_name):
    """Filter consolidated pandas dataframe row by project name.

    :param row: Row from consolidated pandas dataframe
    :type row: pandas.Dataframe.itterrows
    :param target_project_name study name to filter bvy
    :type target_project_name: str
    :returns: Filtered schemas including only target project key
    :rtype: dict
    """
    schemas = {}

    for col in row.keys():
        if col not in ['pid', 'visit']:
            parsed_columns = col.split('_')
            project = parsed_columns[0]
            schema_name = parsed_columns[1]
            variable = parsed_columns[2]
            if variable == 'collect' and parsed_columns[3] == 'date':
                variable = 'collect_date'
            if project == target_project_name:
                if schema_name in schemas:
                    schemas[schema_name][variable] = row[col]
                else:
                    schemas[schema_name] = {}
                    schemas[schema_name][variable] = row[col]

            else:
                # bypass non-target project variables
                continue

    return schemas


def populate_project(
        db_session,
        source_project_name,
        target_project_name,
        consolidated_frame):
    """
    Processes a final dataframe (i.e. a frame after mappings have been applied)
    and creates entities for the target project.

    :param db_session: Current database transaction session
    :type db_session: sqlalchemy.orm.session.Session
    :param source_project_name: source study being processed
    :type source_project_name: str
    :param target_project_name: study where entities will be applied
    :type target_project_name: str
    :param consolidated_frame: dataframe populated with mapped variables
    :type consolidated_frame: pandas.DataFrame
    :returns: none
    """
    for index, row in consolidated_frame.iterrows():
        pid = row['pid']

        schemas = filter_schemas(row, target_project_name)

        patient = (
            db_session.query(studies.Patient)
            .filter_by(pid=pid)
            .one()
        )

        for schema in schemas:
            target_schema = (
                db_session.query(datastore.Schema)
                .filter_by(name=schema)
            ).one()

            default_state = (
                db_session.query(datastore.State)
                .filter_by(name='pending-entry')
                .one()
            )

            entity = datastore.Entity(
                schema=target_schema,
                collect_date=datetime.date.today().isoformat(),
                state=default_state
            )

            patient.entities.add(entity)

            for variable in schemas[schema]:
                target_value = schemas[schema][variable]
                is_number = isinstance(target_value, (int, long, float))
                is_nan = False
                if is_number:
                    is_nan = math.isnan(target_value)
                if not is_number or (is_number and not is_nan):
                    payload = {variable: schemas[schema][variable]}
                    upload_dir = tempfile.mkdtemp()
                    apply_data(db_session, entity, payload, upload_dir)
                    shutil.rmtree(upload_dir)


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
