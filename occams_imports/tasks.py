"""
Contains long-running tasks that cannot interrupt the user experience.

Tasks in this module will be run in a separate process so the user
can continue to use the application and view the mapping results at a
later time.
"""

from occams.celery import app, Session, with_transaction

from . import models
from .importers import imputation, direct
from .importers.utils.pubsub import ImportStatusChannel
from .importers.utils.pivot import \
    load_project_frame, populate_project, truncate_project


def _query_mappings(db_session, project_name):
    """
    Generates a listing of the mappings

    :param db_session: Application database session
    :type db_session: sqlalchemy.orm.Session
    :param project_name: Project Name
    :type project_name: str

    :returns: An iterable query object that contains all of the mappins
    :rtype: sqlalchemy.orm.query.Query[ occams_imports.models.Mapping ]
    """
    query = (
        db_session.query(models.Mapping)
        .filter(models.Mapping.study.has(name=project_name))
    )
    return query


def _count_mappings(mappings):
    """
    """
    return mappings.count()


@app.task(name='apply_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_mappings(task, jobid, source_project_name, target_project_name):
    """
    Applies source project mappings and stores results in the target project

    This process involves creating a large data frame to hold the source data,
    new columns in the data frame will be computed according to the
    mapping specifications specied. Once the data frame has been constructed
    the computed values are stored in target eCRFs for the target project.

    .. note: THIS IS AN EXTREMELY LONG AND RESOURCE-HEAVY PROCESS.

             It is his highly recommended this be run on a machine with
             plenty of horsepower and memory.

    :param task: The anonymously-bound celery task instance
    :type task: celery.Task
    :param jobid: A unique name for this task
    :type jobid: str
    :param source_project_name: Source project to load mappings for
    :type source_project_name: str
    :param target_project_name: Target project to transfer the results
    :type target_project_name: str

    """

    redis = app.redis
    db_session = Session

    frame = load_project_frame(db_session, source_project_name)

    mappings = _query_mappings(db_session, source_project_name)
    mappings_count = _count_mappings(mappings)

    channel = ImportStatusChannel(redis, jobid)
    channel.send_reset(mappings_count)

    for mapping in mappings:

        if mapping.status.name != 'approved':
            channel.send_message(mapping, 'Not in approved state')
            continue

        if mapping.type == 'direct':
            mapper = direct.apply_mapping
        elif mapping.type == 'imputation':
            mapper = imputation.apply_mapping
        else:
            message = 'Unsupported mapping type: %s' % mapping.type
            channel.send_message(mapping, message)
            continue

        mapper(
            Session,
            channel,
            source_project_name,
            target_project_name,
            frame,
            mapping
        )

        channel.send_progress()
        channel.send_message(mapping, 'Mapping complete')

    truncate_project(Session, target_project_name)
    populate_project(Session, target_project_name, frame)
