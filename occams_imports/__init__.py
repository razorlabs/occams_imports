from __future__ import unicode_literals
import logging
import pkg_resources

from pyramid.i18n import TranslationStringFactory
import wtforms_json; wtforms_json.init()  # flake8: noqa


log = logging.getLogger('occams').getChild(__name__)

_ = TranslationStringFactory(__name__)

__version__ = pkg_resources.require(__name__)[0].version


def includeme(config):

    config.registry.settings['occams.apps']['occams_imports'] = {
        'name': 'imports',
        'title': _(u'Imports'),
        'package': 'occams_imports',
        'route': 'imports.index',
        'version': __version__
    }

    config.include('.assets')
    config.include('.routes')
    config.scan()
