# flake8: NOQA
# This module breaks my OCD-ness in favor of readability
from datetime import datetime
from . import log

from . import models


def includeme(config):
    """
    Helper method to configure available routes for the application
    """

    config.add_static_view(path='occams_imports:static',    name='/static', cache_max_age=3600)

    config.add_route('imports.index',                       '/',                          factory=models.RootFactory)
    config.add_route('imports.codebooks_iform',             '/codebooks/iform',           factory=models.ImportFactory)
    config.add_route('imports.codebooks_occams',            '/codebooks/occams',          factory=models.ImportFactory)
    config.add_route('imports.codebooks_qds',               '/codebooks/qds',             factory=models.ImportFactory)
    config.add_route('imports.codebooks_status',            '/codebooks/{format}/status', factory=models.ImportFactory)
    config.add_route('imports.mappings.direct',             '/mappings/direct',           factory=models.ImportFactory)
    config.add_route('imports.mappings.direct.map',         '/mappings/direct/map',       factory=models.ImportFactory)
    config.add_route('imports.mappings.imputation',         '/mappings/imputation',       factory=models.ImportFactory)
    config.add_route('imports.schemas',                     '/schemas',                   factory=models.ImportFactory)
    config.add_route('imports.mappings.view',               '/mappings/view',             factory=models.ImportFactory)
    config.add_route('imports.mappings.view_mapped',        '/mappings/view_mapped',      factory=models.ImportFactory)
    config.add_route('imports.mappings.delete',             '/mappings/delete',           factory=models.ImportFactory)
    config.add_route('imports.mapping.status',              '/mapping/status',            factory=models.ImportFactory)
    config.add_route('imports.demos.cytoscapejs',           '/demos/cytoscapejs',         factory=models.ImportFactory)

    log.debug('Routes configured')
