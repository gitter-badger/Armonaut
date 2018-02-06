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

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_multiauth import MultiAuthenticationPolicy
from armonaut.auth.services import database_login_factory, oauth_state_factory
from armonaut.auth.interfaces import IUserService, IOAuthStateService
from armonaut.auth.policies import SessionAuthenticationPolicy


REDIRECT_FIELD_NAME = 'next'
OAUTH_SCOPES = ' '.join(['user', 'user:email', 'repo', 'repo:status', 'repo_deployment', 'read:org', 'write:repo_hook'])


def _authenticate(userid, request):
    login_service = request.find_service(IUserService, context=None)
    user = login_service.get_user(userid)

    if user is None:
        return None

    principals = []
    if user.is_superuser:
        principals.append('group:admins')
    return principals


def _user(request):
    userid = request.authenticated_userid
    if userid is None:
        return None
    login_service = request.find_service(IUserService, context=None)
    return login_service.get_user(userid)


def includeme(config):
    config.register_service_factory(database_login_factory, IUserService)
    config.register_service_factory(oauth_state_factory, IOAuthStateService)

    config.set_authentication_policy(
        MultiAuthenticationPolicy([
            SessionAuthenticationPolicy(callback=_authenticate)
        ])
    )
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # Add a request method adds a `user` object.
    config.add_request_method(_user, name='user', reify=True)
