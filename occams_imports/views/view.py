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
        row['mapped_id'] = mapping.id

        data['rows'].append(row)

    return json.dumps(data)


@view_config(
    route_name='imports.mappings.view_mapped',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mapped.pt')
def get_schemas_mapped(context, request):
    import json
    from sqlalchemy.orm import joinedload
    from occams_datastore import models as datastore
    from occams_imports import models as models

    mappings = Session.query(models.Mapper).filter(
        models.Mapper.id == request.params['id']).one()

    if mappings.mapped['mapping_type'] == u'direct':
        drsc_form_rows = []
        drsc_variable = mappings.mapped['drsc_variable']
        if mappings.schema.attributes[drsc_variable].type == u'choice':
            choices = mappings.schema.attributes[drsc_variable].choices
            for choice in choices:
                drsc_form_rows.append({
                    'variable': drsc_variable,
                    'description': mappings.schema.title,
                    'type': mappings.schema.attributes[drsc_variable].type,
                    'confidence': mappings.mapped['mapping']['confidence'],
                    'label': choices[choice].title,
                    'key': choice,

                })

    else:
        # process as imputation
        pass

    return {
        'drsc_form': mappings.schema.name,
        'drsc_publish_date': mappings.schema.publish_date.strftime('%Y-%m-%d'),
        'drsc_form_rows': drsc_form_rows
    }
