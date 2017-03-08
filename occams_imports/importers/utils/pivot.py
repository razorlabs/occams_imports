"""
Toolset for creating a pivot table from project data files
"""

import math
import io
import numbers
import shutil
import tempfile

import numpy as np
import pandas as pd
from sqlalchemy import orm

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
        project,
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

    index_columns = [pid_column, visit_column, collect_date_column]
    variable_columns = [a.name for a in schema.iterleafs()]

    # Load the data uninterpreted so that we can convert the columns manually
    frame = pd.read_csv(buffer_, dtype=str)

    frame[collect_date_column].apply(pd.to_datetime)

    for variable_name in variable_columns:

        # Add any columns that are in the codebook but not in the source file
        if variable_name not in frame:
            frame[variable_name] = np.nan
            continue

        type_ = schema.attributes[variable_name].type

        if type_ in ('number',):
            frame[variable_name] = \
                frame[variable_name].apply(pd.to_numeric, errors='coerce')
        elif type_ in ('date', 'datetime'):
            frame[variable_name] = \
                frame[variable_name].apply(pd.to_datetime, errors='coerce')

    frame = frame[index_columns + variable_columns]

    renamed_columns = {
        c: '_'.join([project.name, schema.name, c])
        for c in variable_columns
    }
    renamed_columns[collect_date_column] = \
        '_'.join([project.name, schema.name, collect_date_column])

    frame.rename(columns=renamed_columns, inplace=True)

    return frame


def populate_project(
        db_session,
        project_name,
        consolidated_frame,
        pid_column=DEFAULT_PID_COLUMN,
        visit_column=DEFAULT_VISIT_COLUMN,
        collect_date_column=DEFAULT_COLLECT_DATE_COLUMN,
        ):
    """
    Processes a final dataframe (i.e. a frame after mappings have been applied)
    and creates entities for the target project.

    :param db_session: Current database transaction session
    :type db_session: sqlalchemy.orm.session.Session
    :param project_name : study where entities will be applied
    :type project_name: str
    :param consolidated_frame: dataframe populated with mapped variables
    :type consolidated_frame: pandas.DataFrame
    :returns: none
    """

    site = db_session.query(studies.Site).filter_by(name=project_name).one()
    project = (
        db_session.query(studies.Study)
        .filter_by(name=project_name)
        .one()
    )
    default_state = (
        db_session.query(datastore.State)
        .filter_by(name='pending-entry')
        .one()
    )

    for index, row in consolidated_frame.iterrows():
        pid = row['pid']

        try:
            patient = (
                db_session.query(studies.Patient)
                .filter_by(pid=pid)
                .one()
            )
        except orm.exc.NoResultFound:
            patient = studies.Patient(site=site, pid=pid)
            db_session.add(patient)
            db_session.flush()

        for schema in project.schemata:

            payload = {}

            for attribute in schema.iterleafs():
                column_name = '_'.join([
                    project.name, schema.name, attribute.name
                ])

                if column_name not in row:
                    continue

                value = row[column_name]

                if isinstance(value, numbers.Number) and math.isnan(value):
                    continue

                payload[attribute.name] = value

            # Avoid creating empty records
            if not payload:
                continue

            calculated_collect_date_column = '_'.join([
                project.name, schema.name, collect_date_column
            ])
            collect_date = row[calculated_collect_date_column]

            entity = datastore.Entity(
                schema=schema,
                collect_date=collect_date,
                state=default_state
            )

            patient.entities.add(entity)

            upload_dir = tempfile.mkdtemp()
            apply_data(db_session, entity, payload, upload_dir)
            shutil.rmtree(upload_dir)
            db_session.flush()


def truncate_project(db_session, project_name):
    """
    Truncates all of the data for a project

    :param db_session: Current database transaction session
    :type db_session: sqlalchemy.orm.session.Session
    :param project_name: Project whose data will be removed
    :type project_name: str
    """

    context_subquery = (
        db_session.query(datastore.Context.id)
        .join(
            studies.Patient,
            (studies.Patient.id == datastore.Context.key) &
            (datastore.Context.external == 'patient')
        )
        .subquery()
    )

    (
        db_session.query(datastore.Context)
        .filter(datastore.Context.id.in_(context_subquery))
        .delete(synchronize_session=False)
    )

    (
        db_session.query(studies.Patient)
        .filter(studies.Patient.site.has(name=project_name))
        .delete(synchronize_session=False)
    )


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
            upload.study,
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
