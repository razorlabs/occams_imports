"""
Testing fixtures

To run the tests you'll then need to run the following command:

    py.test --db=postgres://user:pass@host/db

Also, you can reuse a database:

    py.test --db=postgres://user:pass@host/db --reuse

This is particularly handing while developing as it saves about a minute
each time the tests are run.

"""

from __future__ import unicode_literals
import pytest
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.compiler import compiles


REDIS_URL = 'redis://localhost/9'

USERID = 'test_user'


def pytest_addoption(parser):
    """
    Registers a command line argument for a database URL connection string

    :param parser: The pytest command-line parser
    """
    parser.addoption('--db', action='store', help='db string for testing')
    parser.addoption('--reuse', action='store_true',
                     help='Reuses existing database')


@compiles(CreateTable, 'postgresql')
def compile_unlogged(create, compiler, **kwargs):
    """
    Updates the CREATE TABLE construct for PostgreSQL to UNLOGGED

    The benefit of this is faster writes for testing, at the cost of
    slightly slower table creation.

    See: http://www.postgresql.org/docs/9.1/static/sql-createtable.html

    :param create:      the sqlalchemy CREATE construct
    :param compiler:    the current dialect compiler

    :return: the compiled SQL string

    """
    if 'UNLOGGED' not in create.element._prefixes:
        create.element._prefixes.append('UNLOGGED')
        return compiler.visit_create_table(create)


@pytest.fixture(scope='session', autouse=True)
def create_tables(request):
    """
    Creates the database tables for the entire testing session

    :param request: The pytest context

    :returns: configured database session
    """
    import os
    from sqlalchemy import create_engine
    from occams_datastore import models as datastore
    from occams_studies import models as studies
    from occams_imports.models.meta import Base

    db_url = request.config.getoption('--db')
    reuse = request.config.getoption('--reuse')

    engine = create_engine(db_url)
    url = engine.url

    if not reuse:
        # This is very similar to the init_db script: create tables
        # and pre-populate with expected data
        with engine.begin() as connection:
            connection.info['blame'] = 'test_installer'
            datastore.DataStoreModel.metadata.create_all(connection)
            studies.StudiesModel.metadata.create_all(connection)
            Base.metadata.create_all(connection)
            # Clear out the state table since the data is populated on each test
            connection.execute('DELETE FROM state')
            connection.execute('DELETE FROM imports.status')

    def drop_tables():
        if url.drivername == 'sqlite':
            if url.database not in ('', ':memory:'):
                os.unlink(url.database)
        elif not reuse:
            Base.metadata.drop_all(engine)
            studies.StudiesModel.metadata.drop_all(engine)
            datastore.DataStoreModel.metadata.drop_all(engine)

    request.addfinalizer(drop_tables)


@pytest.yield_fixture
def config(request):
    """
    (Integration Testing) Instantiates a Pyramid testing configuration

    :param request: The pytest context
    """

    from pyramid import testing
    import transaction

    db_url = request.config.getoption('--db')

    test_config = testing.setUp(settings={
        'occams.db.url': db_url
    })

    # Load mimimum set of plugins
    test_config.include('occams.models')
    #test_config.include('occams_forms.routes')

    yield test_config

    testing.tearDown()
    transaction.abort()


@pytest.fixture
def db_session(config):
    """
    (Integration Testing) Instantiates a database session.

    :param config: The pyramid testing configuartion

    :returns: An instantiated sqalchemy database session
    """
    from occams_datastore import models
    from occams_imports import models as import_models
    import occams_datastore.models.events
    import zope.sqlalchemy

    db_session = config.registry['dbsession_factory']()

    occams_datastore.models.events.register(db_session)
    zope.sqlalchemy.register(db_session)

    # Pre-configure with a blame user
    blame = models.User(key=USERID)
    db_session.add(blame)
    db_session.flush()
    db_session.info['blame'] = blame

    # Other expected settings
    db_session.info['settings'] = config.registry.settings

    # Hardcoded workflow
    db_session.add_all([
        models.State(name=u'pending-entry', title=u'Pending Entry'),
        models.State(name=u'pending-review', title=u'Pending Review'),
        models.State(name=u'pending-correction',
                     title=u'Pending Correction'),
        models.State(name=u'complete', title=u'Complete'),
        import_models.Status(
            name=u'review',
            title=u'Review',
            description=u'Denotes mapping in need of review.'
        ),
        import_models.Status(
            name=u'in-progress',
            title=u'In Progress',
            description=u'Denotes mapping in is not ready to review.'
        ),
        import_models.Status(
            name=u'approved',
            title=u'Approved',
            description=u'Denotes mapping has been approved by reviewer.'
        ),
        import_models.Status(
            name=u'rejected',
            title=u'Rejected',
            description=u'Denotes mapping has been rejected by reviewer.'
        )
    ])

    return db_session


@pytest.fixture
def req(db_session):
    """
    (Integration Testing) Creates a dummy request

    The request is setup with configuration CSRF values and the expected
    ``db_session`` property, the goal being to be be as close to a real
    database session as possible.

    Note that we must called it "req" as "request" is reserved by pytest.

    :param db_session: The testing database session

    :returns: a configured request object
    """
    import uuid
    import mock
    from pyramid.testing import DummyRequest

    dummy_request = DummyRequest()

    # Configurable csrf token
    csrf_token = str(uuid.uuid4())
    get_csrf_token = mock.Mock(return_value=csrf_token)
    dummy_request.session.get_csrf_token = get_csrf_token
    dummy_request.headers['X-CSRF-Token'] = csrf_token

    # Attach database session for expected behavior
    dummy_request.db_session = db_session
    db_session.info['request'] = dummy_request

    return dummy_request


@pytest.fixture(scope='session')
def wsgi(request):
    """
    (Functional Testing) Sets up a full-stacked singleton WSGI app

    :param request: The pytest context

    :returns: a WSGI application
    """
    import tempfile
    import shutil
    import six
    from occams import main

    # The pyramid_who plugin requires a who file, so let's create a
    # barebones files for it...
    who_ini = tempfile.NamedTemporaryFile()
    who = six.moves.configparser.ConfigParser()
    who.add_section('general')
    who.set('general', 'request_classifier',
            'repoze.who.classifiers:default_request_classifier')
    who.set('general', 'challenge_decider',
            'repoze.who.classifiers:default_challenge_decider')
    who.set('general', 'remote_user_key', 'REMOTE_USER')
    who.write(who_ini)
    who_ini.flush()

    db_url = request.config.getoption('--db')

    tmp_dir = tempfile.mkdtemp()

    wsgi = main({}, **{
        'redis.url': REDIS_URL,
        'redis.sessions.secret': 'sekrit',

        'who.config_file': who_ini.name,
        'who.identifier_id': '',

        # Enable regular error messages so we can see useful traceback
        'debugtoolbar.enabled': True,
        'pyramid.debug_all': True,

        'webassets.debug': True,

        'occams.apps': 'occams_imports',

        'occams.db.url': db_url,
        'occams.groups': [],

        'celery.broker.url': REDIS_URL,
        'celery.backend.url': REDIS_URL,
        'celery.blame': 'celery@localhost',
    })

    who_ini.close()

    def cleanup():
        shutil.rmtree(tmp_dir)

    request.addfinalizer(cleanup)

    return wsgi


@pytest.yield_fixture
def app(request, wsgi, db_session):
    """
    (Functional Testing) Initiates a user request against a WSGI stack

    :param request: The pytest context
    :param wsgi: An initialized WSGI stack
    :param db_session: A database session for seting up pre-existing data

    :returns: a test app request against the WSGI instance
    """
    import transaction
    from webtest import TestApp
    from zope.sqlalchemy import mark_changed
    from occams_datastore import models
    from occams_imports import models as import_models

    # Save all changes up tho this point (db_session does some configuration)
    with transaction.manager:
        blame = models.User(key='workflow@localhost')
        db_session.add(blame)
        db_session.flush()
        db_session.info['blame'] = blame

        db_session.add_all([
            models.State(name=u'pending-entry', title=u'Pending Entry'),
            models.State(name=u'pending-review', title=u'Pending Review'),
            models.State(name=u'pending-correction',
                         title=u'Pending Correction'),
            models.State(name=u'complete', title=u'Complete'),
            import_models.Status(
                name=u'review',
                title=u'Review',
                description=u'Denotes mapping in need of review.'
            ),
            import_models.Status(
                name=u'in-progress',
                title=u'In Progress',
                description=u'Denotes mapping in is not ready to review.'
            ),
            import_models.Status(
                name=u'approved',
                title=u'Approved',
                description=u'Denotes mapping has been approved by reviewer.'
            ),
            import_models.Status(
                name=u'rejected',
                title=u'Rejected',
                description=u'Denotes mapping has been rejected by reviewer.'
            )
        ])

    app = TestApp(wsgi)

    yield app

    with transaction.manager:
        # DELETE is dramatically faster than TRUNCATE
        # http://stackoverflow.com/a/11423886/148781
        # We also have to do this as a raw query becuase SA does
        # not have a way to invoke server-side cascade
        db_session.execute('DELETE FROM "imports"."import" CASCADE')
        db_session.execute('DELETE FROM "imports"."status" CASCADE')
        db_session.execute('DELETE FROM "schema" CASCADE')
        db_session.execute('DELETE FROM "state" CASCADE')
        db_session.execute('DELETE FROM "study" CASCADE')
        db_session.execute('DELETE FROM "user" CASCADE')
        mark_changed(db_session)


@pytest.fixture
@pytest.mark.usefixtures('create_tables')
def celery(request):
    """
    (Function Testing) Sets up a celery application for testing

    :param request: The pytest context
    """
    import shutil
    import tempfile
    import mock
    from redis import StrictRedis
    from sqlalchemy import create_engine
    from occams.celery import Session
    from occams_datastore import models as datastore
    from occams_studies import tasks

    settings = {
        'studies.export.dir': tempfile.mkdtemp(),
        'celery.blame': USERID
    }

    tasks.app.userid = settings['celery.blame']
    tasks.app.redis = StrictRedis.from_url(REDIS_URL)
    tasks.app.settings = settings

    db_url = request.config.getoption('--db')
    engine = create_engine(db_url)
    Session.configure(bind=engine, info={'settings': settings})
    Session.add(datastore.User(key=settings['celery.blame']))

    Session.flush()

    commitmock = mock.patch('occams_imports.tasks.Session.commit')
    commitmock.start()

    def cleanup():
        commitmock.stop()
        shutil.rmtree(settings['studies.export.dir'])
        Session.remove()

    request.addfinalizer(cleanup)


@pytest.fixture
def datadir(tmpdir, request):
    """
    Returns a path to the data file for the tests data directory

    This Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely without interfering with other tests.

    :param tmpdir: pytest's tmpdir fixture
    :param request: pytest fixture request object

    .. notes:: This module depends on pytest's provided tmpdir module
    .. seealso:: http://doc.pytest.org/en/latest/tmpdir.html
    .. seealso:: http://stackoverflow.com/a/29631801/148781

    """
    import os
    from distutils import dir_util

    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, bytes(tmpdir))

    return tmpdir
