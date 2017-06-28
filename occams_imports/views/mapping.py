"""
Perform direct and imputation mappings of Target variables
"""

import json
from operator import itemgetter

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from pyramid.renderers import render_to_response
from sqlalchemy import asc
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import wtforms

from occams_datastore import models as datastore
from occams_studies import models as studies

from .. import models


def update_schema_data(data, schemas, drsc):
    """Converts sql alchemy schema objects to dictionary for rendering"""

    site = u'DRSC' if drsc else u''

    for schema in schemas:
        attributes = []
        for attr in sorted(schema.attributes):
            attribute = {}
            attribute['variable'] = schema.attributes[attr].name
            attribute['label'] = schema.attributes[attr].title
            attribute['datatype'] = schema.attributes[attr].type
            if schema.attributes[attr].type == u'choice':
                choices = []
                for choice in schema.attributes[attr].choices:
                    name = schema.attributes[attr].choices[choice].name
                    title = schema.attributes[attr].choices[choice].title
                    order = schema.attributes[attr].choices[choice].order
                    choices.append(
                        {u'name': name, u'label': title, u'order': order}
                    )
                    # choices need to be sorted for display in mappings table
                    choices = sorted(choices, key=itemgetter('order'))

            else:
                choices = []

            attribute['choices'] = choices
            attributes.append(attribute)

        data['forms'].append({
            u'name': schema.name,
            u'publish_date': schema.publish_date.strftime('%Y-%m-%d'),
            u'attributes': attributes,
            u'site': site
        })

    return data


@view_config(
    route_name='imports.schemas',
    permission='add',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_all_schemas(context, request):
    db_session = request.db_session

    # mappings may only occur with schemas associated with a study
    schemas = (
        db_session.query(datastore.Schema)
        .options(joinedload('attributes').joinedload('choices'))
        .select_from(studies.Study)
        .join(studies.Study.schemata)
        .filter(studies.Study.name != u'drsc')
        .distinct().order_by(datastore.Schema.name).all())

    drsc_schemas = (
        db_session.query(datastore.Schema)
        .options(joinedload('attributes').joinedload('choices'))
        .select_from(studies.Study)
        .join(studies.Study.schemata)
        .filter(studies.Study.name == u'drsc')
        .distinct().order_by(datastore.Schema.name).all())

    data = {}
    data['forms'] = []

    data = update_schema_data(data, schemas, drsc=False)
    data = update_schema_data(data, drsc_schemas, drsc=True)

    return data


@view_config(
    route_name='imports.mappings.direct',
    permission='add',
    request_method='GET',
    renderer='../templates/mapping/direct.pt')
def occams_direct(context, request):
    return {}


@view_config(
    route_name='imports.mappings.imputation',
    permission='add',
    request_method='GET',
    renderer='../templates/mapping/imputation.pt')
def occams_imputation(context, request):
    return {}


@view_config(
    route_name='imports.schemas',
    permission='add',
    request_method='GET',
    xhr=True,
    request_param='vocabulary=available_schemata',
    renderer='json')
def schemas(context, request):
    db_session = request.db_session

    class SearchForm(wtforms.Form):
        term = wtforms.StringField(
            validators=[wtforms.validators.Optional()])

    search_form = SearchForm(request.GET)
    search_form.validate()

    data = search_form.data

    # mappings may only occur with schemas associated with a study
    schemata_query = (
        db_session.query(datastore.Schema)
        .select_from(studies.Study)
        .join(studies.Study.schemata)
        .distinct())

    if data['term']:
        schemata_query = (
            schemata_query
            .filter(datastore.Schema.name.ilike('%{}%'.format(data['term']))))

    schemata_query = (
        schemata_query
        .order_by(datastore.Schema.name)
        .limit(25)
    )

    def schema2json(schema):
        return {
            u'name': schema.name,
            u'publish_date': schema.publish_date,
            u'attributes': [],
        }

    return {
        'schemata': [schema2json(schema) for schema in schemata_query]
    }


@view_config(
    route_name='imports.schemas',
    permission='add',
    request_method='GET',
    xhr=True,
    request_param='vocabulary=available_attributes',
    renderer='json')
def get_attributes(context, request):
    db_session = request.db_session

    class SearchForm(wtforms.Form):
        schema = wtforms.StringField(
            validators=[wtforms.validators.InputRequired()])
        term = wtforms.StringField(
            validators=[wtforms.validators.Optional()])

    search_form = SearchForm(request.GET)

    if not search_form.validate():
        return {}

    data = search_form.data

    attributes_query = (
        db_session.query(datastore.Attribute)
        .options(joinedload('choices'))
        .join(datastore.Schema)
        .filter(datastore.Schema.name == data['schema'])
    )

    if data['term']:
        attributes_query = (
            attributes_query
            .filter(datastore.Attribute.name.ilike(
                '%{}%'.format(data['term']))))

    attributes_query = (
        attributes_query
        .order_by(datastore.Attribute.name)
        .limit(25)
    )

    def choice2json(choice):
        return {
            u'name': choice.name,
            u'label': choice.title,
            u'order': choice.order
        }

    def attribute2json(attribute):
        return {
            'name': attribute.name,
            'title': attribute.title,
            'type': attribute.type,
        }

    return {
        'attributes': [attribute2json(schema) for schema in attributes_query]
    }


@view_config(
    route_name='imports.schemas',
    permission='add',
    request_method='GET',
    xhr=True,
    request_param='vocabulary=available_choices',
    renderer='json')
def get_choices(context, request):
    db_session = request.db_session

    class SearchForm(wtforms.Form):
        schema = wtforms.StringField(
            validators=[wtforms.validators.InputRequired()])
        attribute = wtforms.StringField(
            validators=[wtforms.validators.InputRequired()])
        term = wtforms.StringField(
            validators=[wtforms.validators.Optional()])

    search_form = SearchForm(request.GET)

    if not search_form.validate():
        return {}

    data = search_form.data

    choices_query = (
        db_session.query(datastore.Choice)
        .join(datastore.Attribute)
        .join(datastore.Schema)
        .filter(datastore.Schema.name == data['schema'])
        .filter(datastore.Attribute.name == data['attribute'])
    )

    if data['term']:
        pattern = '%{}%'.format(data['term'])
        choices_query = (
            choices_query
            .filter(
                datastore.Choice.name.ilike(pattern)
                | datastore.Choice.title.ilike(pattern)))

    choices_query = (
        choices_query
        .order_by(datastore.Choice.name)
        .limit(25)
    )

    def choice2json(choice):
        return {
            u'name': choice.name,
            u'title': choice.title,
            u'order': choice.order
        }

    return {
        'choices': [choice2json(choice) for choice in choices_query]
    }


@view_config(
    route_name='imports.mappings.direct.map',
    permission='add',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_direct_map(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    target_study = (
        db_session.query(studies.Study)
        .join(studies.Study.schemata)
        .filter(datastore.Schema.name == request.json['source_schema'])
        .filter(datastore.Schema.publish_date == request.json['source_schema_publish_date']).one())

    data = request.json

    if request.json['choices_mapping']:
        adj_choices_mapping = []
        for mapping in request.json['choices_mapping']:
            for name in mapping['mapped'].split(','):
                adj_choices_mapping.append({'source': name, 'target': mapping['name']})

        data['choices_mapping'] = adj_choices_mapping

    # add default review status to mapping
    status = db_session.query(models.Status).filter_by(name=u'review').one()

    mapped_obj = models.Mapping(
        study=target_study,
        status=status,
        type=u'direct',
        logic=data
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return {'id': mapped_obj.id}


@view_config(
    route_name='imports.mappings.imputation',
    permission='add',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_imputations_map(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    # TODO - find a better way to obtain the site
    schema_obj = request.json['groups'][0]['conversions'][0]['value']['schema']
    study_form_name = schema_obj['name']
    study_form_publish_date = schema_obj['publish_date']
    study = (
        db_session.query(studies.Study)
        .join(studies.Study.schemata)
        .filter(datastore.Schema.name == study_form_name)
        .filter(datastore.Schema.publish_date == study_form_publish_date)).one()

    mapped_attribute = (
        db_session.query(datastore.Attribute)
        .filter(datastore.Attribute.name == request.json['target']['attribute']['name'])
        .filter(datastore.Attribute.schema.has(
            name=request.json['target']['schema']['name'],
            publish_date=request.json['target']['schema']['publish_date']))
        .one())

    mapped_choice_data = request.json.get('targetChoice')

    if mapped_choice_data:
        mapped_choice = mapped_attribute.choices[mapped_choice_data['name']]
    else:
        mapped_choice = None

    logic = {}
    logic['groups'] = request.json['groups']
    logic['condition'] = request.json['condition']
    logic['target_schema'] = request.json['target']['schema']['name']
    logic['target_variable'] = request.json['target']['attribute']['name']
    logic['target_choice'] = request.json.get('targetChoice', {})
    logic['forms'] = []
    for group in request.json['groups']:
        for conversion in group['conversions']:
            if isinstance(conversion['value'], dict):
                form_name = conversion['value']['schema']['name']
                variable = conversion['value']['attribute']['name']
                logic['forms'].append([form_name, variable])

    mapping_id = request.json.get('id')

    if mapping_id:
        status_name = request.json['status']
    else:
        status_name = 'review'

    # add default review status to mapping
    status = db_session.query(models.Status).filter_by(name=status_name).one()

    if mapping_id:
        mapped_obj = db_session.query(models.Mapping).get(mapping_id)
    else:
        mapped_obj = models.Mapping(study=study, type='imputation')
        db_session.add(mapped_obj)

    mapped_obj.status = status
    mapped_obj.description = request.json.get('description', '')
    mapped_obj.logic = logic

    db_session.flush()

    return {'__next__': request.route_path('imports.index')}


@view_config(
    route_name='imports.mapping.status',
    permission='view',
    request_method='GET',
    renderer='json')
def get_status_and_notes(context, request):
    db_session = request.db_session
    mapping_id = int(request.params['id'])

    mapping = db_session.query(models.Mapping).filter_by(id=mapping_id).one()
    status = mapping.status.name
    notes = mapping.notes

    return {'status': status, 'notes': notes}


@view_config(
    route_name='imports.mapping.status',
    permission='approve',
    request_method='PUT',
    renderer='json')
def update_status(context, request):
    check_csrf_token(request)
    db_session = request.db_session
    mapping_id = int(request.params['id'])

    mapping = db_session.query(models.Mapping).filter_by(id=mapping_id).one()
    new_status_name = request.json['status']
    status = db_session.query(models.Status).filter_by(name=new_status_name).one()

    mapping.status = status

    db_session.add(mapping)
    db_session.flush()

    return {}


@view_config(
    route_name='imports.mapping.notes',
    permission='approve',
    request_method='PUT',
    renderer='json')
def update_notes(context, request):
    check_csrf_token(request)
    db_session = request.db_session
    mapping_id = int(request.params['id'])

    mapping = db_session.query(models.Mapping).filter_by(id=mapping_id).one()
    updated_notes = request.json['notes']

    mapping.notes = updated_notes

    db_session.add(mapping)
    db_session.flush()

    return {}


@view_config(
    route_name='imports.mappings.view',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json'
)
def mappings(context, request):
    db_session = request.db_session

    mappings = (
        db_session.query(models.Mapping)
        .order_by(models.Mapping.id))

    data = {}

    if request.has_permission('add'):
        data['$addDirectUrl'] = \
            request.current_route_path(_route_name='imports.mappings.direct')
        data['$addImputationUrl'] = \
            request.current_route_path(_route_name='imports.mappings.imputation')

    if request.has_permission('delete'):
        data['$deleteUrl'] = request.current_route_path()

    data['rows'] = []

    for mapping in mappings:
        row = {}

        row['target_form'] = mapping.logic['target_schema']
        row['target_variable'] = mapping.logic['target_variable']

        # imputation mappings may have multiple forms and variables
        if mapping.type == 'imputation':
            row['forms'] = mapping.logic['forms']

        else:
            row['study_form'] = mapping.logic['source_schema']
            row['study_variable'] = mapping.logic['source_variable']

        row['study'] = mapping.study.title
        row['date_mapped'] = mapping.create_date.date()
        row['mapped_id'] = mapping.id

        row['status'] = mapping.status.name
        row['note'] = mapping.notes

        data['rows'].append(row)

    return data


@view_config(
    route_name='imports.mappings.delete',
    permission='delete',
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

    return {}


def convert_logic(db_session, logic):
    """Converts server side logic to clientside logic."""

    logic = dict(logic)
    logic.pop('forms', None)
    logic['description'] = u''
    logic['targetChoice'] = logic.pop('target_choice')
    logic['groupsLength'] = len(logic['groups'])
    if logic['groupsLength'] > 1:
        logic['hasMultipleGroups'] = True
    else:
        logic['hasMultipleGroups'] = False

    target_schema = (
        db_session.query(datastore.Schema)
        .filter_by(name=logic.pop('target_schema'))
        .order_by(asc(datastore.Schema.publish_date))
    ).limit(1).one()

    target_schema_publish_date = target_schema.publish_date.isoformat()
    target_variable = target_schema.attributes[logic['target_variable']]

    logic['target'] = {}
    logic['target']['schema'] = {}
    logic['target']['schema']['name'] = target_schema.name
    logic['target']['schema']['publish_date'] = target_schema_publish_date

    logic['target']['attribute'] = {}
    logic['target']['attribute']['name'] = target_variable.name
    logic['target']['attribute']['title'] = target_variable.title
    logic['target']['attribute']['type'] = target_variable.type

    if logic['target']['attribute']['type'] == u'choice':
        logic['target']['attribute']['hasChoices'] = True
    else:
        logic['target']['attribute']['hasChoices'] = False

    logic.pop('target_variable')

    return logic


@view_config(
    route_name='imports.mappings.view_mapped',
    permission='view'
)
def view_mappings(context, request):
    """View a mapped imputation. """
    db_session = request.db_session

    mapping_id = int(request.params['id'])
    mapping = db_session.query(models.Mapping).filter_by(id=mapping_id).one()

    if request.has_permission('edit'):
        pass

    if request.has_permission('view'):
        pass

    if mapping.type == u'direct':
        url = '../templates/mapping/direct-view.pt'

        return render_to_response(url, {}, request=request)
    else:
        url = '../templates/mapping/imputation.pt'
        logic = convert_logic(db_session, mapping.logic)

        return render_to_response(url, logic, request=request)

    return {}


@view_config(
    route_name='imports.mappings.view_mapped',
    permission='view',
    xhr=True,
    request_method='GET',
    renderer='json'
)
def view_imputation(context, request):
    """View a mapped imputation. """
    db_session = request.db_session

    mapping_id = int(request.params['id'])
    mapping = db_session.query(models.Mapping).filter_by(id=mapping_id).one()

    if request.has_permission('edit'):
        pass

    if request.has_permission('view'):
        pass

    logic = convert_logic(db_session, mapping.logic)
    logic['id'] = mapping_id
    logic['description'] = mapping.description
    logic['status'] = mapping.status.name

    return logic


@view_config(
    route_name='imports.mapping_detail',
    permission='view',
    renderer='json'
)
def get_schemas_mapped(context, request):
    db_session = request.db_session

    mapping = db_session.query(models.Mapping).filter(
        models.Mapping.id == request.matchdict['mapping']).one()

    study = mapping.study

    mappings_form_rows = []
    target_form_rows = []

    # get site form and choices
    # we need to display the label map on visualization page
    # site labels for choices is not available in json map in mappings tbl
    schema = (
        db_session.query(datastore.Schema)
        .filter_by(
            name=mapping.logic['source_schema'],
            publish_date=mapping.logic['source_schema_publish_date'])
        .one())

    attribute = schema.attributes[mapping.logic['source_variable']]

    target_variable = (
        db_session.query(datastore.Attribute)
        .filter(datastore.Attribute.name == mapping.logic['target_variable'])
        .filter(datastore.Attribute.schema.has(
            name=mapping.logic['target_schema'],
            publish_date=mapping.logic['target_schema_publish_date']))
        .one())

    if target_variable.type == u'choice':
        # data to populate target table
        for choice in target_variable.iterchoices():
            target_form_rows.append({
                'variable': target_variable.name,
                'description': target_variable.title,
                'type': target_variable.type,
                'label': choice.title,
                'key': choice.name,

            })

        for choice in attribute.iterchoices():
            mapped_value = u''
            mapped_label = u''
            for row in mapping.logic['choices_mapping']:
                if choice.name == row['source']:
                    mapped_value = row['target']
                    for target in target_variable.iterchoices():
                        if target.name == mapped_value:
                            mapped_label = target.title

            mappings_form_rows.append({
                'variable': attribute.name,
                'description': attribute.title,
                'type': u'direct',
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
            'description': target_variable.title,
            'type': target_variable.type,
            'label': u'N/A',
            'key': u'N/A',
        })

        mappings_form_rows.append({
            'variable': attribute.name,
            'description': attribute.title,
            'type': target_variable.type,
            'study': study.title,
            'form': schema.name,
            'label': attribute.title,
            'value': u'N/A',
            'mapped_variable': target_variable.name,
            'mapped_label': u'N/A',
            'mapped_value': u'N/A'
        })

    return {
        'target_form': mapping.logic['target_schema'],
        'target_publish_date': mapping.logic['target_schema_publish_date'],
        'target_form_rows': target_form_rows,
        'mappings_form_rows': mappings_form_rows,
        'status': mapping.status.name,
        '$approveUrl': 'FIXME' if request.has_permission('approve') else None
    }
