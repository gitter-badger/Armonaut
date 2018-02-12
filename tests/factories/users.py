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
import factory.fuzzy
from armonaut.auth.models import User
from . import ArmonautFactory


class UserFactory(ArmonautFactory):
    class Meta:
        model = User

    github_id = factory.fuzzy.FuzzyInteger(low=1, high=10000)
    username = factory.fuzzy.FuzzyText(length=12)
    display_name = factory.fuzzy.FuzzyText(length=12)
    avatar_url = factory.fuzzy.FuzzyText(length=12)
    access_token = factory.fuzzy.FuzzyText(length=32)

    is_superuser = False

    joined_date = factory.fuzzy.FuzzyNaiveDateTime(
        datetime.datetime(2017, 1, 1),
        datetime.datetime(2018, 1, 1)
    )
    last_login = factory.fuzzy.FuzzyNaiveDateTime(
        datetime.datetime(2017, 1, 1)
    )
