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

from armonaut import Model, login
from flask_login import UserMixin
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID


class User(Model, UserMixin):
    email = Column(String(96), nullable=False, index=True)
    password = Column(String(60), nullable=False)

    api_token = Column(
        UUID(as_uuid=True),
        server_default=text('gen_random_uuid()'),
        index=True
    )


@login.user_loader
def load_user(user_id):
    return User.get(user_id)
