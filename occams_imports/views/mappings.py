"""
Perform direct and imputation mappings of DRSC variables
"""

from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid.session import check_csrf_token

from .. import Session


@view_config(
    route_name='imports.mappings',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mappings.pt')
def occams(context, request):
    return {}


@view_config(
    route_name='imports.schemas',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_schemas(context, request):
    import json
    from sqlalchemy.orm import joinedload
    from occams_datastore import models as datastore

    schemas = Session.query(datastore.Schema).options(
        joinedload('attributes')).all()

    data = {}
    data['forms'] = []
    for schema in schemas:
        try:
            attributes = schema.attributes.keys()
        except KeyError:
            attributes = []
        data['forms'].append({
            u'name': schema.name,
            u'publish_date': schema.publish_date.strftime('%Y-%m-%d'),
            u'attributes': attributes
        })

    return json.dumps(data)
