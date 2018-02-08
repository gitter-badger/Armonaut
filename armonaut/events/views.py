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

import re
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from armonaut.events.forms import PusherAuthenticateForm


_PROJECT_CHANNEL_REGEX = re.compile(r'^private-project-([^@]+)@([^@]+)$')


@view_config(
    route_name='auth.pusher',
    renderer='json',
    uses_session=True,
    require_csrf=True,
    require_methods='POST',
    permission='project:read'
)
def auth_pusher(request, project, _form_class=PusherAuthenticateForm):
    form = _form_class(request.POST)
    if not form.validate():
        raise HTTPForbidden('Did not send correct information to authenticate with Pusher.')

    # Grab the project's slug from the channel name.
    match = _PROJECT_CHANNEL_REGEX.match(form.channel_name.data)
    if match is None:
        raise HTTPForbidden(f'Malformed channel_name `{form.channel_name.data}`.')

    # Make sure that the channel we're authenticating with is the same
    # as what we've declared in the view's route.
    owner, name = match.groups()
    if project.owner != owner or project.name != name:
        raise HTTPForbidden('Route and channel name do not match.')

    # Authenticate with the project's channel.
    auth_json = request.pusher.authenticate(
        channel_name=form.channel_name.data,
        socket_id=form.socket_id.data
    )
    return auth_json
