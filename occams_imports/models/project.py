from pyramid.security import Allow, Authenticated
import sqlalchemy as sa
from sqlalchemy import orm

from occams_studies.models import Study as Project

from .groups import groups
from .table import TableFactory


class ProjectFactory(object):

    __parent__ = None

    RESOURCE = 'projects'

    @property
    def __name__(self):
        return self.RESOURCE

    __acl__ = [
        (Allow, groups.administrator(), ('view', 'add')),
        (Allow, groups.manager(), ('view', 'add')),
        (Allow, groups.reviewer(), ('view')),
        (Allow, groups.member(), ('view',)),
        (Allow, Authenticated, 'view')
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, name):
        db_session = self.request.db_session
        try:
            project = (
                db_session.query(Project)
                .filter(sa.func.lower(Project.name) == name.lower())
                .one()
            )
        except orm.exc.NoResultFound:
            raise KeyError
        else:
            project.__parent__ = self
            return project


def _project__getitem__(self, name):
    if name == TableFactory.RESOURCE:
        return TableFactory(self)
    else:
        raise KeyError


def _project__acl__(self):
    acl = [
        (Allow, groups.administrator(), ('view', 'edit', 'delete')),
        (Allow, groups.manager(), ('view', 'edit', 'delete')),
    ]
    return acl


Project.__getitem__ = _project__getitem__
Project.__acl__ = property(_project__acl__)
