"""
Views to support data file uploads after study lock.
"""

import six
import uuid
import json
import datetime
from cgi import FieldStorage

from pyramid.httpexceptions import HTTPOk
from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy import orm

from occams_studies import models as studies
from occams_datastore import models as datastore
from occams_imports import models as models, tasks, log


@view_config(
    route_name='imports.process_app',
    permission='import',
    renderer='../templates/process/index.pt'
)
def index(context, request):
    """
    Serve the index page for file uploads.
    """

    return {}


@view_config(
    route_name='imports.upload_list',
    request_method='GET',
    permission='add',
    renderer='json'
)
def upload_list(context, request):
    """
    Return the uploads for a particular project.
    """

    db_session = request.db_session

    project = request.matchdict['project']

    this_url = request.route_path('imports.project_list')
    url = '{}/{}/uploads'.format(this_url, project)

    files = (
        db_session.query(models.Upload)
        .filter(models.Upload.study.has(name=project))
    )

    result = {}
    result['items'] = []

    for file in files:
        delete_url = '{}/{}'.format(url, file.id)
        result['items'].append({
            'filename': file.filename,
            'uploadDate': file.modify_date.date(),
            '$url': url,
            '$deleteUrl': delete_url
        })

    return result


@view_config(
    route_name='imports.upload_list',
    request_method='POST',
    permission='add',
    renderer='json'
)
def upload_add(context, request):
    """
    Return the uploads for a particular project.
    """

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
    except orm.exc.MultipleResultsFound:
        errors.append('Multiple studies found in the db for: {}'.format(study))
        study = None
    except orm.exc.NoResultFound:
        errors.append('No study found in the db for: {}'.format(study))
        study = None

    schema_name = request.POST.get('schema')
    try:
        # we need the schema with most recent publish date
        schema = (
            db_session.query(datastore.Schema)
            .filter_by(name=schema_name)
            .order_by(datastore.Schema.publish_date.asc())
        ).limit(1).one()
    except orm.exc.MultipleResultsFound:
        msg = 'Multiple schema found with same publish date found for: {}' \
            .format(schema)
        errors.append(msg)
        study = None
    except orm.exc.NoResultFound:
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
    route_name='imports.upload_detail',
    request_method='DELETE',
    permission='add',
    renderer='json'
)
def upload_delete(context, request):
    """
    Return the uploads for a particular project.
    """

    check_csrf_token(request)
    db_session = request.db_session
    upload_id = request.matchdict['upload']

    db_session.query(models.Upload).filter_by(id=upload_id).delete()

    return HTTPOk()


@view_config(
    route_name='imports.process_project',
    request_method='POST',
    permission='add',
    renderer='json'
)
def process(context, request):
    """
    Dispatches mapping pipeline for the target project
    """

    source_project_name = request.matchdict['project']
    target_project_name = 'drsc'
    jobid = six.text_type(str(uuid.uuid4()))

    tasks.apply_mappings.apply_async(
        args=[jobid, source_project_name, target_project_name],
        task_id=jobid
    )

    return HTTPOk()


@view_config(
    route_name='imports.process_status',
    permission='view'
)
def status(context, request):
    """
    Mapping status notifications

    Yields server-sent events containing status updates of direct mappings
    REQUIRES GUNICORN WITH GEVENT WORKER
    """

    # Close DB connections so we don't hog them while polling
    request.db_session.close()

    def listener():
        pubsub = request.redis.pubsub()
        pubsub.subscribe('mappings')

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
    response.headers['X-Accel-Buffering'] = 'no'  # Tell NGINX not to buffer
    response.app_iter = listener()

    return response
