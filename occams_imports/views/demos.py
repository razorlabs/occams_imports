from pyramid.view import view_config


@view_config(
    route_name='imports.mappings.jointjs.demo',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/jointjs_demo.pt')
def occams_jointjs_demo(context, request):
    return {}


@view_config(
    route_name='imports.mappings.cytoscapejs.demo',
    permission='view',
    request_method='GET',
    renderer='../templates/mappings/cytoscapejs_demo.pt')
def occams_cytoscape_demo(context, request):
    return {}