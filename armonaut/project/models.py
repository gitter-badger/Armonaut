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
from sqlalchemy import Column, BigInteger, Enum, String, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship, object_session, lazyload
from sqlalchemy.orm.exc import NoResultFound
from pyramid.authorization import Allow, Everyone
from pyramid.security import DENY_ALL
from armonaut.db import Model


class ProjectRoleType(enum.Enum):
    OWNER = 'owner'  # read, manage, admin
    COLLABORATOR = 'collaborator'  # read, manage
    READ_ONLY = 'read_only'  # read


class ProjectRole(Model):
    __tablename__ = 'project_roles'

    role_type = Column(Enum(ProjectRoleType), nullable=False)
    user = relationship('User', uselist=False, back_populates='roles')
    user_id = Column(
        ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )

    project = relationship('Project', uselist=False, back_populates='roles')
    project_id = Column(
        ForeignKey('projects.id', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False
    )


class Project(Model):
    __tablename__ = 'projects'
    __table_args__ = (UniqueConstraint('name', 'owner', name='uix_slug'),)

    active = Column(Boolean, default=False, nullable=False)

    github_id = Column(BigInteger, nullable=False, index=True)

    name = Column(String(255), nullable=False, index=True)
    owner = Column(String(255), nullable=False, index=True)

    public = Column(Boolean, nullable=False)

    webhook_id = Column(String)
    webhook_secret = Column(String(255))

    builds = relationship('Build', back_populates='project')
    roles = relationship('ProjectRole', back_populates='project')

    @property
    def slug(self):
        return f'{self.owner}/{self.name}'

    def __acl__(self):
        session = object_session(self)
        acls = [(Allow, 'group:admins', ['admin'])]

        query = session.query(ProjectRole).filter(ProjectRole.project == self)
        query = query.options(lazyload('project'))
        query = query.options(lazyload('user'))

        def sorted_key(item):
            return [
                ProjectRoleType.OWNER,
                ProjectRoleType.COLLABORATOR,
                ProjectRoleType.READ_ONLY
            ].index(item)

        for role in sorted(query.all(), key=sorted_key):
            if role.role_type == ProjectRoleType.OWNER:
                acls.append((Allow, str(role.account.user_id), ['project:admin', 'project:manage', 'project:read']))
            elif role.role_type == ProjectRoleType.COLLABORATOR:
                acls.append((Allow, str(role.account.user_id), ['project:manage', 'project:read']))
            elif role.role_type == ProjectRoleType.READ_ONLY:
                acls.append((Allow, str(role.user_id), ['project:read']))

        if self.public:
            acls.append((Allow, Everyone, ['project:read']))

        return acls


class ProjectFactory(object):
    """Factory object for Pyramid view traversal
    in order to determine the ACLs that a user
    has over a given project. This factory must
    be traversed twice (owner then name) before
    returning an object with ACLs.
    """
    def __init__(self, request):
        self.request = request
        self.owner = None

    def __getitem__(self, item):
        if self.owner is None:
            self.owner = item
            return self
        else:
            try:
                project = (
                    self.request.db.query(Project)
                    .filter(Project.owner == self.owner)
                    .filter(Project.name == item)
                    .one()
                )
                return project
            except NoResultFound:
                raise KeyError from None

    def __acl__(self):
        """We deny all here because we want to do a full traversal
        from owner to name not to stick in the middle.
        """
        return [DENY_ALL]
