from sqlalchemy import event

from .meta import Base

from occams_datastore import models as datastore


class Status(Base,
             datastore.Describeable,
             datastore.Referenceable,
             datastore.Modifiable):
    """Stats to track approval state of mappings."""

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
