# flake8: NOQA
# This module breaks my OCD-ness in favor of readability
from datetime import datetime
from . import log

from . import models


def includeme(config):
    """
    Helper method to configure available routes for the application
    """

    config.add_static_view('/imports/static',               'occams_imports:static', cache_max_age=3600)

    config.add_route('imports.main',                        '/imports',                              factory=models.RootFactory)

    config.add_route('imports.upload',                      '/imports/upload',                       factory=models.RootFactory)

    log.debug('Routes configured')
