# flake8: NOQA
# This module breaks my OCD-ness in favor of readability
import time
from datetime import datetime

from pyramid.static import QueryStringConstantCacheBuster

from . import log
from . import models

def includeme(config):
    """
    Helper method to configure available routes for the application
    """

    config.add_static_view(path='occams_imports:static',    name='/static', cache_max_age=3600)
    config.add_cache_buster(
        'occams_imports:static/',
        QueryStringConstantCacheBuster(str(int(time.time()))))

    config.add_route('imports.index',                       '/',                          factory=models.ImportFactory)

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
    config.add_route('imports.mapping_detail',              '/api/mappings/{mapping}',    factory=models.ImportFactory)
    config.add_route('imports.mappings.delete',             '/mappings/delete',           factory=models.ImportFactory)
    config.add_route('imports.mapping.status',              '/mapping/status',            factory=models.ImportFactory)
    config.add_route('imports.mapping.notes',               '/mapping/notes',             factory=models.ImportFactory)

    config.add_route('imports.upload',                      '/upload',                    factory=models.ImportFactory)
    config.add_route('imports.upload_status',               '/upload/status',             factory=models.ImportFactory)
    config.add_route('imports.apply_direct',                '/apply/direct',              factory=models.ImportFactory)
    config.add_route('imports.apply_direct_status',         '/apply/direct/status',       factory=models.ImportFactory)
    config.add_route('imports.apply_imputation_status',     '/apply/imputation/status',   factory=models.ImportFactory)
    config.add_route('imports.apply_imputation',            '/apply/imputation',          factory=models.ImportFactory)

    config.add_route('imports.sitedata',                    '/sitedata',                  factory=models.ImportFactory)

    config.add_route('imports.direct_notifications',        '/direct_notifications',      factory=models.ImportFactory)
    config.add_route('imports.imputations_notifications',   '/import_notifications',      factory=models.ImportFactory)


    config.add_route('imports.project_app',     '/projects',                                                    factory=models.ProjectFactory)

    config.add_route('imports.project_list',    '/api/projects',                                                factory=models.ProjectFactory, traverse='/')
    config.add_route('imports.project_detail',  '/api/projects/{project}',                                      factory=models.ProjectFactory, traverse='/{project}')
    config.add_route('imports.table_list',      '/api/projects/{project}/tables',                               factory=models.ProjectFactory, traverse='/{project}/tables')
    config.add_route('imports.table_detail',    '/api/projects/{project}/tables/{table}',                       factory=models.ProjectFactory, traverse='/{project}/tables/{table}')
    config.add_route('imports.variable_list',   '/api/projects/{project}/tables/{table}/variables',             factory=models.ProjectFactory, traverse='/{project}/tables/{table}/variables')
    config.add_route('imports.variable_detail', '/api/projects/{project}/tables/{table}/variables/{variable}',  factory=models.ProjectFactory, traverse='/{project}/tables/{table}/variables/{variable}')

    config.add_route('imports.uploads_list',    '/api/projects/{project}/uploads',                              factory=models.ProjectFactory)
    config.add_route('imports.uploads_detail',  '/api/projects/{project}/uploads/{upload}',                     factory=models.ProjectFactory)

    config.add_route('imports.apply',           '/api/projects/{project}/apply',                                factory=models.ProjectFactory)
