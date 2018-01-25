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

from wtforms import Form as _Form
from wtforms.validators import StopValidation, ValidationError
from zxcvbn import zxcvbn


class PasswordStrengthValidator:
    def __init__(self, *, user_input_fields=None, required_strength=2):
        self.user_input_fields = user_input_fields
        self.required_strength = required_strength

    def __call__(self, form, field):
        user_inputs = []
        for fieldname in self.user_input_fields:
            try:
                user_inputs.append(form[fieldname].data)
            except KeyError:
                raise ValidationError(f'Invalid field name: {fieldname!r}')

        results = zxcvbn(field.data, user_inputs=user_inputs)

        if results['score'] < self.required_strength:
            message = (results['feedback']['warning']
                       if results['feedback']['warning']
                       else 'Password is too easily guessed.')
            if results['feedback']['suggestions']:
                message += ' ' + ', '.join(results['feedback']['suggestions'])
            raise ValidationError(message)


class Form(_Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._form_errors = []

    def validate(self, *args, **kwargs):
        success = super().validate(*args, **kwargs)

        # Determine what form level validators we have to run.
        form_validators = getattr(self.meta, "validators", [])
        full_validate = getattr(self, "full_validate", None)
        if full_validate is not None:
            form_validators.append(full_validate.__func__)

        # Attempt run any form level validators now.
        self._form_errors = []
        for validator in form_validators:
            try:
                validator(self)
            except StopValidation as exc:
                success = False
                if exc.args and exc.args[0]:
                    self._form_errors.append(exc.args[0])
                break
            except ValueError as exc:
                success = False
                self._form_errors.append(exc.args[0])

        return success

    @property
    def errors(self):
        if self._errors is None:
            self._errors = super().errors
            if self._form_errors:
                self._errors["__all__"] = self._form_errors
        return self._errors
