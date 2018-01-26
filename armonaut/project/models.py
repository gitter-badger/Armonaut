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

import enum
from sqlalchemy import Column, Enum, String, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from armonaut.db import Model


class ProjectHost(enum.Enum):
    GITHUB = 'github'
    GITLAB = 'gitlab'
    BITBUCKET = 'bitbucket'


class RoleType(enum.Enum):
    OWNER = 'owner'  # read, commit, admin
    COLLABORATOR = 'collaborator'  # read, commit


class Role(Model):
    __tablename__ = 'roles'

    role_type = Column(Enum(RoleType), nullable=False)
    user = relationship('Account', uselist=False, back_populates='roles')
    user_id = Column(
        ForeignKey('accounts.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )

    project = relationship('Project', uselist=False, back_populates='roles')
    project_id = Column(
        ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )


class Project(Model):
    __tablename__ = 'projects'
    __table_args__ = (UniqueConstraint('host', 'name', 'owner', name='uix_slug'),)

    active = Column(Boolean, default=False, nullable=False)

    host = Column(Enum(ProjectHost), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255), nullable=False, index=True)

    webhook_id = Column(String)
    webhook_secret = Column(String(255))

    builds = relationship('Build', back_populates='project')
    roles = relationship('Role', back_populates='project')

    @property
    def slug(self):
        return f'{str(self.host)}/{self.owner}/{self.name}'
