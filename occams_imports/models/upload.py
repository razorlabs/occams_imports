import sqlalchemy as sa
from sqlalchemy import orm, String
from sqlalchemy.dialects.postgresql import BYTEA

from occams_datastore import models as datastore
from occams_studies import models as studies

from .meta import Base


class Upload(Base, datastore.Referenceable, datastore.Modifiable):
    """Table to store project source data."""

    __tablename__ = 'upload'

    study_id = sa.Column(
        sa.ForeignKey(studies.Study.id, ondelete='CASCADE'),
        nullable=False
    )

    study = orm.relationship(studies.Study)

    project_file = sa.Column(BYTEA, nullable=False)

    filename = sa.Column(String, nullable=False)
