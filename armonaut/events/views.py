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
from sqlalchemy.orm.exc import NoResultFound
from armonaut.events.forms import PusherAuthenticateForm
from armonaut.project.models import Project, ProjectRole


_PROJECT_CHANNEL_REGEX = re.compile(r'^private-project-([^/]+)/([^/]+)$')


@view_config(
    route_name='auth.pusher',
    renderer='json',
    uses_session=True,
    require_csrf=True,
    require_methods=['POST'],
    permission='project:read'
)
def auth_pusher(request, _form_class=PusherAuthenticateForm):
    form = _form_class(request.POST)
    if not form.validate():
        return HTTPForbidden('Did not send correct information to authenticate with Pusher.')

    # Grab the project's slug from the channel name.
    match = _PROJECT_CHANNEL_REGEX.match(form.channel_name.data)
    if match is None:
        return HTTPForbidden(f'Malformed channel_name `{form.channel_name.data}`.')
    owner, name = match.groups()

    # Attempt to look up the project, if it exists then we need
    # to check if the project is either public or there exists
    # a ProjectRole with our user id and the project id attached.
    try:
        project = (
            request.db.query(Project)
            .filter(Project.owner == owner)
            .filter(Project.name == name)
            .one()
        )
    except NoResultFound:
        return HTTPForbidden('Could not find a project with this channel.')

    # Non-public projects require a ProjectRole for our user.
    # We don't care what the RoleType is because the lowest tier
    # is READ_ONLY which we allow to bind to channels.
    if not project.public:
        try:
            (
                request.db.query(ProjectRole)
                .filter(ProjectRole.project_id == project.id)
                .filter(ProjectRole.user_id == request.user.id)
                .one()
            )
        except NoResultFound:
            return HTTPForbidden('Could not find a project with this channel.')

    # Authenticate with the project's channel.
    auth_json = request.pusher.authenticate(
        channel_name=form.channel_name.data,
        socket_id=form.socket_id.data
    )
    return auth_json
