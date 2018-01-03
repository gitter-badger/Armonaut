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
import flask
import typing


def cache_control(seconds: int, public: bool=True,
                  stale_while_revalidate: typing.Optional[bool]=None,
                  stale_if_error: typing.Optional[bool]=None):
    """
    Controls HTTP and Fastly caching on a view with a given number
    of seconds in both Cache-Control and Surrogate-Control headers.
    Use this decorator on any view that requires caching.

    :param int seconds: Number of seconds to cache the response
    :param bool public: If True the cache can be maintained by proxies.
    :param typing.Optional[bool] stale_while_revalidate:
        If True Fastly will show stale content while a background
        process fetches the most recent content from the origin servers.
    :param typing.Optional[bool] stale_if_error:
        If True Fastly will show stale content if the origin servers are erroring.
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            response = flask.make_response(view(*args, **kwargs))  # type: flask.Response

            if flask.current_app.config.get('CACHE_CONTROL_ENABLED', False):

                # HTTP Cache-Control headers
                if seconds:
                    if public:
                        response.cache_control.public = True
                    else:
                        response.cache_control.private = True
                    response.cache_control.max_age = seconds
                else:
                    response.cache_control.no_cache = True
                    response.cache_control.no_store = True
                    response.cache_control.must_revalidate = True

                # Fastly Surrogate-Control headers
                if flask.current_app.config.get('FASTLY_ENABLED'):
                    values = []
                    if seconds is not None:
                        values.append(f'max-age={seconds}')
                    if stale_while_revalidate is not None:
                        values.append(f'stale-while-revalidate={stale_while_revalidate}')
                    if stale_if_error is not None:
                        values.append(f'stale-if-error={stale_if_error}')
                    response.headers['Surrogate-Control'] = ', '.join(values)

            return response
        return wrapped
    return decorator
