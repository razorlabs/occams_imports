"""Model definitions to store file imports."""


from pyramid.security import Allow, Authenticated
import sqlalchemy as sa
from sqlalchemy import orm

from occams_datastore import models as datastore
from occams_studies import models as studies

from .meta import Base
from .groups import groups


class ImportFactory(dict):
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

    def __init__(self, request):
        self.request = request


class Import(Base, datastore.Referenceable, datastore.Modifiable):
    """Record imports and track by study and schema.

    :param Base: SQLAlchemy Base class
    :param datastore.Referenceable: SQLAlchemy mixin...adds primary key id
                                    columns to tables.
    :param datastore.Modifiable: SQLAlchemy mixin...adds user edit
                                 modification meta data for lifecycle tracking.
    """

    __tablename__ = 'import'

    study_id = sa.Column(
        sa.ForeignKey(studies.Study.id, ondelete='CASCADE'),
        nullable=False
    )

    study = orm.relationship(studies.Study)

    schema_id = sa.Column(
        sa.ForeignKey(datastore.Schema.id, ondelete='CASCADE'),
        nullable=False
    )

    schema = orm.relationship(datastore.Schema)

    __table_args__ = (
        sa.UniqueConstraint(study_id, schema_id),
    )
