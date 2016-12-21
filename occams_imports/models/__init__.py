from sqlalchemy.orm import configure_mappers

from .import_ import ImportFactory, Import  # noqa
from .mapping import Mapping  # noqa
from .sitedata import SiteData  # noqa
from .status import Status  # noqa

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()
