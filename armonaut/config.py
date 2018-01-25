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

import enum
import os
import typing
import transaction
from pyramid.response import Response
from pyramid.config import Configurator as _Configurator
from pyramid.tweens import EXCVIEW


class Environment(enum.Enum):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'


class Configurator(_Configurator):
    def add_wsgi_middleware(self, middleware, *args, **kwargs):
        middlewares = self.get_settings().setdefault('wsgi.middlewares', [])
        middlewares.append((middleware, args, kwargs))

    def make_wsgi_app(self, *args, **kwargs):
        app = super().make_wsgi_app(*args, **kwargs)
        for middleware, args, kw in self.get_settings()['wsgi.middlewares']:
            app = middleware(app, *args, **kw)
        return app


def require_https_tween_factory(handler, registry):
    if not registry.settings.get('armonaut.require_https', True):
        return handler

    def require_https_tween(request):
        if request.scheme != 'https':
            resp = Response('SSL is required.',
                            status=403,
                            content_type='text/plain')
            resp.status = '403 SSL is required'
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


def _tm_activate_hook(request) -> bool:
    # Don't activate our transaction manager on the debug toolbar
    # or on static resources
    if request.path.startswith(('/_debug_toolbar', '/static')):
        return False
    return True


def configure(settings=None) -> Configurator:
    if settings is None:
        settings = {}

    # Gather all settings from the environment
    maybe_set(settings, 'armonaut.env', 'ARMONAUT_ENV',
              coercer=lambda x: Environment(x.lower()),
              default=Environment.PRODUCTION)
    maybe_set(settings, 'armonaut.secret', 'ARMONAUT_SECRET')
    maybe_set(settings, 'armonaut.domain', 'ARMONAUT_DOMAIN')

    maybe_set(settings, 'celery.broker_url', 'REDIS_URL')
    maybe_set(settings, 'celery.result_url', 'REDIS_URL')
    maybe_set(settings, 'celery.scheduler_url', 'REDIS_URL')
    maybe_set(settings, 'database.url', 'DATABASE_URL')
    maybe_set(settings, 'ratelimit.url', 'REDIS_URL')

    maybe_set(settings, 'sessions.url', 'REDIS_URL')
    maybe_set(settings, 'sessions.secret', 'ARMONAUT_SECRET')

    maybe_set(settings, 'logging.level', 'LOGGING_LEVEL')

    maybe_set(settings, 'sentry.dsn', 'SENTRY_DSN')

    maybe_set(settings, 'mail.host', 'MAIL_HOST')
    maybe_set(settings, 'mail.port', 'MAIL_PORT')
    maybe_set(settings, 'mail.username', 'MAIL_USERNAME')
    maybe_set(settings, 'mail.password', 'MAIL_PASSWORD')
    maybe_set(settings, 'mail.ssl', 'MAIL_SSL', default=True)

    # TODO: Remove this after setting up Heroku TLS
    settings['armonaut.require_https'] = True

    # Setup our development environment
    if settings['armonaut.env'] == Environment.DEVELOPMENT:
        settings.setdefault('armonaut.require_https', False)
        settings.setdefault('pyramid.reload_assets', True)
        settings.setdefault('pyramid.reload_templates', True)
        settings.setdefault('pyramid.prevent_http_cache', True)
        settings.setdefault('debugtoolbar.hosts', ['0.0.0.0/0'])
        settings.setdefault('logging.level', 'DEBUG')
        settings.setdefault(
            'debugtoolbar.panels',
            [f'pyramid_debugtoolbar.panels.{panel}'
                for panel in [
                    'versions.VersionDebugPanel',
                    'settings.SettingsDebugPanel',
                    'headers.HeaderDebugPanel',
                    'request_vars.RequestVarsDebugPanel',
                    'renderings.RenderingsDebugPanel',
                    'logger.LoggingPanel',
                    'performance.PerformanceDebugPanel',
                    'routes.RoutesDebugPanel',
                    'sqla.SQLADebugPanel',
                    'tweens.TweensDebugPanel',
                    'introspection.IntrospectionDebugPanel'
                ]
             ]
        )

    # Create a configuration from the settings
    config = Configurator(settings=settings)

    # Include SRF support immediate after the Configurator instance
    # to ensure our defaults get set ASAP so no moficiatins before commit()
    config.include('.csrf')

    # Add configuration for logging
    config.include('.logging')

    # Add the Pyramid debugtoolbar for development debugging
    if config.registry.settings['armonaut.env'] == Environment.DEVELOPMENT:
        config.include('pyramid_debugtoolbar')

    # Configure Jinja2 as our template renderer
    config.include('pyramid_jinja2')
    config.add_settings({'jinja2.newstyle': True})

    for jinja2_renderer in ['.html']:
        config.add_jinja2_renderer(jinja2_renderer)
        config.add_jinja2_search_path('armonaut:templates', name=jinja2_renderer)

    # Setup our transaction manager before the database
    config.include('pyramid_retry')
    config.add_settings({
        'tm.attempts': 3,
        'tm.manager_hook': lambda request: transaction.TransactionManager(),
        'tm.activate_hook': _tm_activate_hook,
        'tm.annotate_user': False
    })
    config.include('pyramid_tm')

    # Register support for services
    config.include('pyramid_services')

    # Register emailing tasks
    config.include('pyramid_mailer')

    # Register support for database connections
    config.include('.db')

    # Register support for celery tasks
    config.include('.tasks')

    # Register support for sessions
    config.include('.sessions')

    # Register support for rate-limiting
    config.include('.rate_limit')

    # Register HTTP caching
    config.include('.cache.http')

    # Register authentication
    config.include('.auth')

    # Register XSS protections
    config.include('.xss')

    # Block non-HTTPS in production
    config.add_tween('armonaut.config.require_https_tween_factory')

    # Enable compression of our HTTP responses
    config.add_tween(
        'armonaut.compression.compression_tween_factory',
        over=[
            'armonaut.cache.http.conditional_http_tween_factory',
            'pyramid.debugtoolbar.toolbar_tween_factory',
            'armonaut.raven.raven_tween_factory',
            EXCVIEW
        ]
    )

    # Setup static file serving
    prevent_http_cache = \
        config.get_settings().get("pyramid.prevent_http_cache", False)
    max_age = 0 if prevent_http_cache else 10 * 365 * 24 * 60 * 60
    config.include('.static')
    config.add_static_view(
        'static',
        'armonaut:static/dist/',
        cache_max_age=max_age
    )
    config.whitenoise_serve_static(
        autorefresh=prevent_http_cache,
        max_age=max_age
    )
    config.whitenoise_add_files('armonaut:static/dist/', prefix='/static/')

    # Register Content-Security-Policy service
    config.include('.csp')

    # Register Raven last so that it's our outermost WSGI middleware
    config.include('.raven')

    # Scan everything for additional configuration
    config.scan(ignore=['armonaut.migrations.env',
                        'armonaut.celery',
                        'armonaut.routes',
                        'armonaut.wsgi'])

    # Load routes last to ensure all views are loaded first
    config.include('.routes')
    config.commit()

    return config
