from sqlalchemy import orm

from occams_datastore.models import Schema as Table
from .variable import VariableFactory


class TableFactory(object):

    __parent__ = None

    RESOURCE = 'tables'

    @property
    def __name__(self):
        return self.RESOURCE

    def __init__(self, parent):
        db_session = orm.object_session(parent)
        request = db_session.info['request']
        self.request = request
        self.__parent__ = parent

    def __getitem__(self, name):
        db_session = self.request.db_session
        try:
            table = (
                db_session.query(Table)
                .join(Table.studies)
                .filter_by(study=self.__parent__)
                .filter(Table.name.lower() == name.lower())
                .one()
            )
        except orm.exc.NoResultFound:
            raise KeyError
        else:
            table.__parent__ = self
            table.request = self.request
            return table


def _table__getitem__(self, name):
    if name == VariableFactory.__name__:
        return VariableFactory(self)
    else:
        raise KeyError


def _table__acl__(self):
    acl = []
    return acl


Table.__getitem__ = _table__acl__
Table.__acl__ = _table__acl__
