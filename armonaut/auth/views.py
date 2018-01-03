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

from flask import redirect, url_for, request
from flask_login import current_user, logout_user
from armonaut.auth import auth_blueprint


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    raise NotImplementedError()


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    raise NotImplementedError()


@auth_blueprint.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(request.args.get('next', url_for('index')))
