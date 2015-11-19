"""
Perform direct and imputation mappings of DRSC variables
"""

import json
from operator import itemgetter

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy.orm import joinedload
import wtforms

from occams_datastore import models as datastore
from occams_studies import models as studies

from .. import models


def update_schema_data(data, schemas, site=None):
    """Converts sql alchemy schema objects to dictionary for rendering"""

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
            u'site': site.title if site else ''
        })

    return data


@view_config(
    route_name='imports.schemas',
    permission='view',
    request_method='GET',
    xhr=True,
    renderer='json')
def get_all_schemas(context, request):
    db_session = request.db_session

    target_site = (
        db_session.query(studies.Site)
        .filter_by(name=u'drsc')
        .one())

    schemas = db_session.query(datastore.Schema).options(
        joinedload('attributes').joinedload('choices')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site != target_site).order_by(datastore.Schema.name).all()

    drsc_schemas = db_session.query(datastore.Schema).options(
        joinedload('attributes').joinedload('choices')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site == target_site).all()

    data = {}
    data['forms'] = []

    data = update_schema_data(data, schemas, None)
    data = update_schema_data(data, drsc_schemas,  target_site)

    return json.dumps(data)


@view_config(
    route_name='imports.mappings.direct',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mappings.pt')
def occams_direct(context, request):
    return {}


@view_config(
    route_name='imports.mappings.imputation',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/imputations.pt')
def occams_imputation(context, request):
    return {}


@view_config(
    route_name='imports.mappings.imputation.demo',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/imputation_demo.pt')
def occams_imputation_demo(context, request):
    return {}


@view_config(
    route_name='imports.schemas',
    permission='view',
    request_method='GET',
    xhr=True,
    request_param='vocabulary=available_schemata',
    renderer='json')
def get_schemas(context, request):
    db_session = request.db_session

    class SearchForm(wtforms.Form):
        is_target = wtforms.BooleanField(
            validators=[wtforms.validators.Optional()])
        term = wtforms.StringField(
            validators=[wtforms.validators.Optional()])

    search_form = SearchForm(request.GET)
    search_form.validate()

    data = search_form.data

    schemata_query = (
        db_session.query(datastore.Schema)
        .filter(datastore.Schema.id == models.Import.schema_id)
    )

    target_site = db_session.query(studies.Site).filter_by(name='drsc').one()

    # TODO: Need to implement sites at the form level
    if data['is_target']:
        schemata_query = schemata_query.filter(models.Import.site == target_site)
    else:
        schemata_query = schemata_query.filter(models.Import.site != target_site)

    if data['term']:
        schemata_query = (
            schemata_query
            .filter(models.Schema.name.ilike('%{}%'.format(data['term']))))

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
    permission='view',
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
    permission='view',
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
    permission='view',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_direct_map(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    target_site = (
        db_session.query(studies.Site)
        .select_from(models.Import)
        .join(models.Import.site)
        .filter(models.Import.schema.has(
            name=request.json['site']['name'],
            publish_date=request.json['site']['publish_date']))
        .one())

    mapped_attribute = (
        db_session.query(datastore.Attribute)
        .filter(
            (datastore.Attribute.name == request.json['selected_drsc']['variable'])
            & (datastore.Attribute.schema.has(
                name=request.json['drsc']['name'],
                publish_date=request.json['drsc']['publish_date'])))
        .one())

    logic = {
        'source_schema':  {
            'name': request.json['site']['name'],
            'publish_date': request.json['site']['publish_date']
        },
        'source_attribute': request.json['selected']['variable']
    }

    if u'choices' not in request.json['selected_drsc']:
        logic['choices_map'] = None
    else:
        logic['choices_map'] = request.json['selected_drsc']['choices']

    mapped_obj = models.Mapping(
        site=target_site,
        mapped_attribute=mapped_attribute,
        type=u'direct',
        confidence=request.json['confidence'],
        logic=logic
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return json.dumps({'id': mapped_obj.id})


@view_config(
    route_name='imports.mappings.imputation',
    permission='view',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_imputations_map(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    # TODO - find a better way to obtain the site
    schema_obj = request.json[u'groups'][0][u'conversions'][0][u'value'][u'schema']
    site_name = schema_obj[u'name']
    site_publish_date = schema_obj['publish_date']
    site_import = db_session.query(models.Import).filter(
        datastore.Schema.name == site_name).filter(
        datastore.Schema.publish_date == site_publish_date).filter(
        datastore.Schema.id == models.Import.schema_id).one()
    site = site_import.site

    mapped_attribute = (
        db_session.query(datastore.Attribute)
        .filter(datastore.Attribute.name == request.json[u'target'][u'attribute']['name'])
        .filter(datastore.Attribute.schema.has(
            name=request.json[u'target'][u'schema']['name'],
            publish_date=request.json[u'target'][u'schema']['publish_date']))
        .one())

    mapped_choice_data = request.json.get('targetChoice')

    if mapped_choice_data:
        mapped_choice = mapped_attribute.choices[mapped_choice_data['name']]
    else:
        mapped_choice = None

    logic = {}
    logic['groups'] = request.json[u'groups']
    logic['condition'] = request.json[u'condition']
    logic['forms'] = []
    for group in request.json[u'groups']:
        for conversion in group[u'conversions']:
            if isinstance(conversion[u'value'], dict):
                form_name = conversion[u'value'][u'schema'][u'name']
                variable = conversion[u'value'][u'attribute'][u'name']
                logic['forms'].append([form_name, variable])

    mapped_obj = models.Mapping(
        site=site,
        mapped_attribute=mapped_attribute,
        mapped_choice=mapped_choice,
        confidence=request.json[u'confidence'],
        type=u'imputation',
        description=request.json['description'],
        logic=logic
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return {'__next__': request.route_path('imports.index')}
