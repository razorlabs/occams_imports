"""
Perform direct and imputation mappings of DRSC variables
"""

from datetime import datetime
import json
from operator import itemgetter

from pyramid.view import view_config
from pyramid.session import check_csrf_token
from sqlalchemy.orm import joinedload
import wtforms

from occams_datastore import models as datastore
from occams_imports import models as models



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

    # TODO: Need to implement sites at the form level
    if data['is_target']:
        schemata_query = schemata_query.filter(models.Import.site == 'DRSC')
    else:
        schemata_query = schemata_query.filter(models.Import.site != 'DRSC')

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
            'site': u'DRSC' if data['is_target'] else u''
        }

    return {
        'forms': [schema2json(schema) for schema in schemata_query]
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
            'variable': attribute.name,
            'label': attribute.title,
            'datatype': attribute.type,
            'choices': [
                choice2json(choice) for choice in attribute.iterchoices()]
        }

    return {
        'attributes': [attribute2json(schema) for schema in attributes_query]
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

    site_import = db_session.query(models.Import).filter(
        datastore.Schema.name == request.json['site']['name']).filter(
        datastore.Schema.publish_date == request.json['site']['publish_date']).filter(
        datastore.Schema.id == models.Import.schema_id).one()

    site = site_import.site

    mapping = {}
    mapping['drsc_name'] = request.json['drsc']['name']
    mapping['drsc_publish_date'] = request.json['drsc']['publish_date']
    mapping['drsc_variable'] = request.json['selected_drsc']['variable']
    mapping['drsc_label'] = request.json['selected_drsc']['label']
    mapping['site'] = site

    mapping['mapping_type'] = u'direct'

    mapping['mapping'] = {}
    mapping['mapping']['confidence'] = request.json['confidence']
    mapping['mapping']['name'] = request.json['site']['name']
    mapping['mapping']['publish_date'] = request.json['site']['publish_date']
    mapping['mapping']['variable'] = request.json['selected']['variable']
    mapping['mapping']['label'] = request.json['selected']['label']

    if u'choices' not in request.json['selected_drsc']:
        mapping['mapping']['choices_map'] = None
    else:
        mapping['mapping']['choices_map'] = request.json['selected_drsc']['choices']

    publish_date = datetime.strptime(
        request.json['drsc']['publish_date'], '%Y-%m-%d')

    schema = db_session.query(models.Schema).filter(
        datastore.Schema.name == request.json['drsc']['name'],
        datastore.Schema.publish_date == publish_date.date()
    ).one()

    mapped_obj = models.Mapper(
        schema=schema,
        mapped=mapping
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return json.dumps({'id': mapped_obj.id})


@view_config(
    route_name='imports.mappings.imputation.map',
    permission='view',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_imputations_map(context, request):
    check_csrf_token(request)
    db_session = request.db_session

    site_name = request.json['site']['name']
    site_publish_date = request.json['site']['publish_date']

    site_import = db_session.query(models.Import).filter(
        datastore.Schema.name == site_name).filter(
        datastore.Schema.publish_date == site_publish_date).filter(
        datastore.Schema.id == models.Import.schema_id).one()

    site = site_import.site

    mapping = {}
    mapping['drsc_name'] = request.json['drsc']['name']
    mapping['drsc_publish_date'] = request.json['drsc']['publish_date']
    mapping['drsc_variable'] = request.json['selected_drsc']['variable']
    mapping['drsc_label'] = request.json['selected_drsc']['label']
    mapping['site'] = site

    mapping['mapping_type'] = u'imputation'

    mapping['mapping'] = {}
    mapping['mapping']['confidence'] = request.json['confidence']
    mapping['mapping']['conversions'] = request.json['conversions']
    mapping['mapping']['maps_to'] = request.json['maps_to']
    selected_comparison = request.json['selected_comparison_condition']
    mapping['mapping']['selected_comparison_condition'] = selected_comparison
    mapping['mapping']['logical'] = request.json['logical']
    mapping['mapping']['comparison'] = request.json['comparison']

    mapping['mapping']['forms'] = []

    for conversion in request.json['conversions']:
        form_name = conversion['selectedForm']['name']
        variable = conversion['selectedAttribute']['variable']
        mapping['mapping']['forms'].append([form_name, variable])

    publish_date = datetime.strptime(
        request.json['drsc']['publish_date'], '%Y-%m-%d')

    schema = db_session.query(models.Schema).filter(
        datastore.Schema.name == request.json['drsc']['name'],
        datastore.Schema.publish_date == publish_date.date()
    ).one()

    mapped_obj = models.Mapper(
        schema=schema,
        mapped=mapping
    )

    db_session.add(mapped_obj)
    db_session.flush()

    return json.dumps({})
