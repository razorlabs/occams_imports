"""
Views to support data file uploads after study lock.
"""

import six
import uuid
import json
import datetime

from pyramid.view import view_config
from pyramid.session import check_csrf_token

from occams_studies import models as studies
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

    project = request.matchdict['project']
    this_url = request.route_path('imports.project_list')
    url = '{}/{}/uploads'.format(this_url, project)

    study = db_session.query(studies.Study).filter_by(name=project).one()
    upload = request.POST['uploadFile']
    filename = upload.filename
    upload_file = upload.file.read()

    if study and upload_file:
        upload = models.Upload(
            study=study,
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
        errors = []
        if not study:
            errors.append('No study found in the db for: '.format(project))
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

    records = (
        db_session.query(models.Upload).filter(models.Upload.study.has(
            name=project)).all()
    )

    study = records[0].study.name
    filename = records[0].filename
    # this is the new one
    # this will apply direct and imputation for a particular project
    from pdb import set_trace; set_trace()
    # tasks.apply_direct_mappings.apply_async(
    #     args=[]
    # )

    return {}


@view_config(
    route_name='imports.apply_imputation',
    permission='import',
    xhr=True,
    renderer='json')
def imputation(context, request):
    """Process imputation mappings."""
    task_id = six.text_type(str(uuid.uuid4()))

    tasks.apply_imputation_mappings.apply_async(
        args=[],
        task_id=task_id
    )

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
