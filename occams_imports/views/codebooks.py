"""
Insert records to schema and attribute tables.

This data is the structure of the schemas and attributes for forms not the
collected data
"""

from pyramid.view import view_config
from pyramid.session import check_csrf_token

from sqlalchemy.sql import exists

from occams.utils.forms import wtferrors
from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_forms.views.field import FieldFormFactory

from occams_imports import models
from occams_imports.parsers import parse


def log_errors(errors, record):
    """
    Return error template dict

    :errors: wtf form errors
    :record: line in csv being processed

    :return: error template data
    """
    output = {}
    output['errors'] = errors
    output['schema_name'] = record['schema_name']
    output['schema_title'] = record['schema_title']
    output['name'] = record['name']
    output['title'] = record['title']

    return output


def process_import(schema, attr_dict, site, db_session):
    """
    Insert import, schema, and attrs to datastore

    :schema: datastore schema object
    :attr_dict: dict of attributes to be bound to schema
    :site: studies site object
    :db_session: required for db inserts

    :return: None
    """
    schema.attributes = attr_dict

    imported = models.Import(
        site=site,
        schema=schema
    )

    db_session.add(imported)
    db_session.flush()


def validate_populate_imports(request, records):
    """
    Return list of errors, imports and forms

    :request: request obj
    :records: a list of csv row data

    :return: errors, imports, and forms for template rendering
    """
    errors, imports, forms = ([], [], [])
    for record in records:
        schema = datastore.Schema(
            name=record['schema_name'],
            title=record['schema_title'],
            publish_date=record['publish_date']
        )

        if schema.to_json() not in forms:
            forms.append(schema.to_json())

        choices = parse.get_choices(record['choices'])
        # below needed because we are calling from_json on record
        record['choices'] = choices
        FieldForm = FieldFormFactory(context=schema, request=request)
        form = FieldForm.from_json(record)

        if not form.validate():
            output = log_errors(wtferrors(form), record)
            errors.append(output)

        else:
            imports.append((datastore.Attribute(
                name=record['name'],
                title=record['title'],
                description=record['description'],
                is_required=record['is_required'],
                is_collection=record['is_collection'],
                is_private=record['is_private'],
                type=record['type'],
                order=record['order'],
                choices=choices
            ), schema))

    return errors, imports, forms


def group_imports_by_schema(imports, site, db_session):
    """
    Group attributes by schema and process

    :imports: list of tuples, 1st element is an attribute, 2nd is a schema
    :site: site of the import
    :db_session: required for db inserts

    :return: count of fields inserted
    """
    current_schema = imports[0][1]
    fields_inserted = 0
    attr_dict = {}
    for attribute, schema in imports:
        if schema.name == current_schema.name:
            attr_dict[attribute.name] = attribute
            fields_inserted += 1
        else:
            process_import(current_schema, attr_dict, site, db_session)
            current_schema = schema
            attr_dict = {}
            attr_dict[attribute.name] = attribute
            fields_inserted += 1

    if attr_dict:
        process_import(current_schema, attr_dict, site, db_session)

    return fields_inserted


def is_duplicate_schema(forms, errors, db_session):
    """
    Test for duplicate schema in the db

    :forms: A list of forms represented by dictionaries
    :errors: A list of dictionaries of error datastore
    :db_session: required for db operations

    :return: updated error list
    """
    forms = get_unique_forms(forms)

    for form in forms:
        name = form[0]
        title = form[1]
        publish_date = form[2]
        form_exists = (
            db_session.query(
                exists()
                .where(datastore.Schema.name == name)
                .where(datastore.Schema.title == title)
                .where(datastore.Schema.publish_date == publish_date)).scalar()
        )

        if form_exists:
            errors.append(
                {
                    'schema_name': name,
                    'schema_title': title,
                    'name': u'N/A',
                    'title': u'N/A',
                    'errors': 'Duplicate schema -  already exists in the db'
                }
            )

    return errors


def get_unique_forms(forms):
    """
    From the forms dict, return a list of dictionaries of unique forms

    :forms: A list of forms represented by dictionaries

    :return: a list of tuples of unique forms from forms list
    """
    unique_forms = []
    for form in forms:
        unique_forms.append((form['name'], form['title'], form['publish_date']))

    return list(set(unique_forms))


@view_config(
    route_name='imports.codebooks_occams',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/occams_codebook.pt')
def occams(context, request):
    return {}


@view_config(
    route_name='imports.codebooks_iform',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/iform_codebook.pt')
def iform(context, request):
    return {}


@view_config(
    route_name='imports.codebooks_qds',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/qds_codebook.pt')
def qds(context, request):
    return {}


@view_config(
    route_name='imports.codebooks_status',
    permission='import',
    request_method='POST',
    renderer='../templates/codebooks/status.pt')
def insert_codebooks(context, request):
    """
    Insert appropriate records to the database
    """
    check_csrf_token(request)
    db_session = request.db_session

    site_name = request.POST['site']

    site = (
        db_session.query(studies.Site)
        .filter(studies.Site.name.ilike(site_name))
        .one())

    dry = request.POST['mode'] == u'dry'
    codebook = request.POST['codebook'].file
    codebook_format = request.matchdict['format']
    delimiter = request.POST.get('delimiter', ',')

    records = parse.parse_dispatch(codebook, codebook_format, delimiter)
    records = parse.remove_system_entries(records)

    errors, imports, forms = validate_populate_imports(request, records)
    errors = is_duplicate_schema(forms, errors, db_session)

    fields_inserted = 0
    if not dry and not errors:
        fields_inserted = group_imports_by_schema(imports, site, db_session)

    return {
        'fields_evaluated': len(records),
        'errors': errors,
        'error_count': len(errors),
        'fields_inserted': fields_inserted,
        'forms_inserted': len(forms) if not dry and not errors else 0,
        'forms': forms
    }
