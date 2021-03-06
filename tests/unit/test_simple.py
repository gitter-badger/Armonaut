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


def test_index(webtest):
    """Assert that the application is capable of returning 200.
    """
    resp = webtest.get('/')

    assert resp.status_code == 200
    assert resp.content_type == 'text/html'


def test_not_found(webtest):
    """Assert that the application is capable of returning 400.
    """
    resp = webtest.get('/asdasdasd/', status=404)

    assert resp.status_code == 404
