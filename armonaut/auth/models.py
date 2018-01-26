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

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy import sql
from sqlalchemy.orm import relationship
from armonaut.db import Model


class User(Model):
    __tablename__ = 'users'

    email = Column(String(96), nullable=False, index=True, unique=True)
    password = Column(String(128), nullable=False)

    is_superuser = Column(Boolean, nullable=False)
    is_staff = Column(Boolean, nullable=False)

    joined_date = Column(DateTime, nullable=False, server_default=sql.func.now())
    password_date = Column(DateTime, nullable=False, server_default=sql.func.now())
    last_login = Column(DateTime, nullable=False, server_default=sql.func.now())

    accounts = relationship('Account', back_populates='user')


class Account(Model):
    __tablename__ = 'accounts'

    username = Column(String(255), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)

    user = relationship('User', back_populates='accounts', uselist=False)
    user_id = Column(
        ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )
