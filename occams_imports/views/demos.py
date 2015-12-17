from pyramid.view import view_config


@view_config(
    route_name='imports.demos.jointjs',
    permission='view',
    request_method='GET',
    renderer='../templates/demos/jointjs_demo.pt')
def occams_jointjs_demo(context, request):
    return {}


@view_config(
    route_name='imports.demos.cytoscapejs',
    permission='view',
    request_method='GET',
    renderer='../templates/demos/cytoscapejs_demo.pt')
def occams_cytoscape_demo(context, request):
    return {}