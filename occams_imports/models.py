from pyramid.security import Allow, Authenticated
import sqlalchemy as sa
from sqlalchemy import orm, event
from sqlalchemy.dialects.postgresql import JSONB


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
    def manager():
        return groups.principal(group='manager')

    @staticmethod
    def reviewer(location=None):
        return groups.principal(group='reviewer')

    @staticmethod
    def member(location=None):
        return groups.principal(group='member')


class Resource(object):

    def __init__(self, request):
        self.request = request


class ImportFactory(Resource):
    __acl__ = [
        (
            Allow,
            groups.administrator(),
            ('view', 'add', 'edit', 'delete', 'approve', 'import')
        ),
        (Allow, groups.manager(), ('view', 'add', 'edit', 'delete', 'approve')),
        (Allow, groups.reviewer(), ('view', 'approve')),
        (Allow, groups.member(), ('view',)),
        (Allow, Authenticated, 'view')
    ]


class Import(ImportsModel, datastore.Referenceable, datastore.Modifiable):
    __tablename__ = 'import'

    study_id = sa.Column(
        sa.ForeignKey(studies.Study.id, ondelete='CASCADE'),
        nullable=False)

    study = orm.relationship(studies.Study)

    schema_id = sa.Column(
        sa.ForeignKey(datastore.Schema.id, ondelete='CASCADE'),
        nullable=False)

    schema = orm.relationship(datastore.Schema)

    __table_args__ = (
        sa.UniqueConstraint(study_id, schema_id),
    )

class Status(ImportsModel,
             datastore.Describeable,
             datastore.Referenceable,
             datastore.Modifiable):

    __tablename__ = 'status'


@event.listens_for(Status.__table__, 'after_create')
def populate_default_statuses(target, connection, **kw):
    """These are hard-coded statuses, not editable by the user via the UI."""

    blame = connection.info['blame']
    user_table = datastore.User.__table__

    result = connection.execute(
        user_table
        .select()
        .where(user_table.c.key == blame))

    user = result.fetchone()
    blame_id = user['id']

    def status_type(**kw):
        values = kw.copy()
        values.update({
            'create_user_id': blame_id,
            'modify_user_id': blame_id,
        })
        return values

    connection.execute(target.insert().values([
        status_type(
            name=u'review',
            title=u'Review',
            description=u'Denotes mapping in need of review.'
        ),
        status_type(
            name=u'in-progress',
            title=u'In Progress',
            description=u'Denotes mapping in is not ready to review.'
        ),
        status_type(
            name=u'approved',
            title=u'Approved',
            description=u'Denotes mapping has been approved by reviewer.'
        ),
        status_type(
            name=u'rejected',
            title=u'Rejected',
            description=u'Denotes mapping has been rejected by reviewer.'
        ),
    ]))

class Mapping(ImportsModel, datastore.Referenceable, datastore.Modifiable):
    __tablename__ = 'mapping'

    study_id = sa.Column(
        sa.ForeignKey(studies.Study.id, ondelete='CASCADE'),
        nullable=False)

    study = orm.relationship(studies.Study)

    status_id = sa.Column(
        sa.ForeignKey(Status.id, ondelete='CASCADE'),
        nullable=False)

    status = orm.relationship(Status)

    description = sa.Column(sa.UnicodeText())

    notes = sa.Column(sa.UnicodeText())

    type = sa.Column(
        sa.Enum(u'direct', u'imputation', name='mapping_type'),
        nullable=False)

    logic = sa.Column(JSONB)

