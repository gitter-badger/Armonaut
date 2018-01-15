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

import pretend
from armonaut.xss import xss_tween_factory


def test_xss_tween():
    """Assert that all responses receive all XSS protection headers.
    """
    response = pretend.stub(headers={})
    handler = pretend.call_recorder(lambda request: response)
    registry = pretend.stub(settings={})
    tween = xss_tween_factory(handler, registry)

    request = pretend.stub(
        path='/',
    )

    assert tween(request) is response
    assert response.headers == {
        'X-Frame-Options': 'deny',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'X-Permitted-Cross-Domain-Policies': 'none'
    }
