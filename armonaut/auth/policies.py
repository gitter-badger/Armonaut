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

from pyramid.authentication import (
    BasicAuthAuthenticationPolicy as _BasicAuthAuthenticationPolicy,
    SessionAuthenticationPolicy as _SessionAuthenticationPolicy
)
from armonaut.auth.interfaces import IUserService
from armonaut.cache.http import add_vary_callback


class BasicAuthAuthenticationPolicy(_BasicAuthAuthenticationPolicy):
    def unauthenticated_userid(self, request):
        request.add_response_callback(add_vary_callback('Authorization'))

        email = _BasicAuthAuthenticationPolicy.unauthenticated_userid(self, request)

        if email is not None:
            login_service = request.find_service(IUserService, context=None)
            return str(login_service.find_userid(email))


class SessionAuthenticationPolicy(_SessionAuthenticationPolicy):
    def unauthenticated_userid(self, request):
        request.add_response_callback(add_vary_callback('Cookie'))

        return _SessionAuthenticationPolicy.unauthenticated_userid(self, request)
