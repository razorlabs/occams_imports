"""
Home page views for mapping tool
"""

from pyramid.view import view_config


@view_config(
    route_name='imports.index',
    permission='view',
    renderer='../templates/home/index.pt'
)
def index(context, request):
    return {}
