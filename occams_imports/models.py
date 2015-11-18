from pyramid.security import Allow, Authenticated
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSON


from occams_datastore import models as datastore
from occams_studies import models as studies


class ImportsModel(datastore.Base):
    __abstract__ = True
    metadata = sa.MetaData(schema='imports')


sa.event.listen(
    ImportsModel.metadata,
    'before_create',
    sa.DDL('CREATE SCHEMA IF NOT EXISTS imports')
)


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


class Import(ImportsModel, datastore.Referenceable, datastore.Modifiable):
    __tablename__ = 'import'

    site_id = sa.Column(
        sa.ForeignKey(studies.Site.id, ondelete='CASCADE'),
        nullable=False)

    site = orm.relationship(studies.Site)

    schema_id = sa.Column(
        sa.ForeignKey(datastore.Schema.id, ondelete='CASCADE'),
        nullable=False)

    schema = orm.relationship(datastore.Schema)

    __table_args__ = (
        sa.UniqueConstraint(site_id, schema_id),
    )


class Mapping(ImportsModel, datastore.Referenceable, datastore.Modifiable):
    __tablename__ = 'mapping'

    site_id = sa.Column(
        sa.ForeignKey(studies.Site.id, ondelete='CASCADE'),
        nullable=False)

    site = orm.relationship(studies.Site)

    mapped_attribute_id = sa.Column(
        sa.ForeignKey(datastore.Attribute.id, ondelete='CASCADE'),
        nullable=False)

    mapped_attribute = orm.relationship(datastore.Attribute)

    mapped_choice_id = sa.Column(
        sa.ForeignKey(datastore.Choice.id, ondelete='CASCADE'))

    mapped_choice = orm.relationship(datastore.Choice)

    description = sa.Column(sa.UnicodeText())

    confidence = sa.Column(sa.Integer(), nullable=False)

    type = sa.Column(
        sa.Enum(u'direct', u'imputation', name='mapping_type'),
        nullable=False)

    logic = sa.Column(JSON)

    __table_args__ = (
        sa.UniqueConstraint(site_id, mapped_attribute_id, mapped_choice_id),
    )
