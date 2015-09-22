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
    from occams_imports import models as models

    schemas = Session.query(datastore.Schema).options(
        joinedload('attributes')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site != 'DRSC').order_by(datastore.Schema.name).all()

    drsc_schemas = Session.query(datastore.Schema).options(
        joinedload('attributes')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site == 'DRSC').all()

    data = {}
    data['forms'] = []

    for schema in schemas:
        attributes = []
        for attr in schema.attributes:
            attribute = {}
            attribute['variable'] = schema.attributes[attr].name
            attribute['label'] = schema.attributes[attr].title
            attributes.append(attribute)

        data['forms'].append({
            u'name': schema.name,
            u'publish_date': schema.publish_date.strftime('%Y-%m-%d'),
            u'attributes': attributes
        })

    return json.dumps(data)
