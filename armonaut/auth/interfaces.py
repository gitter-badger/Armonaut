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


class IUserService(Interface):
    def get_user(self, user_id):
        raise NotImplementedError()

    def find_user(self, email):
        raise NotImplementedError()

    def check_password(self, user_id, password):
        raise NotImplementedError()

    def create_user(self, email, password):
        raise NotImplementedError()

    def update_user(self, **changes):
        raise NotImplementedError()

    def verify_user(self, user_id, email):
        raise NotImplementedError()
