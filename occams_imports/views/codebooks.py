"""
Insert records to schema and attribute tables.

This data is the structure of the schemas and attributes for forms not the
collected data
"""

from pyramid.httpexceptions import HTTPBadRequest, HTTPOk
from pyramid.renderers import render_to_response
from pyramid.session import check_csrf_token
from pyramid.view import view_config
import sqlalchemy as sa
from sqlalchemy import orm
import wtforms
from wtforms.ext.dateutil.fields import DateField

from occams.utils.forms import wtferrors, ModelField, Form
from occams_forms.renderers import \
    make_form, render_form, entity_data, \
    form2json, version2json

from .. import _, models, Session


def get_choices(raw_choices):
    from occams_datastore import models as datastore
    """
    sample input = [[u'0', label], [u'1': label2]]

    sample output = {
        u'0': models.Choice(
            name=u'1',
            title=u'label',
            order=0
            )
        u'1': models.Choice(
            name=u'1',
            title=u'label2',
            order=1
            )
    }

    :param raw_choices: a dict of choices...key is option, value is label

    :return: a dictionary of choice datastore objects
    """
    choices = {}
    if raw_choices:

        for i, item in enumerate(raw_choices):
            code = item[0]
            label = item[1]
            choices[code] = datastore.Choice(
                name=code.strip(),
                title=label.strip(),
                order=i
            )

    return choices


@view_config(
    route_name='imports.codebooks_occams',
    permission='view',
    request_method='GET',
    renderer='../templates/codebooks/occams_codebook.pt')
def occams(context, request):
    return {}


@view_config(
    route_name='imports.codebooks_iform',
    permission='view',
    request_method='GET',
    renderer='../templates/codebooks/iform_codebook.pt')
def iform(context, request):
    return {}


@view_config(
    route_name='imports.codebooks_occams_status',
    permission='view',
    renderer='../templates/codebooks/occams_status.pt')
def insert_occams(context, request):
    import sys
    import argparse

    from occams import Session
    from occams_datastore import models as datastore
    from occams_forms.views.field import FieldFormFactory
    from occams.utils.forms import wtferrors
    from occams_imports.parsers import parse

    """
    Insert appropriate records to the database

    :param records: a list of lists of records from the csv
    :param: force:  a mode where records are inserted into the db even if
                    some records are bypassed because they are invalid
    :param: dry:    no records are inserted into the db.  this is for testing

    :return:  errors dictionary of invalid form datastore.
              these are the records not inserted
    """
    # codebook = '/Users/jkrooskos/Documents/occams/src/occams_imports/occams_imports/views/output.csv'
    # records = parse.parse(codebook)
    # records = parse.remove_system_entries(records)

    # force = True
    # dry = None

    # schemas = {}
    # errors = []
    # for record in records:
    #     # if it's not a system entry, cache and insert into db
    #     # from pdb import set_trace; set_trace()
    #     if (
    #         record['schema_name'],
    #         record['schema_title'],
    #         record['publish_date']
    #     ) not in schemas:
    #         # create schema object
    #         schema = datastore.Schema(
    #             name=record['schema_name'],
    #             title=record['schema_title'],
    #             publish_date=record['publish_date']
    #         )
    #         Session.add(schema)
    #         Session.flush()

    #         # add schema to cache
    #         schemas[(record['schema_name'],
    #                 record['schema_title'],
    #                 record['publish_date'])] = schema

    #     else:
    #         # get schemas from the cache
    #         schema = schemas[(record['schema_name'],
    #                           record['schema_title'],
    #                           record['publish_date'])]

    #     # convert boolean type to choice type
    #     # occams doesn't support boolean form attribute types
    #     if record['type'] == u'boolean':
    #         record['type'] = u'choice'

    #     choices = get_choices(record['choices'])
    #     record['choices'] = choices

    #     FieldForm = FieldFormFactory(context=schema, dbsession=Session)
    #     form = FieldForm.from_json(record)

    #     if form.validate():
    #         Session.add(datastore.Attribute(
    #             name=record['name'],
    #             title=record['title'],
    #             description=record['description'],
    #             is_required=record['is_required'],
    #             is_collection=record['is_collection'],
    #             is_private=record['is_private'],
    #             type=record['type'],
    #             order=record['order'],
    #             schema=schema,
    #             choices=choices
    #         ))

    #     else:
    #         output = {}
    #         output['errors'] = wtferrors(form)
    #         output['form'] = record
    #         errors.append(output)

    #     if dry:
    #         Session.rollback()
    #     elif force:
    #         Session.flush()
    #     elif errors:
    #         Session.rollback()
    #     else:
    #         Session.flush()

    return {}


@view_config(
    route_name='imports.codebooks_iform_status',
    permission='view',
    request_method='POST')
def insert_iform(context, request):
    from datetime import datetime

    from occams_datastore import models as datastore
    from occams_forms.views.field import FieldFormFactory
    from occams_imports.parsers import parse
    from occams_imports.parsers import convert_iform_to_occams as iform
    """
    Insert appropriate records to the database

    :param records: a list of lists of records from the csv
    :param: force:  a mode where records are inserted into the db even if
                    some records are bypassed because they are invalid
    :param: dry:    no records are inserted into the db.  this is for testing

    :return:  errors dictionary of invalid form datastore.
              these are the records not inserted
    """
    dry = None

    if request.POST['mode'] == u'dry':
        dry = True

    schema_name = request.POST['schema_name']
    schema_title = request.POST['schema_title']

    publish_date = request.POST['publish_date']
    publish_date = datetime.strptime(publish_date, '%Y-%m-%d').date()

    codebook = request.POST['codebook'].file

    converted_codebook = iform.convert(
        schema_name, schema_title, publish_date, codebook)

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

        choices = get_choices(record['choices'])
        record['choices'] = choices

        schema = datastore.Schema(
            name=record['schema_name'],
            title=record['schema_title'],
            publish_date=record['publish_date']
        )

        FieldForm = FieldFormFactory(context=schema, dbsession=Session)
        form = FieldForm.from_json(record)

        if not form.validate():
            output = {}
            output['errors'] = wtferrors(form)
            output['schema_name'] = record['schema_name']
            output['schema_title'] = record['schema_title']
            output['name'] = record['name']
            output['title'] = record['title']
            errors.append(output)

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

    if not dry and not errors:
        attr_dict = {}
        for attribute in attributes:
            flushed = False
            if attribute.schema.name == schema.name:
                # remove unnecessary schema attr
                del(attribute.schema)

                attr_dict[attribute.name] = attribute
            else:
                Session.add(datastore.Schema(
                    name=schema.name,
                    title=schema.title,
                    publish_date=schema.publish_date,
                    attributes=attr_dict
                ))

                Session.flush()

                flushed = True

                schema = attribute.schema

                attr_dict = {}

                # remove unnecessary schema attr
                del(attribute.schema)

                attr_dict[attribute.name] = attribute

        if not flushed:
            Session.add(datastore.Schema(
                name=schema.name,
                title=schema.title,
                publish_date=schema.publish_date,
                attributes=attr_dict
            ))

            Session.flush()

    if records:
        record_count = len(records)
    else:
        record_count = 0

    if errors:
        error_count = len(errors)
    else:
        error_count = 0

    return render_to_response(
        '../templates/codebooks/status.pt',
        {'record_count': record_count,
         'errors': errors,
         'error_count': error_count},
         request=request)
