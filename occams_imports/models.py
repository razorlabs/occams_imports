from pyramid.security import Allow, Authenticated
import sqlalchemy as sa
from sqlalchemy import orm

from occams_datastore.models import (
    ModelClass,
    Schema,
    Referenceable, Modifiable)

Base = ModelClass(u'Base')


class groups:

    @staticmethod
    def principal(location=None, group=None):
        """
        Generates the principal name used internally by this application
        Supported keyword parameters are:
            site --  The site code
            group -- The group name
        """
        return location.name + ':' + group if location else group

    @staticmethod
    def administrator():
        return groups.principal(group='administrator')

    @staticmethod
    def manager(location=None):
        return groups.principal(location=location, group='manager')

    @staticmethod
    def worker(location=None):
        return groups.principal(location=location, group='worker')

    @staticmethod
    def member(location=None):
        return groups.principal(location=location, group='member')


class Resource(object):

    def __init__(self, request):
        self.request = request


class RootFactory(Resource):

    __acl__ = [
        (Allow, Authenticated, 'view')
    ]


class ImportFactory(Resource):
    __acl__ = [
        (Allow, 'administrator', 'import'),
        (Allow, 'manager', 'import')
    ]


class Import(Base, Referenceable, Modifiable):
    __tablename__ = 'import'

    site = sa.Column(
        sa.String(10),
        nullable=False,
        doc='A string distinguishing a site(ucsd, ucla, etc.)')

    schema_id = sa.Column(sa.Integer())

    schema = orm.relationship(
        Schema,
        primaryjoin=(schema_id == Schema.id),
        foreign_keys=[schema_id],
        backref=orm.backref(
            name='import',
            cascade='all, delete-orphan'))
