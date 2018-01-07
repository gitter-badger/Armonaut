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

import click
import contextlib
import alembic.command
from armonaut.cli import armonaut


@contextlib.contextmanager
def alembic_lock(engine, alembic_config):
    with engine.begin() as connection:
        # Locks the database so that only one Alembic
        # command can be executed at a time.
        connection.execute("SELECT pg_advisory_lock(hashtext('alembic'))")
        try:
            alembic_config.attributes["connection"] = connection
            yield alembic_config
        finally:
            connection.execute(
                "SELECT pg_advisory_unlock(hashtext('alembic'))")


@armonaut.group()  # pragma: no branch
def db():
    pass


def _alembic_command(command, config, *args, **kwargs):
    with alembic_lock(config.registry['sqlalchemy.engine'],
                      config.alembic_config()) as alembic_config:
        args = (alembic_config,) + args
        cmd = getattr(alembic.command, command)
        cmd(*args, **kwargs)


@db.command()
@click.argument('revision', required=True, default='head')
@click.pass_obj
def upgrade(config, revision, **kwargs):
    kwargs['revision'] = revision
    _alembic_command('upgrade', config, **kwargs)


@db.command()
@click.option(
    "--message", "-m",
    metavar="MESSAGE",
    help="Message string to use with the revision",
)
@click.option(
    "--autogenerate", "-a",
    is_flag=True,
    help=(
        "Populate revision script with candidate migration operations, based "
        "on comparison of database to tables."
    ),
)
@click.option(
    "--head",
    metavar="HEAD",
    help=(
        "Specify a head revision or <brachname>@head to base new revision on."
    ),
)
@click.option(
    "--splice",
    is_flag=True,
    help="Allow a non-head revision as the 'head' to splice onto.",
)
@click.option(
    "--branch-label",
    metavar="BRANCH",
    help="Specify a branch label to apply to the new revision.",
)
@click.pass_obj
def revision(config, **kwargs):
    _alembic_command('revision', config, **kwargs)
