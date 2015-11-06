"""
Roster for direct and imputation mappings of DRSC variables

This is a listing of mapped variables
"""

import json

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from occams_datastore import models as datastore
from occams_imports import models as models


@view_config(
    route_name='imports.index',
    permission='view',
    renderer='../templates/main/view.pt')
def index(context, request):
    """
    """
    return {}


@view_config(
    route_name='imports.mappings.view',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_schemas(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    mappings = db_session.query(models.Mapper).order_by(models.Mapper.id).all()

    data = {}
    data['rows'] = []

    for mapping in mappings:
        row = {}

        row['drsc_form'] = mapping.mapped['drsc_name']
        row['drsc_variable'] = mapping.mapped['drsc_variable']
        row['site'] = mapping.mapped['site']

        # imputation mappings may have multiple forms and variables
        if mapping.mapped['mapping_type'] == u'imputation':
            row['forms'] = mapping.mapped['mapping']['forms']

        else:
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
    check_csrf_token(request)
    db_session = request.db_session

    mappings = request.json['mapped_delete']

    records = []

    # only delete if all records can be deleted
    for mapping in mappings:
        if mapping['deleteRow'] is True:
            try:
                mapped = db_session.query(models.Mapper).filter(
                    models.Mapper.id == mapping['mappedId']).one()

            except NoResultFound:
                request.response.status = 400
                return json.dumps(
                    {'error': 'No record found for id: '.format(
                        mapping['mappedId'])})

            except MultipleResultsFound:
                request.response.status = 400
                return json.dumps(
                    {'error': 'Multiple records found for id: '.format(
                        mapping['mappedId'])})

            else:
                records.append(mapped)

    for record in records:
        db_session.delete(record)

    return json.dumps({})


@view_config(
    route_name='imports.mappings.view_mapped',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mapped.pt')
def get_schemas_mapped(context, request):
    db_session = request.db_session

    mappings = db_session.query(models.Mapper).filter(
        models.Mapper.id == request.params['id']).one()

    if mappings.mapped['mapping_type'] == u'imputation':
        return render_to_response('../templates/mappings/imputed_mapped.pt',
                                  {}, request=request)

    site_import = db_session.query(models.Import).filter(
        datastore.Schema.name == mappings.mapped['mapping']['name']).filter(
        datastore.Schema.publish_date == mappings.mapped['mapping']['publish_date']).filter(
        datastore.Schema.id == models.Import.schema_id).one()

    site = site_import.site

    mappings_form_rows = []
    drsc_form_rows = []

    if mappings.mapped['mapping_type'] == u'direct':
        # get site form and choices
        # we need to display the label map on visualization page
        # site labels for choices is not available in json map in mappings tbl
        schema_name = mappings.mapped['mapping']['name']
        schema_publish_date = mappings.mapped['mapping']['publish_date']
        schema = db_session.query(datastore.Schema).filter(
            datastore.Schema.name == schema_name,
            datastore.Schema.publish_date == schema_publish_date).one()

        attribute = schema.attributes[mappings.mapped['mapping']['variable']]

        drsc_variable = mappings.mapped['drsc_variable']
        if mappings.schema.attributes[drsc_variable].type == u'choice':
            choices = mappings.schema.attributes[drsc_variable].choices
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
                    if choice in row['mapped'].split(','):
                        mapped_value = row['name']
                        mapped_label = row['label']

                mappings_form_rows.append({
                    'variable': attribute.name,
                    'description': attribute.title,
                    'type': mappings.schema.attributes[drsc_variable].type,
                    'site': site,
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
                'site': site,
                'form': schema.name,
                'label': attribute.title,
                'value': u'',
                'mapped_variable': drsc_variable,
                'mapped_label': u'',
                'mapped_value': u''
            })

    return {
        'drsc_form': mappings.schema.name,
        'drsc_publish_date': mappings.schema.publish_date.strftime('%Y-%m-%d'),
        'drsc_form_rows': drsc_form_rows,
        'mappings_form_rows': mappings_form_rows
    }
