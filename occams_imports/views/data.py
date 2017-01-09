"""
Views to support data file uploads after study lock.
"""

import six
import uuid
import json
import unicodecsv as csv

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy.sql import exists

from occams_datastore import models as datastore
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
    route_name='imports.upload_status',
    permission='import',
    renderer='../templates/data/status.pt')
def status(context, request):
    """Process file upload."""
    check_csrf_token(request)
    db_session = request.db_session

    site = request.POST['site'].lower()
    patient_site = studies.Site(name=site.lower(), title=site.upper())
    filename = request.POST['data-file'].filename

    upload_file = request.POST['data-file'].file

    reader = csv.DictReader(upload_file, encoding='utf-8', delimiter=',')

    for row in reader:
        schema_name = row['form_name']
        schema_publish_date = row['form_publish_date']

        schema = (
            db_session.query(datastore.Schema)
            .filter_by(name=schema_name)
            .filter_by(publish_date=schema_publish_date)
        ).one()

        study = (
            db_session.query(studies.Study)
            .filter_by(name=site.lower())
        ).one()

        patient_pid = row['pid']
        patient_exists = (
            db_session.query(
                exists()
                .where(studies.Patient.pid == patient_pid)).scalar()
        )

        if not patient_exists:
            patient = studies.Patient(
                pid=patient_pid,
                site=patient_site
            )
            db_session.add(patient)
            db_session.flush()

        data_row = models.SiteData(
            schema=schema,
            study=study,
            data=row
        )

        db_session.add(data_row)

    return {'site': site, 'filename': filename}


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
