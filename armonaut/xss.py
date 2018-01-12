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

from pyramid.tweens import INGRESS


def xss_tween_factory(handler, registry):
    def xss_tween(request):
        response = handler(request)
        response.headers['X-Frame-Options'] = 'deny'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
        return response
    return xss_tween


def includeme(config):
    config.add_tween(
        'armonaut.xss.xss_tween_factory',
        under=[INGRESS]
    )
