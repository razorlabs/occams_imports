"""Model definitions for data mapping."""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB

from occams_datastore import models as datastore
from occams_studies import models as studies

from .meta import Base
from .status import Status


class Mapping(Base, datastore.Referenceable, datastore.Modifiable):
    """Table to store direct and imputation mappings.

    :param Base: SQLAlchemy Base class
    :param datastore.Referenceable: SQLAlchemy mixin...adds primary key id
                                    columns to tables.
    :param datastore.Modifiable: SQLAlchemy mixin...adds user edit
                                 modification meta data for lifecycle tracking.
    """

    __tablename__ = 'mapping'

    study_id = sa.Column(
        sa.ForeignKey(studies.Study.id, ondelete='CASCADE'),
        nullable=False
    )

    study = orm.relationship(studies.Study)

    status_id = sa.Column(
        sa.ForeignKey(Status.id, ondelete='CASCADE'),
        nullable=False
    )

    status = orm.relationship(Status)

    description = sa.Column(sa.UnicodeText())

    notes = sa.Column(sa.UnicodeText())

    type = sa.Column(
        sa.Enum(u'direct', u'imputation', name='mapping_type'),
        nullable=False
    )

    logic = sa.Column(JSONB)
