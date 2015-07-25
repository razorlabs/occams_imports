from pyramid.view import view_config


@view_config(
    route_name='imports.main',
    permission='view',
    renderer='../templates/main/main.pt')
def main(context, request):
    """
    """
    return {}
