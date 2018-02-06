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

from zope.interface import Interface


class IOAuthService(Interface):
    def create_state():
        """
        Creates a state token with a timeout
        """

    def check_state(state):
        """
        Checks a state token to see if it's valid
        """

    def exchange_code_for_access_token(request, state, code):
        """
        Exchanges a code and state for an access token
        """


class IUserService(Interface):
    def get_user(user_id):
        """
        Return the user object that represented the given userid
        or None if there is no user for that ID.
        """

    def find_userid(username):
        """
        Returns the user ID of a user for the given username.
        """

    def update_user(user_id, **changes):
        """
        Updates the user object
        """

    def get_user_from_access_token(request, access_token):
        """
        Gets a user from an access token from OAuth flow
        """
