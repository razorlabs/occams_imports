"""
Perform direct and imputation mappings of DRSC variables
"""

from pyramid.view import view_config
from pyramid.session import check_csrf_token


def update_schema_data(data, schemas, drsc):
    """Converts sql alchemy schema objects to dictionary for rendering"""
    from operator import itemgetter

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
    renderer='json')
def get_schemas(context, request):
    import json
    from sqlalchemy.orm import joinedload
    from occams_datastore import models as datastore
    from occams_imports import models as models

    check_csrf_token(request)
    db_session = request.db_session

    schemas = db_session.query(datastore.Schema).options(
        joinedload('attributes').joinedload('choices')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site != 'DRSC').order_by(datastore.Schema.name).all()

    drsc_schemas = db_session.query(datastore.Schema).options(
        joinedload('attributes').joinedload('choices')).filter(
        datastore.Schema.id == models.Import.schema_id).filter(
        models.Import.site == 'DRSC').all()

    data = {}
    data['forms'] = []

    data = update_schema_data(data, schemas, drsc=False)
    data = update_schema_data(data, drsc_schemas, drsc=True)

    return json.dumps(data)


@view_config(
    route_name='imports.mappings.direct.map',
    permission='view',
    request_method='POST',
    xhr=True,
    renderer='json')
def mappings_direct_map(context, request):
    import json
    from datetime import datetime

    from occams_datastore import models as datastore
    from occams_imports import models as models

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
    import json
    from datetime import datetime

    from occams_datastore import models as datastore
    from occams_imports import models as models

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
