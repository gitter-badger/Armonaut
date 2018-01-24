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


class TooManyFailedLogins(Exception):
    def __init__(self, *args, resets_in, **kwargs):
        self.resets_in = resets_in
        super(TooManyFailedLogins, self).__init__(*args, **kwargs)


class InvalidPasswordResetToken(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(InvalidPasswordResetToken, self).__init__(*args, **kwargs)


class IUserService(Interface):
    def get_user(user_id):
        """
        Return the user object that represented the given userid
        or None if there is no user for that ID.
        """

    def find_userid(email):
        """
        Returns the user ID of a user for the given username.
        """

    def check_password(user_id, password):
        """
        Returns a boolean representing whether the given password
        is valid for the given userid
        """

    def create_user(email, password):
        """
        Attempts to create a new user with the given attributes.
        """

    def update_user(user_id, **changes):
        """
        Updates the user object
        """

    def verify_user(user_id, email):
        """
        Verifies the user
        """


class IUserTokenService(Interface):
    def generate_token(user):
        """
        Generates a unique token based on user attributes
        """

    def get_user_by_token(token):
        """
        Gets the user corresponding to the token provided
        """
