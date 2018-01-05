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

import functools
import alembic.config
import sqlalchemy
import psycopg2.extensions
import venusian
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy


class ReadOnlyPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return f'read_only = {self.val!r}'

    phash = text

    def __call__(self, info, request):
        return True


class _ModelBase(object):
    pass


metadata = sqlalchemy.MetaData()
ModelBase = declarative_base(cls=_ModelBase, metadata=metadata)


class Model(ModelBase):
    __abstract__ = True

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)


Session = sessionmaker()


def listens_for(target, identifier, *args, **kwargs):
    def decorator(wrapped):
        def callback(scanner, _name, wrapped):
            wrapped = functools.partial(wrapped, scanner.config)
            event.listen(target, identifier, wrapped, *args, **kwargs)
        venusian.attach(wrapped, callback)
        return wrapped
    return decorator


def _configure_alembic(config):
    """
    Returns a default configuration of Alembic for our database and migrations
    """
    alembic_config = alembic.config.Config()
    alembic_config.set_main_option('script_location', 'armonaut:migrations')
    alembic_config.set_main_option(
        'url', config.registry.settings['database.url']
    )
    return alembic_config


def _reset(dbapi_connection, connection_record):
    """
    Resets the database connection if required.
    """
    needs_reset = connection_record.info.pop('armonaut.needs_reset', False)
    if needs_reset:
        dbapi_connection.set_session(
            isolation_level='READ COMMITTED',
            readonly=False,
            deferrable=False
        )


def _create_engine(url: str):
    """
    Creates the SQLAlchemy engine from the ``database.url`` setting
    """
    engine = sqlalchemy.create_engine(
        url,
        isolation_level='READ COMMITTED',
        pool_size=30,
        max_overflow=60,
        pool_timeout=20
    )
    event.listen(engine, 'reset', _reset)
    return engine


def _create_session(request) -> sqlalchemy.orm.Session:
    """
    Creates a session for the request. If the request is read-only then
    the database is set in read-only mode as well for security.
    """
    connection = request.registry['sqlalchemy.engine'].connect()

    # Issue where sometimes the first connection errors so we want
    # to discard that first connection if it's not idle.
    if (connection.connection.get_transaction_status() !=
            psycopg2.extensions.TRANSACTION_STATUS_IDLE):
        connection.connection.rollback()

    # If we receive a read-only request then we can set
    # the isolation level of the session to be read-only.
    if request.read_only:
        connection.info['armonaut.needs_reset'] = True
        connection.connection.set_session(
            isolation_level='SERIALIZABLE',
            readonly=True,
            deferrable=True
        )

    # Create the session bound to our connection
    session = Session(bind=connection)

    # Register our session transaction manager as pyramid_tm manager
    zope.sqlalchemy.register(session, transaction_manager=request.tm)

    @request.add_finished_callback
    def cleanup(request):
        session.close()
        connection.close()

    return session


def _is_readonly(request) -> bool:
    if request.matched_route is not None:
        for predicate in request.matched_route.predicates:
            if isinstance(predicate, ReadOnlyPredicate) and predicate.val:
                return True
    return False


def includeme(config):
    # Add a directive to get an Alembic configuration
    config.add_directive('alembic_config', _configure_alembic)

    # Create the SQLAlchemy engine
    config.registry['sqlalchemy.engine'] = _create_engine(
        config.registry.settings['database.url']
    )

    # Add a request method to create a database session
    config.add_request_method(_create_session, name='db', reify=True)

    # Add support for marking certain routes as read-only.
    config.add_route_predicate('read_only', ReadOnlyPredicate)
    config.add_request_method(_is_readonly, name='read_only', reify=True)
