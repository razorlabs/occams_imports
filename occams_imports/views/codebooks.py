"""
Insert records to schema and attribute tables.

This data is the structure of the schemas and attributes for forms not the
collected data
"""

from pyramid.view import view_config
from pyramid.session import check_csrf_token

from sqlalchemy.sql import exists
import unicodecsv as csv

from occams.utils.forms import wtferrors
from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_forms.views.field import FieldFormFactory
from occams_forms.views.form import FormFormFactory

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


def process_import(schema, attr_dict, study, db_session):
    """
    Insert import, schema, and attrs to datastore

    :schema: datastore schema object
    :attr_dict: dict of attributes to be bound to schema
    :study: study object
    :db_session: required for db inserts

    :return: None
    """
    schema.attributes = attr_dict
    study.schemata.add(schema)

    imported = models.Import(
        study=study,
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
        schema_dict = {
            'name': record['schema_name'],
            'title': record['schema_title'],
            'publish_date': record['publish_date'].strftime('%Y-%m-%d')
        }

        FormForm = FormFormFactory(context=None, request=request)
        form_form = FormForm.from_json(schema_dict)

        if not form_form.validate():
            schema_error = {}
            schema_error['errors'] = wtferrors(form_form)
            schema_error['schema_name'] = schema_dict['name']
            schema_error['schema_title'] = schema_dict['title']
            schema_error['name'] = 'N/A'
            schema_error['title'] = 'N/A'
            errors.append(schema_error)

        else:
            schema = datastore.Schema.from_json(schema_dict)

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


def group_imports_by_schema(imports, study, db_session):
    """
    Group attributes by schema and process

    :imports: list of tuples, 1st element is an attribute, 2nd is a schema
    :study: study of the import
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
            process_import(current_schema, attr_dict, study, db_session)
            current_schema = schema
            attr_dict = {}
            attr_dict[attribute.name] = attribute
            fields_inserted += 1

    if attr_dict:
        process_import(current_schema, attr_dict, study, db_session)

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


def convert_delimiter(delimiter):
    """
    Convert delimiter to match csv dialect

    :delimiter: delimiter as selected from the UI

    :return: delimiter is the csv dialect format
    """
    if delimiter == u'comma':
        delimiter = ','
    elif delimiter == u'tab':
        delimiter = '\t'

    return delimiter


def validate_delimiter(delimiter, codebook):
    """
    Validate the selected delimiter matches the sniffed delimeter

    :delimiter: delimiter as selected from the UI
    :codebook: open file object for reading

    :return: boolean of delimiter mismatch and errors list
    """
    errors = []
    delimiter_mismatch = False
    codebook.readline()
    dialect = csv.Sniffer().sniff(codebook.readline())
    sniffed_delimiter = dialect.delimiter

    if delimiter != sniffed_delimiter:
        error = {
            'errors': u"Selected delimiter doesn't match file delimiter",
            'schema_name': 'N/A',
            'schema_title': 'N/A',
            'name': 'N/A',
            'title': 'N/A'
        }

        delimiter_mismatch = True
        errors.append(error)

    codebook.seek(0)

    return delimiter_mismatch, errors


@view_config(
    route_name='imports.codebooks_occams',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/occams_codebook.pt')
def occams(context, request):
    db_session = request.db_session

    all_studies = (
        db_session.query(studies.Study).all()
    )

    return {'study_options': [study.title for study in all_studies]}


@view_config(
    route_name='imports.codebooks_iform',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/iform_codebook.pt')
def iform(context, request):
    db_session = request.db_session

    all_studies = (
        db_session.query(studies.Study).all()
    )

    return {'study_options': [study.title for study in all_studies]}


@view_config(
    route_name='imports.codebooks_qds',
    permission='import',
    request_method='GET',
    renderer='../templates/codebooks/qds_codebook.pt')
def qds(context, request):
    db_session = request.db_session

    all_studies = (
        db_session.query(studies.Study).all()
    )

    return {'study_options': [study.title for study in all_studies]}


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

    study_name = request.POST['site']

    study = (
        db_session.query(studies.Study)
        .filter(studies.Study.title == study_name)
        .one())

    dry = request.POST['mode'] == u'dry'
    codebook = request.POST['codebook'].file
    codebook_format = request.matchdict['format']
    delimiter = request.POST.get('delimiter', ',')
    delimiter = convert_delimiter(delimiter)

    if codebook_format != u'iform':
        delimiter_mismatch, errors = validate_delimiter(delimiter, codebook)
    else:
        delimiter_mismatch = None
        errors = []

    # if delimiter isn't correct, don't process the file
    if delimiter_mismatch:
        records = []
        fields_inserted = 0
        forms = []

    else:
        records = parse.parse_dispatch(codebook, codebook_format, delimiter)
        records = parse.remove_system_entries(records)

        errors, imports, forms = validate_populate_imports(request, records)
        errors = is_duplicate_schema(forms, errors, db_session)

        fields_inserted = 0
        if not dry and not errors:
            fields_inserted = group_imports_by_schema(imports, study, db_session)

    return {
        'fields_evaluated': len(records),
        'errors': errors,
        'error_count': len(errors),
        'fields_inserted': fields_inserted,
        'forms_inserted': len(forms) if not dry and not errors else 0,
        'forms': forms
    }
