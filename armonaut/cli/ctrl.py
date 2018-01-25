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
import os
from armonaut.cli import armonaut


@armonaut.group()  # pragma: no cover
def ctrl():
    pass


@ctrl.command()
def initdb():
    os.system('docker-compose run --rm web psql -h database -d postgres -U postgres -c '
              '"DROP DATABASE IF EXISTS armonaut"')
    os.system('docker-compose run --rm web psql -h database -d postgres -U postgres -c '
              '"CREATE DATABASE armonaut ENCODING \'UTF-8\'"')
    os.system('docker-compose run --rm web python -m armonaut db upgrade head')


@ctrl.command()
def build():
    os.system('docker-compose build web')
    os.system('docker-compose build worker')


@ctrl.command()
@click.option(
    '--detach', '-d',
    metavar='detach',
    help=('If provided will run the containers detached from the current shell. '
          'Use `python -m armonaut ctrl down` to stop detached containers.')
)
def up(detach):
    os.system(f'docker-compose up{" -d" if detach else ""}')


@ctrl.command()
def down():
    os.system('docker ps -aq --filter name=armonaut | xargs docker stop')


@ctrl.command()
@click.argument(
    'test_path',
    required=True,
    default='tests/'
)
def test(test_path):
    os.system('docker-compose build web')
    os.system('docker-compose build worker')
    os.system(f'docker-compose run --rm web pytest {test_path}')


@ctrl.command()
def shell():
    os.system('docker-compose run --rm web bash')
