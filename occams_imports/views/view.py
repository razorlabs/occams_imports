"""
Roster for direct and imputation mappings of DRSC variables

This is a listing of mapped variables
"""

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
    route_name='imports.mappings.delete',
    permission='view',
    request_method='DELETE',
    xhr=True,
    renderer='json')
def delete_mappings(context, request):
    import json
    from occams_imports import models as models

    check_csrf_token(request)

    mappings = request.json['mapped_delete']

    for mapping in mappings:
        if mapping['deleteRow'] is True:
            Session.query(models.Mapper).filter(
                models.Mapper.id == mapping['mapped_id']).delete()

    Session.flush()

    return json.dumps({})


@view_config(
    route_name='imports.mappings.view_mapped',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mapped.pt')
def get_schemas_mapped(context, request):
    from occams_datastore import models as datastore
    from occams_imports import models as models

    mappings = Session.query(models.Mapper).filter(
        models.Mapper.id == request.params['id']).one()

    mappings_form_rows = []
    drsc_form_rows = []

    if mappings.mapped['mapping_type'] == u'direct':
        # get site form and choices
        # we need to display the label map on visualization page
        # site labels for choices is not available in json map in mappings tbl
        schema_name = mappings.mapped['mapping']['name']
        schema_publish_date = mappings.mapped['mapping']['publish_date']
        schema = Session.query(datastore.Schema).filter(
            datastore.Schema.name == schema_name,
            datastore.Schema.publish_date == schema_publish_date).one()

        attribute = schema.attributes[mappings.mapped['mapping']['variable']]

        drsc_variable = mappings.mapped['drsc_variable']
        if mappings.schema.attributes[drsc_variable].type == u'choice':
            choices = mappings.schema.attributes[drsc_variable].choices
            # from pdb import set_trace; set_trace()
            # choices = sorted(choices, key=itemgetter('order'))
            # data to populate drsc table
            for choice in sorted(choices, key=lambda i: choices[i].order):
                drsc_form_rows.append({
                    'variable': drsc_variable,
                    'description': mappings.schema.title,
                    'type': mappings.schema.attributes[drsc_variable].type,
                    'confidence': mappings.mapped['mapping']['confidence'],
                    'label': choices[choice].title,
                    'key': choice,

                })

            # We need all choices to diplay even if not mapped
            choices = attribute.choices

            for choice in sorted(choices, key=lambda i: choices[i].order):
                mapped_value = u''
                mapped_label = u''
                for row in mappings.mapped['mapping']['choices_map']:
                    if row['mapped'] == choice:
                        mapped_value = row['name']
                        mapped_label = row['label']

                mappings_form_rows.append({
                    'variable': attribute.name,
                    'description': attribute.title,
                    'type': mappings.schema.attributes[drsc_variable].type,
                    'form': schema.name,
                    'label': choices[choice].title,
                    'value': choices[choice].name,
                    'mapped_variable': drsc_variable,
                    'mapped_label': mapped_label,
                    'mapped_value': mapped_value
                })
        else:
            # no choices processing
            drsc_form_rows.append({
                'variable': drsc_variable,
                'description': mappings.schema.title,
                'type': mappings.schema.attributes[drsc_variable].type,
                'confidence': mappings.mapped['mapping']['confidence'],
                'label': u'',
                'key': u'',
            })

            mappings_form_rows.append({
                'variable': attribute.name,
                'description': attribute.title,
                'type': mappings.schema.attributes[drsc_variable].type,
                'form': schema.name,
                'label': attribute.title,
                'value': u'',
                'mapped_variable': drsc_variable,
                'mapped_label': u'',
                'mapped_value': u''
            })

    else:
        # process as imputation
        pass

    return {
        'drsc_form': mappings.schema.name,
        'drsc_publish_date': mappings.schema.publish_date.strftime('%Y-%m-%d'),
        'drsc_form_rows': drsc_form_rows,
        'mappings_form_rows': mappings_form_rows
    }
