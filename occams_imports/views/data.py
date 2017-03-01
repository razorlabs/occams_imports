"""
Views to support data file uploads after study lock.
"""

import six
import uuid
import json
import datetime
from cgi import FieldStorage

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy import asc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from occams_studies import models as studies
from occams_datastore import models as datastore
from occams_imports import models as models, tasks, log


@view_config(
    route_name='imports.upload',
    permission='import',
    renderer='../templates/data/upload.pt')
def index(context, request):
    """Serve the index page for file uploads."""
    return {}


@view_config(
    route_name='imports.uploads_list',
    request_method='GET',
    permission='add',
    renderer='json')
def uploads_list(context, request):
    """Return the uploads for a particular project."""
    db_session = request.db_session

    project = request.matchdict['project']

    this_url = request.route_path('imports.project_list')
    url = '{}/{}/uploads'.format(this_url, project)

    files = db_session.query(models.Upload).filter(
        models.Upload.study.has(name=project)).all()

    result = {}
    result['items'] = []
    for file in files:
        delete_url = '{}/{}'.format(url, file.id)
        result['items'].append({
            'filename': file.filename,
            'uploadDate': file.modify_date.date().isoformat(),
            '$url': url,
            '$deleteUrl': delete_url
        })

    return result


@view_config(
    route_name='imports.uploads_list',
    request_method='POST',
    permission='add',
    renderer='json')
def add_uploads(context, request):
    """Return the uploads for a particular project."""
    check_csrf_token(request)
    db_session = request.db_session

    project = request.matchdict.get('project')
    if not project:
        request.response.status = 400
        return {'errors': ['No project found in request']}

    this_url = request.route_path('imports.project_list')
    url = '{}/{}/uploads'.format(this_url, project)

    errors = []
    try:
        study = db_session.query(studies.Study).filter_by(name=project).one()
    except MultipleResultsFound, _:
        errors.append('Multiple studies found in the db for: {}'.format(study))
        study = None
    except NoResultFound, _:
        errors.append('No study found in the db for: {}'.format(study))
        study = None

    schema_name = request.POST.get('schema')
    try:
        # we need the schema with most recent publish date
        schema = (
            db_session.query(datastore.Schema)
            .filter_by(name=schema_name)
            .order_by(asc(datastore.Schema.publish_date))
        ).limit(1).one()
    except MultipleResultsFound, _:
        msg = 'Multiple schema found with same publish date found for: {}' \
            .format(schema)
        errors.append(msg)
        study = None
    except NoResultFound, _:
        msg = 'No schema found in the db for: {}'.format(schema)
        errors.append(msg)
        study = None

    upload = request.POST.get('uploadFile')
    upload_file = None

    if isinstance(upload, FieldStorage):
        filename = upload.filename
        upload_file = upload.file.read()

    if study and upload_file and schema:
        upload = models.Upload(
            study=study,
            schema=schema,
            project_file=upload_file,
            filename=filename
        )
        db_session.add(upload)
        db_session.flush()

        delete_url = '{}/{}'.format(url, upload.id)

        result = {
            'filename': filename,
            'uploadDate': datetime.datetime.now().date(),
            '$url': url,
            '$deleteUrl': delete_url
        }
    else:
        request.response.status = 400
        if not upload_file:
            errors.append('No file found in the request')

        return {'errors': errors}

    return result


@view_config(
    route_name='imports.uploads_detail',
    request_method='DELETE',
    permission='add',
    renderer='json')
def delete_upload(context, request):
    """Return the uploads for a particular project."""
    check_csrf_token(request)
    db_session = request.db_session
    upload_id = request.matchdict['upload']

    db_session.query(models.Upload).filter_by(id=upload_id).delete()

    return {}


@view_config(
    route_name='imports.apply_direct',
    permission='import',
    xhr=True,
    renderer='json')
def direct(context, request):
    tasks.apply_direct_mappings.apply_async(
        args=[]
    )

    return {}


@view_config(
    route_name='imports.apply',
    request_method='GET',
    permission='add',
    renderer='json')
def apply_mappings(context, request):
    db_session = request.db_session
    project = request.matchdict['project']

    task_id = six.text_type(str(uuid.uuid4()))

    # this is the new one
    # this will apply direct and imputation for a particular project

    from ..importers import imputation
    from ..importers.utils.pivot import load_project_frame, populate_project

    db_session = request.db_session
    project_name = project
    redis = request.redis
    jobid = task_id

    frame = load_project_frame(db_session, project_name)
    imputation.apply_all(db_session, redis, jobid, project_name, frame)

    # TODO: project name is case sensitive, need to fix it
    populate_project(db_session, project_name, 'drsc', frame)

    # tasks.apply_imputation_mappings.apply_async(
        # args=[task_id, project],
        # task_id=task_id
    # )


    return {}


@view_config(
    route_name='imports.apply_imputation',
    permission='import',
    xhr=True,
    renderer='json')
def imputation(context, request):
    """Process imputation mappings."""
    # task_id = six.text_type(str(uuid.uuid4()))
    # tasks.apply_imputation_mappings.apply_async(
        # args=[task_id, project_id],
        # task_id=task_id
    # )

    return {}


@view_config(
    route_name='imports.apply_direct_status',
    permission='import',
    renderer='../templates/data/direct.pt')
def apply_direct_status(context, request):
    """Serve mappings result page."""
    return {}


@view_config(
    route_name='imports.apply_imputation_status',
    permission='import',
    renderer='../templates/data/imputation.pt')
def imputation_status(context, request):
    """Serve imputations mappings result page."""
    return {}


@view_config(
    route_name='imports.direct_notifications',
    permission='view')
def notifications(context, request):
    """
    Notifications.

    Yields server-sent events containing status updates of direct mappings
    REQUIRES GUNICORN WITH GEVENT WORKER
    """
    # Close DB connections so we don't hog them while polling
    request.db_session.close()

    def listener():
        pubsub = request.redis.pubsub()
        pubsub.subscribe('direct')

        sse_payload = 'id:{0}\nevent: progress\ndata:{1}\n\n'

        # emit subsequent progress
        for message in pubsub.listen():

            if message['type'] != 'message':
                continue

            data = json.loads(message['data'])

            log.debug(data)
            yield sse_payload.format(str(uuid.uuid4()), json.dumps(data))

    response = request.response
    response.content_type = 'text/event-stream'
    response.cache_control = 'no-cache'
    # Set reverse proxies (if any, i.e nginx) not to buffer this connection
    response.headers['X-Accel-Buffering'] = 'no'
    response.app_iter = listener()

    return response


@view_config(
    route_name='imports.imputations_notifications',
    permission='view')
def imputations_notifications(context, request):
    """
    Notifications.

    Yields server-sent events containing status updates of direct mappings
    REQUIRES GUNICORN WITH GEVENT WORKER
    """
    # Close DB connections so we don't hog them while polling
    request.db_session.close()

    def listener():
        pubsub = request.redis.pubsub()
        pubsub.subscribe('imputation')

        sse_payload = 'id:{0}\nevent: progress\ndata:{1}\n\n'

        # emit subsequent progress
        for message in pubsub.listen():

            if message['type'] != 'message':
                continue

            data = json.loads(message['data'])

            log.debug(data)
            yield sse_payload.format(str(uuid.uuid4()), json.dumps(data))

    response = request.response
    response.content_type = 'text/event-stream'
    response.cache_control = 'no-cache'
    # Set reverse proxies (if any, i.e nginx) not to buffer this connection
    response.headers['X-Accel-Buffering'] = 'no'
    response.app_iter = listener()

    return response
