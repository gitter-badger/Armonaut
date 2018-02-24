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
import pytest
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPForbidden
from tests.factories.projects import ProjectFactory
from armonaut.events import views


@pytest.mark.parametrize('post_data', [
    {'channel_name': ''},
    {'socket_id': ''},
    {'what_is_this': 'not_a_key'}
])
def test_auth_pusher_post_data_invalid(post_data, pyramid_request):
    project = ProjectFactory.create()
    pyramid_request.POST = MultiDict(post_data)

    with pytest.raises(HTTPForbidden):
        views.auth_pusher(pyramid_request, project)


@pytest.mark.parametrize('channel_name', [
    'private-project-owner-name',
    'private-owner@name',
    'project-owner@name',
    'owner@name'
])
def test_auth_pusher_malformed_channel_name(channel_name, pyramid_request):
    project = ProjectFactory.create(
        owner='owner',
        name='name'
    )

    pyramid_request.POST = MultiDict({'channel_name': channel_name, 'socket_id': '1'})

    with pytest.raises(HTTPForbidden):
        views.auth_pusher(pyramid_request, project)


@pytest.mark.parametrize(['owner', 'name'], [
    ('owner', 'nam'),
    ('owne', 'name'),
    ('owne', 'nam')
])
def test_auth_pusher_wrong_project_data(owner, name, pyramid_request):
    project = ProjectFactory.create(
        owner='owner',
        name='name'
    )

    pyramid_request.POST = MultiDict({
        'channel_name': f'private-project-{owner}@{name}',
        'socket_id': 1
    })

    with pytest.raises(HTTPForbidden):
        views.auth_pusher(pyramid_request, project)


def test_auth_pusher_authenticate(pyramid_request):
    auth_json = {'auth': 'json'}
    pusher = pretend.stub(authenticate=pretend.call_recorder(lambda *args, **kwargs: auth_json))

    project = ProjectFactory.create()

    channel_name = f'private-project-{project.owner}@{project.name}'

    pyramid_request.pusher = pusher
    pyramid_request.POST = MultiDict({
        'channel_name': channel_name,
        'socket_id': '1'
    })

    resp = views.auth_pusher(pyramid_request, project)

    assert resp == auth_json
    assert pusher.authenticate.calls == [
        pretend.call(channel_name=channel_name, socket_id='1')
    ]
