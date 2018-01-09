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

from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.viewderivers import INGRESS, csrf_view


SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}


def require_method_view(view, info):
    require_methods = info.options.get('require_methods', SAFE_METHODS)
    explicit = bool(info.options.get('require_methods'))

    # Support disabling via @view_config(require_methods=False)
    if not require_methods:
        return view

    def wrapped(context, request):
        if (request.method not in require_methods and
                (getattr(request, 'exception', None) is None or explicit)):
            raise HTTPMethodNotAllowed(
                headers={'Allow': ', '.join(require_methods)}
            )
        return view(context, request)
    return wrapped


require_method_view.options = {'require_methods'}


def includeme(config):
    config.set_default_csrf_options(require_csrf=True)

    # Make sure that the csrf_view comes over the
    # secure_view so that we can't access session cookie
    # without ensuring this isn't a cross-site request.
    config.add_view_deriver(csrf_view, under=INGRESS, over='secured_view')

    # Also add view deriver that will ensure that only allowed
    # methods get called on particular views. Needs to happen
    # prior to CSRF checks to prevent CSRF checks from firing
    # on views that we don't expect them to.
    config.add_view_deriver(
        require_method_view,
        under=INGRESS,
        over='csrf_view'
    )
