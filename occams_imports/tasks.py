"""
Contains long-running tasks that cannot interrupt the user experience.

Tasks in this module will be run in a separate process so the user
can continue to use the application and view the mapping results at a
later time.
"""

from occams.celery import app, Session, with_transaction

from .importers import imputation, direct
from .importers.utils.pivot import load_project_frame, populate_project


@app.task(name='apply_mappings', ignore_result=True, bind=True)
@with_transaction
def apply_mappings(task, jobid, source_project_name, target_project_name):
    """
    Applies source project mappings and stores results in the target project

    This process involves creating a large data frame to hold the source data,
    new columns in the data frame will be computed according to the
    mapping specifications specied. Once the data frame has been constructed
    the computed values are stored in target eCRFs for the target project.

    :param task: The anonymously-bound celery task instance
    :type task: celery.Task
    :param jobid: A unique name for this task
    :type jobid: str
    :param source_project_name: Source project to load mappings for
    :type source_project_name: str
    :param target_project_name: Target project to transfer the results
    :type target_project_name: str

    """

    frame = load_project_frame(Session, source_project_name)

    direct.apply_all(Session, app.redis, jobid, source_project_name, frame)
    imputation.apply_all(Session, app.redis, jobid, source_project_name, frame)

    populate_project(Session, source_project_name, target_project_name, frame)
