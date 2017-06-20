"""Model definitions for site data uploades."""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB

from occams_datastore import models as datastore
from occams_studies import models as studies

from .meta import Base


class SiteData(Base, datastore.Referenceable, datastore.Modifiable):
    """Table to store patient site data.

    :param Base: SQLAlchemy Base class
    :param datastore.Referenceable: SQLAlchemy mixin...adds primary key id
                                    columns to tables.
    :param datastore.Modifiable: SQLAlchemy mixin...adds user edit
                                 modification meta data for lifecycle tracking.

    """

    __tablename__ = 'sitedata'

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

    data = sa.Column(JSONB)
