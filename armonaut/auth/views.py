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

import datetime
from urllib.parse import urlencode
from pyramid.httpexceptions import HTTPSeeOther, HTTPBadRequest
from pyramid.security import remember, forget
from pyramid.view import view_config
from armonaut.auth import REDIRECT_FIELD_NAME, OAUTH_SCOPES
from armonaut.auth.interfaces import IUserService, IOAuthStateService
from armonaut.utils.http import is_safe_url


@view_config(
    route_name='auth.authorize',
    uses_session=True,
    require_csrf=True,
    require_methods=['GET']
)
def authorize(request):
    state_service = request.find_service(IOAuthStateService, context=None)
    state = state_service.create_state()
    query = urlencode({
        'state': state,
        'scopes': OAUTH_SCOPES,
        'client_id': request.registry.settings['github.oauth_id'],
        'allow_signup': 'true'
    })
    resp = HTTPSeeOther(
        f'https://github.com/login/oauth/authorize?{query}'
    )
    return resp


@view_config(
    route_name='auth.callback',
    uses_session=True,
    require_csrf=True,
    require_methods=['GET']
)
def callback(request):
    state = request.GET.get('state')
    code = request.GET.get('code')

    if code is None or state is None:
        return HTTPBadRequest('Invalid OAuth callback')

    state_service = request.find_service(IOAuthStateService, context=None)
    if not state_service.check_state(state):
        return HTTPBadRequest('Expired OAuth state token. Try authorizing again.')

    user_service = request.find_service(IUserService, context=None)
    user_service.

    _login_user(request, userid)


@view_config(
    route_name='auth.logout',
    renderer='auth/logout.html',
    uses_session=True,
    require_csrf=True,
    require_methods=False
)
def logout(request, redirect_field_name=REDIRECT_FIELD_NAME):
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name))

    if request.method == 'POST':
        headers = forget(request)

        request.session.invalidate()

        # Make sure that the ?next=[URL] parameter is safe to redirect to.
        if (not redirect_to or
                not is_safe_url(url=redirect_to, host=request.host)):
            redirect_to = '/'

        resp = HTTPSeeOther(redirect_to, headers=dict(headers))
        return resp

    return {
        'redirect': {
            'field': REDIRECT_FIELD_NAME,
            'data': redirect_to
        }
    }


def _login_user(request, userid):

    # To protect against session fixation attacks we must force
    # invalidate the current session.
    if (request.unauthenticated_userid is not None and
            request.unauthenticated_userid != userid):
        request.session.invalidate()
    else:
        data = dict(request.session.items())
        request.session.invalidate()
        request.session.update(data)

    # Remember the userid using the authentication policy
    headers = remember(request, str(userid))

    # Cycle the CSRF token since we've crossed an authentication
    # boundary and we don't want to continue using the old one.
    request.session.new_csrf_token()

    # Whenever we log in the user we want to update their user so
    # that it records when the last login was.
    user_service = request.find_service(IUserService, context=None)
    user_service.update_user(userid, last_login=datetime.datetime.utcnow())

    return headers
