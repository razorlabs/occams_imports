import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB

from occams_datastore import models as datastore
from occams_studies import models as studies

from .meta import Base


class SiteData(Base, datastore.Referenceable, datastore.Modifiable):
    """Table to store patient site data."""

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
