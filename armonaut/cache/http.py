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

import collections
import functools


BUFFER_MAX = 1 * 1024 * 1024


def add_vary_callback(*varies):
    def wrapped(request, response):
        vary = set(response.vary if response.vary is not None else [])
        vary |= set(varies)
        response.vary = vary
    return wrapped


def add_vary(*varies):
    def wrapper(view):
        @functools.wraps(view)
        def wrapped(context, request):
            request.add_response_callback(add_vary_callback(*varies))
            return view(context, request)
        return wrapped
    return wrapper


def cache_control(seconds, public=True,
                  stale_while_revalidate=None,
                  stale_if_error=None):
    def inner(view):
        @functools.wraps(view)
        def wrapped(context, request):
            response = view(context, request)
            if not request.registry.settings.get('pyramid.prevent_http_cache', False):
                if seconds:
                    if public:
                        response.cache_control.public = True
                    else:
                        response.cache_control.private = True

                    response.cache_control.stale_while_revalidate = \
                        stale_while_revalidate
                    response.cache_control.stale_if_error = stale_if_error
                    response.cache_control.max_age = seconds
                else:
                    response.cache_control.no_cache = True
                    response.cache_control.no_store = True
                    response.cache_control.must_revalidate = True

            return response
        return wrapped
    return inner


def conditional_http_tween_factory(handler, registry):
    def conditional_http_tween(request):
        response = handler(request)

        if response.last_modified is not None:
            response.condional_response = True

        streaming = not isinstance(response.app_iter, collections.Sequence)

        if response.etag is not None:
            response.condional_response = True
        elif (request.method in {'GET', 'HEAD'} and
                response.status_code == 200):
            if streaming and response.content_length <= BUFFER_MAX:
                response.body  # noqa: Load the response body into memory
                streaming = False
            if not streaming:
                response.condional_response = True
                response.md5_etag()
        return response
    return conditional_http_tween


def includeme(config):
    config.add_tween('armonaut.cache.http.conditional_http_tween_factory')
