"""
Table views

Each collaborating site's project has specific tables associated.

"""

from datetime import date

import colander
from pyramid.httpexceptions import HTTPBadRequest, HTTPSeeOther
from pyramid.session import check_csrf_token
from pyramid.view import view_config

from .. import models
from ..serializers import strip_whitespace
from ..traversal import traversed


@view_config(
    route_name='imports.table_list',
    permission='add',
    request_method='GET',
    renderer='json'
)
def list_(context, request):
    result = {}

    project = context.__parent__

    this_url = request.route_path('imports.table_list', project=project.name)

    if request.has_permission('add'):
        result['$addUrl'] = this_url

    if request.has_permission('delete'):
        result['$deleteUrl'] = this_url

    result['items'] = [
        get(traversed(table, context), request)
        for table in project.schemata
        if request.has_permission('view', table)
    ]

    return result


@view_config(
    route_name='imports.table_detail',
    permission='add',
    request_method='GET',
    renderer='json'
)
def get(context, request):

    project = context.__parent__.__parent__

    this_url = request.route_path(
        'imports.table_detail',
        project=project.name,
        table=context.name
    )

    result = {}

    if request.has_permission('edit', context):
        result['$editUrl'] = this_url

    result.update({
        '$url': this_url,
        'name': context.name,
        'title': context.title,
    })

    return result


#@colander.deferred
#def study_name_validator(node, kw):
    #project = kw['project']
    #db_session = kw['request'].db_session

    #def unique(node, value):
        #query = db_session.query(models.Project).filter_by(name=value)

        #if project is not None:
            #query = query.filter(models.Project.id != project.id)

        #exists = db_session.query(query.exists).scalar()

        #if exists:
            #raise colander.Invalid(node, '%r already exists' % value)

    #validators = colander.All(
        #colander.Length(min=1, max=8),
        #unique
    #)

    #return validators


#class ProjectSchema(colander.MappingSchema):

    #name = colander.SchemaNode(
        #colander.String(),
        #preparer=strip_whitespace,
        #validator=study_name_validator
    #)

    #title = colander.SchemaNode(
        #colander.String(),
        #preparer=strip_whitespace,
        #validator=colander.Length(min=1, max=32)
    #)


#@view_config(
    #route_name='imports.project_list',
    #permission='add',
    #request_method='POST',
    #renderer='json'
#)
#@view_config(
    #route_name='imports.project_detail',
    #permission='add',
    #request_method='PATCH',
    #renderer='json'
#)
#def patch(context, request):
    #check_csrf_token(request)
    #db_session = request.db_session

    #is_new = isinstance(context, models.ProjectFactory)
    #project = context if not is_new else None

    #schema = ProjectSchema().bind(project=project, request=request)

    #try:
        #data = schema.deserialize(request.POST)
    #except colander.Invalid as e:
        #return HTTPBadRequest(json=e.asdict())

    #if is_new:
        #project = models.Project(
            ## We don't care about these for mappings
            #short_title=data['name'],
            #consent_date=date.today()
        #)
        #db_session.add(project)

    #project.name = data['name'],
    #project.title = data['title'],

    #next_url = request.current_route_path(
        #_route_name='imports.project_detail',
        #project=project.name
    #)

    #result = HTTPSeeOther(location=next_url)
    #return result


#@view_config(
    #route_name='imports.project_detail',
    #permission='add',
    #request_method='DELETE',
    #renderer='json'
#)
#def delete(context, request):
    #check_csrf_token(request)
    #db_session = request.db_session
    #db_session.remove(context)
    #next_url = request.current_route_path(_route_name='imports.project_list')
    #result = HTTPSeeOther(location=next_url)
    #return result
