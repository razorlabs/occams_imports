"""
Insert records to schema and attribute tables.

This data is the structure of the schemas and attributes for forms not the
collected data
"""

from pyramid.view import view_config
from pyramid.session import check_csrf_token

from occams.utils.forms import wtferrors
from occams_datastore import models as datastore
from occams_studies import models as studies
from occams_forms.views.field import FieldFormFactory

from occams_imports import models
from occams_imports.parsers import parse
from occams_imports.parsers import iform_json
from occams_imports.parsers import convert_qds_to_occams


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

    :param records: a list of lists of records from the csv
    :param: force:  a mode where records are inserted into the db even if
                    some records are bypassed because they are invalid
    :param: dry:    no records are inserted into the db.  this is for testing

    :return:  errors dictionary of invalid form datastore.
              these are the records not inserted
    """
    check_csrf_token(request)
    db_session = request.db_session

    dry = None
    forms = []

    site_name = request.POST['site']

    site = (
        db_session.query(studies.Site)
        .filter(studies.Site.name.ilike(site_name))
        .one())

    if request.POST['mode'] == u'dry':
        dry = True

    codebook = request.POST['codebook'].file
    codebook_format = request.matchdict['format']

    if codebook_format == u'iform':
        converted_codebook = iform_json.convert(codebook)
        records = parse.parse(converted_codebook)

    elif codebook_format == u'occams':
        if request.POST['delimiter'] == u'comma':
            delimiter = ','

        elif request.POST['delimiter'] == u'tab':
            delimiter = '\t'

        records = parse.parse(codebook, delimiter=delimiter)

    elif codebook_format == u'qds':
        if request.POST['delimiter'] == u'comma':
            delimiter = ','

        elif request.POST['delimiter'] == u'tab':
            delimiter = '\t'

        converted_codebook = convert_qds_to_occams.convert(
            codebook, delimiter=delimiter)

        records = parse.parse(converted_codebook)

    records = parse.remove_system_entries(records)

    errors = []
    attributes = []

    for record in records:
        # convert boolean type to choice type
        # occams doesn't support boolean form attribute types
        # this feels like it should be in the parse module
        if record['type'] == u'boolean':
            record['type'] = u'choice'

        choices = parse.get_choices(record['choices'])
        record['choices'] = choices

        schema = datastore.Schema(
            name=record['schema_name'],
            title=record['schema_title'],
            publish_date=record['publish_date']
        )

        form_data = {'name': record['schema_name'],
                     'title': record['schema_title'],
                     'publish_date': record['publish_date']}

        if form_data not in forms:
            forms.append(form_data)

        FieldForm = FieldFormFactory(context=schema, request=request)
        form = FieldForm.from_json(record)

        if not form.validate():
            output = {}
            output['errors'] = wtferrors(form)
            output['schema_name'] = record['schema_name']
            output['schema_title'] = record['schema_title']
            output['name'] = record['name']
            output['title'] = record['title']
            errors.append(output)

        else:
            attributes.append(datastore.Attribute(
                name=record['name'],
                title=record['title'],
                description=record['description'],
                is_required=record['is_required'],
                is_collection=record['is_collection'],
                is_private=record['is_private'],
                type=record['type'],
                order=record['order'],
                schema=schema,
                choices=choices
            ))

    # get the first schema from the list
    schema = attributes[0].schema

    fields_inserted = 0
    forms_inserted = 0
    if not dry and not errors:
        attr_dict = {}
        for attribute in attributes:
            flushed = False
            if attribute.schema.name == schema.name:
                # remove unnecessary schema attr
                del(attribute.schema)

                attr_dict[attribute.name] = attribute

                fields_inserted += 1
            else:
                schema = datastore.Schema(
                    name=schema.name,
                    title=schema.title,
                    publish_date=schema.publish_date,
                    attributes=attr_dict
                )

                imported = models.Import(
                    site=site,
                    schema=schema
                )

                db_session.add(imported)

                db_session.flush()

                forms_inserted += 1

                flushed = True

                schema = attribute.schema

                attr_dict = {}

                # remove unnecessary schema attr
                del(attribute.schema)

                attr_dict[attribute.name] = attribute

        if not flushed:
            schema = datastore.Schema(
                name=schema.name,
                title=schema.title,
                publish_date=schema.publish_date,
                attributes=attr_dict
            )

            imported = models.Import(
                site=site,
                schema=schema
            )

            db_session.add(imported)

            db_session.flush()

            forms_inserted += 1

    fields_evaluated = len(records)
    error_count = len(errors)

    return {
        'fields_evaluated': fields_evaluated,
        'errors': errors,
        'error_count': error_count,
        'fields_inserted': fields_inserted,
        'forms_inserted': forms_inserted,
        'forms': forms
    }
