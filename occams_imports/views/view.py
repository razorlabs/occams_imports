"""
Roster for direct and imputation mappings of DRSC variables

This is a listing of mapped variables
"""

from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid.session import check_csrf_token

from .. import Session

@view_config(
    route_name='imports.mappings.view',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_schemas(context, request):
    import json
    from sqlalchemy.orm import joinedload
    from occams_datastore import models as datastore
    from occams_imports import models as models

    check_csrf_token(request)

    mappings = Session.query(models.Mapper).all()

    data = {}
    data['rows'] = []

    for mapping in mappings:
        row = {}

        row['drsc_form'] = mapping.mapped['drsc_name']
        row['drsc_variable'] = mapping.mapped['drsc_variable']
        row['site_form'] = mapping.mapped['mapping']['name']
        row['site_variable'] = mapping.mapped['mapping']['variable']
        row['date_mapped'] = mapping.create_date.strftime('%Y-%m-%d')

        data['rows'].append(row)

    # from pdb import set_trace; set_trace()

    return json.dumps(data)
