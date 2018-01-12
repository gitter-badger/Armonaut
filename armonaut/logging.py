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

import logging.config
import threading
import uuid

import structlog
import structlog.stdlib

from armonaut.__about__ import __version__


RENDERER = structlog.processors.JSONRenderer()


class StructlogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        if not record.name.startswith('armonaut.'):
            event_dict = {
                'logger': record.name,
                'level': record.levelname,
                'event': record.msg,
                'thread': threading.get_ident()
            }
            record.msg = RENDERER(None, None, event_dict)
        return super().format(record)


def _create_id(request):
    return str(uuid.uuid4().hex)


def _create_logger(request):
    logger = structlog.get_logger('armonaut.request')
    logger = logger.bind(**{'request.id': request.id})
    return logger


def includeme(config):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structlog': {
                '()': 'armonaut.logging.StructlogFormatter'
            }
        },
        'handlers': {
            'primary': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'structlog'
            },
            'sentry': {
                'class': 'raven.handlers.logging.SentryHandler',
                'level': 'ERROR',
                'dsn': config.registry.settings.get('sentry.dsn'),
                'release': __version__,
                'transport': 'raven.transport.requests.RequestsHTTPTransport'
            }
        },
        'root': {
            'level': config.registry.settings.get('logging.level', 'INFO'),
            'handlers': ['primary', 'sentry']
        }
    })

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            RENDERER
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger
    )

    config.add_request_method(_create_id, name='id', reify=True)
    config.add_request_method(_create_logger, name='log', reify=True)
