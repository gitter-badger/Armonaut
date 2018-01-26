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

import disposable_email_domains
import wtforms
import wtforms.fields.html5

from armonaut import forms
from armonaut.auth.interfaces import TooManyFailedLogins


class RegistrationForm(forms.Form):
    email = wtforms.fields.html5.EmailField(
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Email(
                message=('The email address you have chosen is not a '
                         'valid format. Please try again.')
            )
        ]
    )

    password = wtforms.PasswordField(
        validators=[
            wtforms.validators.DataRequired(),
            forms.PasswordStrengthValidator(
                user_input_fields=['email']
            )
        ]
    )

    password_confirm = wtforms.PasswordField(
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.EqualTo(
                'password', 'The two password fields do not match.'
            )
        ]
    )

    def __init__(self, *args, user_service, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = user_service

    def validate_email(self, field):
        if self.user_service.find_userid(field.data) is not None:
            raise wtforms.validators.ValidationError(
                'This email address is already being used by another account. '
                'Please use a different email address.'
            )

        domain = field.data.split('@')[-1]
        if domain in disposable_email_domains.blacklist:
            raise wtforms.validators.ValidationError(
                'This email address domain is not allowed. Please use a '
                'different email address.'
            )


class LoginForm(forms.Form):
    email = wtforms.fields.html5.EmailField(
        validators=[
            wtforms.validators.DataRequired()
        ]
    )

    password = wtforms.fields.PasswordField(
        validators=[
            wtforms.validators.DataRequired()
        ]
    )

    def __init__(self, *args, user_service, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = user_service

    def validate_password(self, field):
        userid = self.user_service.find_userid(self.email.data)
        if userid is not None:
            try:
                if not self.user_service.check_password(userid, field.data):
                    raise wtforms.validators.ValidationError(
                        'The email address and password combination you have '
                        'provided is invalid. Please try again or request a '
                        'password reset.'
                    )
            except TooManyFailedLogins:
                raise wtforms.validators.ValidationError(
                    'There have been too many unsuccessful login attempts. '
                    'Try again later or contact support.'
                )
        else:

            # This isn't a security flaw as email-enumeration
            # can occur already via registration screen.
            raise wtforms.validators.ValidationError(
                'There is no account registered for this email address.'
            )
