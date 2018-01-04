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

import os
import typing
from pyramid.response import Response
from pyramid.config import Configurator


PRODUCTION = 'production'
DEVELOPMENT = 'development'


def require_https_tween_factory(handler, registry):
    if not registry.settings.get('enforce_https', True):
        return handler

    def require_https_tween(request):
        if request.scheme != 'https':
            resp = Response('SSL is required.',
                            status=403,
                            content_type='text/plain')
            resp.status = '403 SSL is required'
            resp.headers['X-Fastly-Error'] = '803'
            return resp

        return handler(request)
    return require_https_tween


def maybe_set(settings: typing.Dict[str, typing.Any],
              name: str,
              env: str,
              coercer: typing.Optional[typing.Callable[[str], typing.Any]]=None,
              default: typing.Any=None):

    value = os.environ.get(env)
    if value is not None:
        if coercer is not None:
            value = coercer(value)
        settings.setdefault(name, value)
    elif default is not None:
        settings.setdefault(name, default)
    else:
        raise RuntimeError(f'Could not get a value for `{name}` setting.')


def configure(settings=None) -> Configurator:
    if settings is None:
        settings = {}

    # Gather all settings from the environment
    maybe_set(settings, 'armonaut.env', 'ARMONUAT_ENV')
    maybe_set(settings, 'celery.broker_url', 'AMQP_URL')
    maybe_set(settings, 'celery.result_url', 'REDIS_URL')
    maybe_set(settings, 'celery.scheduler_url', 'REDIS_URL')
    maybe_set(settings, 'database.url', 'DATABASE_URL')
    maybe_set(settings, 'sessions.url', 'REDIS_URL')
    maybe_set(settings, 'ratelimit.url', 'REDIS_URL')

    if settings['armonaut.env'] == PRODUCTION:

    else:


    config = Configurator(settings=settings)

    # Configure Jinja2 as our template renderer
    config.include('pyramid_jinja2')
    config.add_settings({'jinja2.newstyle': True})

    for jinja2_renderer in ['.html']:
        config.add_jinja2_renderer(jinja2_renderer)
        config.add_jinja2_search_path('armonaut:templates', name=jinja2_renderer)

    # Block non-HTTPS in production
    config.add_tween('armonaut.config.require_https_tween_factory')

    # Enable compression of our HTTP responses
    config.add_tween('armonaut.compression.compression_tween_factory')

    # Scan everything for additional configuration
    config.scan(ignore=['armonaut.migrations.env',
                        'armonaut.celery',
                        'armonaut.wsgi'])
    config.commit()

    return config
