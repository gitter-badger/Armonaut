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

from armonaut.db import Model
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID


class User(Model):
    __tablename__ = 'users'

    email = Column(String(96), nullable=False, index=True)
    password = Column(String(60), nullable=False)

    email_verify_code = Column(String(8), default=None)
    email_verify_expires = Column(DateTime, default=None)

    api_token = Column(
        UUID(as_uuid=True),
        server_default=text('gen_random_uuid()'),
        index=True
    )
