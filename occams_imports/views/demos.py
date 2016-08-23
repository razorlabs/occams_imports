from pyramid.view import view_config


@view_config(
    route_name='imports.demos.cytoscapejs',
    permission='view',
    request_method='GET',
    renderer='../templates/demos/cytoscapejs_demo.pt')
def occams_cytoscape_demo(context, request):
    return {}