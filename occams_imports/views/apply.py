"""Views to support the application of mappings."""

import six
import uuid
import json

from pyramid.view import view_config

from occams_imports import tasks, log


@view_config(
    route_name='imports.apply_direct',
    permission='import',
    xhr=True,
    renderer='json')
def direct(context, request):
    """Process direct mappings."""
    task_id = six.text_type(str(uuid.uuid4()))

    tasks.apply_direct_mappings.apply_async(
        args=[],
        task_id=task_id
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
    renderer='../templates/apply/direct.pt')
def status(context, request):
    """Serve mappings result page."""
    return {}


@view_config(
    route_name='imports.apply_imputation_status',
    permission='import',
    renderer='../templates/apply/imputation.pt')
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
