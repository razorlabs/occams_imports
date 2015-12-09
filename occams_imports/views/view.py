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
    db_session = request.db_session

    mappings = (
        db_session.query(models.Mapping)
        .order_by(models.Mapping.id))

    data = {}
    data['rows'] = []

    for mapping in mappings:
        row = {}

        row['target_form'] = mapping.mapped_attribute.schema.name
        row['target_variable'] = mapping.mapped_attribute.name
        row['study'] = mapping.study.title

        # imputation mappings may have multiple forms and variables
        if mapping.type == 'imputation':
            row['forms'] = mapping.logic['forms']

        else:
            row['study_form'] = mapping.logic['source_schema']['name']
            row['study_variable'] = mapping.logic['source_attribute']

        row['date_mapped'] = mapping.create_date.date()
        row['mapped_id'] = mapping.id

        data['rows'].append(row)

    return data


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
                mapped = db_session.query(models.Mapping).filter(
                    models.Mapping.id == mapping['mappedId']).one()

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

    mapping = db_session.query(models.Mapping).filter(
        models.Mapping.id == request.params['id']).one()

    if mapping.type == u'imputation':
        return render_to_response('../templates/mappings/imputed_mapped.pt',
                                  {}, request=request)

    # site = mapping.site

    study = mapping.study

    mappings_form_rows = []
    target_form_rows = []

    if mapping.type == u'direct':
        # get site form and choices
        # we need to display the label map on visualization page
        # site labels for choices is not available in json map in mappings tbl
        schema = (
            db_session.query(datastore.Schema)
            .filter_by(
                name=mapping.logic['source_schema']['name'],
                publish_date=mapping.logic['source_schema']['publish_date'])
            .one())

        attribute = schema.attributes[mapping.logic['source_attribute']]

        target_variable = mapping.mapped_attribute

        if target_variable.type == u'choice':
            # data to populate target table
            for choice in target_variable.iterchoices():
                target_form_rows.append({
                    'variable': target_variable.name,
                    'description': schema.title,
                    'type': target_variable.type,
                    'confidence': mapping.confidence,
                    'label': choice.title,
                    'key': choice.name,

                })

            for choice in attribute.iterchoices():
                mapped_value = u''
                mapped_label = u''
                for row in mapping.logic['choices_map']:
                    if choice.name in row['mapped'].split(','):
                        mapped_value = row['name']
                        mapped_label = row['label']

                mappings_form_rows.append({
                    'variable': attribute.name,
                    'description': attribute.title,
                    'type': mapping.mapped_attribute.type,
                    'study': study.title,
                    'form': schema.name,
                    'label': choice.title,
                    'value': choice.name,
                    'mapped_variable': target_variable.name,
                    'mapped_label': mapped_label,
                    'mapped_value': mapped_value
                })
        else:
            # no choices processing
            target_form_rows.append({
                'variable': target_variable.name,
                'description': mapping.mapped_attribute.schema.title,
                'type': mapping.mapped_attribute.type,
                'confidence': mapping.confidence,
                'label': u'',
                'key': u'',
            })

            mappings_form_rows.append({
                'variable': attribute.name,
                'description': attribute.title,
                'type': mapping.mapped_attribute.type,
                'site': site.title,
                'form': schema.name,
                'label': attribute.title,
                'value': u'',
                'mapped_variable': target_variable,
                'mapped_label': u'',
                'mapped_value': u''
            })

    return {
        'target_form': mapping.mapped_attribute.schema.name,
        'target_publish_date': mapping.mapped_attribute.schema.publish_date,
        'target_form_rows': target_form_rows,
        'mappings_form_rows': mappings_form_rows
    }
