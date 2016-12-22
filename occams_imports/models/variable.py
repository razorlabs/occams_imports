from sqlalchemy import orm

from occams_datastore.models import Attribute as Variable, Choice  # noqa


class VariableFactory(object):

    __parent__ = None

    RESOURCE = 'variables'

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
            variable = (
                db_session.query(Variable)
                .filter_by(schema=self.__parent__)
                .filter(Variable.name == name.lower())
                .one()
            )
        except orm.exc.NoResultFound:
            raise KeyError
        else:
            variable.__parent__ = self
            variable.request = self.request
            return variable
