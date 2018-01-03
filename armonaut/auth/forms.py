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

from wtforms import Form, BooleanField, PasswordField, validators
from wtforms.fields.html5 import EmailField


class RegisterForm(Form):
    email = EmailField(
        'Email Address',
        [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=96)]
    )
    password = PasswordField(
        'Password',
        [validators.DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        [validators.DataRequired(),
         validators.EqualTo('password', message='Passwords do not match.')]
    )
    accept_tos = BooleanField('I accept the Terms and Services', [validators.DataRequired()])


class LoginForm(Form):
    email = EmailField(
        'Email Address',
        [validators.DataRequired(), validators.Email(), validators.Length(min=4, max=96)]
    )
    password = PasswordField(
        'Password',
        [validators.DataRequired()]
    )
    remember_me = BooleanField('Remember Me')
