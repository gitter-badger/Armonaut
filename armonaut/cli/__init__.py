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
import pkgutil
import importlib


class _LazyConfig(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._config = None

    def __getattr__(self, item):
        if self._config is None:
            from armonaut.config import configure
            self._config = configure(*self._args, **self._kwargs)
        return getattr(self._config, item)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def armonaut(ctx):
    ctx.obj = _LazyConfig()


for _, name, _ in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    importlib.import_module(name)
