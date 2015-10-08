# flake8: NOQA
# This module breaks my OCD-ness in favor of readability
from datetime import datetime
from . import log

from . import models


def includeme(config):
    """
    Helper method to configure available routes for the application
    """

    config.add_static_view('/imports/static',               'occams_imports:static',              cache_max_age=3600)

    config.add_route('imports.main',                        '/imports',                           factory=models.RootFactory)

    config.add_route('imports.codebooks_iform',             '/imports/codebooks/iform',           factory=models.ImportFactory)

    config.add_route('imports.codebooks_occams',            '/imports/codebooks/occams',          factory=models.ImportFactory)

    config.add_route('imports.codebooks_qds',               '/imports/codebooks/qds',             factory=models.ImportFactory)

    config.add_route('imports.codebooks_iform_status',      '/imports/codebooks/iform/status',    factory=models.ImportFactory)

    config.add_route('imports.codebooks_occams_status',     '/imports/codebooks/occams/status',   factory=models.ImportFactory)

    config.add_route('imports.codebooks_qds_status',        '/imports/codebooks/qds/status',      factory=models.ImportFactory)

    config.add_route('imports.mappings.direct',             '/imports/mappings/direct',           factory=models.RootFactory)

    config.add_route('imports.mappings.direct.map',         '/imports/mappings/direct/map',       factory=models.RootFactory)

    config.add_route('imports.mappings.imputation',         '/imports/mappings/imputation',       factory=models.RootFactory)

    config.add_route('imports.schemas',                     '/imports/schemas',                   factory=models.RootFactory)

    config.add_route('imports.mappings.view',               '/imports/mappings/view',             factory=models.RootFactory)

    config.add_route('imports.mappings.view_mapped',        '/imports/mappings/view_mapped',      factory=models.RootFactory)

    config.add_route('imports.mappings.delete',             '/imports/mappings/delete',           factory=models.RootFactory)

    config.add_route('imports.mappings.imputation.demo',    '/imports/mappings/imputation/demo',  factory=models.RootFactory)

    log.debug('Routes configured')
