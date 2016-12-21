import sqlalchemy as sa

from occams_datastore import models as datastore


class Base(datastore.Base):
    __abstract__ = True
    metadata = sa.MetaData(schema='imports')


sa.event.listen(
    Base.metadata,
    'before_create',
    sa.DDL('CREATE SCHEMA IF NOT EXISTS imports')
)
