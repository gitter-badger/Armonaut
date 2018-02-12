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

import pytest
from pyramid.security import Allow, Everyone
from armonaut.project.models import Project, ProjectRoleType
from ...factories.projects import ProjectRoleFactory, ProjectFactory


def test_slug():
    project = Project()
    project.owner = 'owner'
    project.name = 'name'

    assert project.slug == 'owner/name'


@pytest.mark.parametrize(
    ['project_role_type', 'acls'],
    [(ProjectRoleType.OWNER, [(Allow, 'group:admins', ['admin']), (Allow, '1', ['project:admin', 'project:manage', 'project:read'])]),
     (ProjectRoleType.COLLABORATOR, [(Allow, 'group:admins', ['admin']), (Allow, '2', ['project:manage', 'project:read'])]),
     (ProjectRoleType.READ_ONLY, [(Allow, 'group:admins', ['admin']), (Allow, '3', ['project:read'])])]
)
def test_project_acls(project_role_type, acls, db_session):
    role = ProjectRoleFactory.create(role_type=project_role_type)
    project = role.project
    user = role.user

    project.public = False
    user.id = 1
    db_session.add(project)
    db_session.add(user)
    db_session.flush()

    assert project.__acl__() == acls


def test_public_project_acls(db_session):
    project = ProjectFactory.create()

    assert project.__acl__() == [(Allow, 'group:admins', ['admin']), (Allow, Everyone, ['project:read'])]
