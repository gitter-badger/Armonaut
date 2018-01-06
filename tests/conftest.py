# Copyright 2018 Seth Michael Larson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from alembic import command
from armonaut.config import configure
from armonaut.db import Session as _Session
from sqlalchemy import event
from sqlalchemy.orm import scoped_session
import webtest as _webtest
from pytest_postgresql.factories import (
    init_postgresql_database, drop_postgresql_database
)


Session = scoped_session(_Session)


@pytest.fixture(scope='session')
def database(request):
    host = 'database'
    port = '5432'
    user = 'postgres'
    db = 'armonaut'
    version = '9.6'

    # If the database already exists we'll drop it here to make sure
    # we're starting with an empty slate.
    try:
        drop_postgresql_database(user, host, port, db, version)
    except Exception:
        pass

    init_postgresql_database(user, host, port, db)

    @request.addfinalizer
    def drop_database():
        drop_postgresql_database(user, host, port, db, version)

    return f'postgresql://{user}@{host}:{port}/{db}'


@pytest.fixture
def app_config(database):
    config = configure({
        'armonaut.env': 'development',
        'database.url': database
    })

    # Make sure that our migrations have been run.
    command.upgrade(config.alembic_config(), 'head')

    return config


@pytest.yield_fixture
def db_session(app_config):
    engine = app_config['sqlalchemy.engine']
    conn = engine.connect()
    trans = conn.begin()
    session = Session(bind=conn)

    # Start the session in a SAVEPOINT.
    session.begin_nested()

    # Need to reopen the session each time that the SAVEPOINT ends.
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        Session.remove()
        trans.rollback()
        conn.close()
        engine.dispose()


@pytest.yield_fixture
def webtest(app_config) -> _webtest.TestApp:
    try:
        yield _webtest.TestApp(app_config.make_wsgi_app())
    finally:
        app_config.registry['sqlalchemy.engine'].dispose()
