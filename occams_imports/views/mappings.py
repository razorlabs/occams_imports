"""
Perform direct and imputation mappings of Target variables
"""

from operator import itemgetter

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy.orm import joinedload
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
    renderer='../templates/mappings/mappings.pt')
def occams_direct(context, request):
    return {}


@view_config(
    route_name='imports.mappings.imputation',
    permission='add',
    request_method='GET',
    renderer='../templates/mappings/imputations.pt')
def occams_imputation(context, request):
    return {}


@view_config(
    route_name='imports.schemas',
    permission='add',
    request_method='GET',
    xhr=True,
    request_param='vocabulary=available_schemata',
    renderer='json')
def get_schemas(context, request):
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

    # add default review status to mapping
    status = db_session.query(models.Status).filter_by(name='review').one()

    mapped_obj = models.Mapping(
        study=study,
        type='imputation',
        status=status,
        description=request.json['description'],
        logic=logic
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return {'__next__': request.route_path('imports.index')}


@view_config(
    route_name='imports.mapping.status',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_status_and_notes(context, request):
    check_csrf_token(request)
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
    xhr=True,
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
    xhr=True,
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
