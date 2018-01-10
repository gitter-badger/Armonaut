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
import copy

SELF = '\'self\''
NONE = '\'none\''


def _serialize_policy(policy) -> str:
    return '; '.join([
        ' '.join([k] + [v2 for v2 in v if v2 is not None])
        for k, v in sorted(policy.items())
    ])


def content_security_policy_tween_factory(handler, registry):
    def content_security_policy_tween(request):
        resp = handler(request)

        try:
            policy = request.find_service(name='csp')
        except ValueError:
            policy = collections.defaultdict(list)

        # Disable Content-Security-Policy for debugtoolbar
        policy = _serialize_policy(policy).format(request=request)
        if not request.path.startswith('/_debug_toolbar/') and policy:
            resp.headers['Content-Security-Policy'] = policy

        return resp
    return content_security_policy_tween


class ContentSecurityPolicy(collections.defaultdict):
    def __init__(self, policy=None):
        super().__init__(list, policy or {})

    def merge(self, policy):
        for key, attrs in policy.items():
            self[key].extend(attrs)


def csp_factory(_, request):
    try:
        return ContentSecurityPolicy(copy.deepcopy(request.registry.settings['csp']))
    except KeyError:
        return ContentSecurityPolicy({})


def includeme(config):
    config.register_service_factory(csp_factory, name='csp')
    config.add_settings({
        'bare-uri': [SELF],
        'block-all-mixed-content': [],
        'connect-src': [SELF],
        'default-src': [NONE],
        'font-src': [SELF, 'fonts.gstatic.com'],
        'form-action': [SELF],
        'frame-ancestors': [NONE],
        'frame-src': [NONE],
        'img-src': [SELF],
        'script-src': [SELF],
        'style-src': [SELF, 'fonts.googleapis.com']
    })
    config.add_tween('armonaut.csp.content_security_policy_tween_factory')