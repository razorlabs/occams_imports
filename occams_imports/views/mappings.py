"""
Perform direct and imputation mappings of DRSC variables
"""

from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid.session import check_csrf_token

from occams.utils.forms import wtferrors
from .. import Session


@view_config(
    route_name='imports.mappings',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/mappings.pt')
def occams(context, request):
    return {}
