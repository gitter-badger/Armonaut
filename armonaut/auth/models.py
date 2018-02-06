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

from sqlalchemy import Column, String, DateTime, BigInteger, Text, Boolean
from sqlalchemy import sql
from sqlalchemy.orm import relationship
from armonaut.db import Model


class User(Model):
    __tablename__ = 'users'

    github_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=False, index=True)
    display_name = Column(Text, nullable=False)
    avatar_url = Column(Text, nullable=False)

    access_token = Column(Text, nullable=False)

    is_superuser = Column(Boolean, nullable=False)

    joined_date = Column(DateTime, nullable=False, server_default=sql.func.now())
    last_login = Column(DateTime, nullable=False, server_default=sql.func.now())

    roles = relationship('Roles', back_populates='user')
