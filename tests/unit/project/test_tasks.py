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

import pretend
import pytest
from armonaut.project.tasks import (
    list_all_projects, update_all_projects, synchronize_user
)
from armonaut.project import tasks
from armonaut.project.models import ProjectRoleType, Project
from ...factories.users import UserFactory
from ...factories.projects import ProjectFactory, ProjectRoleFactory


def test_list_all_projects_single_repository():
    resp = pretend.stub(
        json=pretend.call_recorder(lambda: [{'id': 1234}]),
        headers={},
        __enter__=lambda *args, **kwargs: resp,
        __exit__=lambda *args, **kwargs: None
    )
    request = pretend.stub(
        http=pretend.stub(
            get=pretend.call_recorder(lambda *args, **kwargs: resp)
        )
    )

    repos = list_all_projects(request, 'owner')

    assert repos == [{'id': 1234}]
    assert request.http.get.calls == [pretend.call(
        'https://api.github.com/user/repos',
        params={'affiliation': 'owner',
                'sort': 'updated'}
    )]
    assert resp.json.calls == [pretend.call()]


def test_list_all_projects_no_link_match():
    resp = pretend.stub(
        json=pretend.call_recorder(lambda: [{'id': 1234}]),
        headers={'Link': 'foo'},
        __enter__=lambda *args, **kwargs: resp,
        __exit__=lambda *args, **kwargs: None
    )
    request = pretend.stub(
        http=pretend.stub(
            get=pretend.call_recorder(lambda *args, **kwargs: resp)
        )
    )

    repos = list_all_projects(request, 'owner')

    assert repos == [{'id': 1234}]
    assert request.http.get.calls == [pretend.call(
        'https://api.github.com/user/repos',
        params={'affiliation': 'owner',
                'sort': 'updated'}
    )]
    assert resp.json.calls == [pretend.call()]


def test_list_all_projects_multiple_pages():
    link = """<https://api.github.com/user/repos?affiliation=owner&sort=updated&page=2>; rel="next",
  <https://api.github.com/user/repos?affiliation=owner&sort=updated&page=3>; rel="last",
  <https://api.github.com/user/repos?affiliation=owner&sort=updated&page=1>; rel="first",
  <https://api.github.com/user/repos?affiliation=owner&sort=updated&page=1>; rel="prev"""

    resp1 = pretend.stub(
        json=pretend.call_recorder(lambda: [{'id': 1234}]),
        headers={'Link': link},
        __enter__=lambda *args, **kwargs: resp1,
        __exit__=lambda *args, **kwargs: None
    )
    resp2 = pretend.stub(
        json=pretend.call_recorder(lambda: [{'id': 2345}]),
        headers={'Link': 'foo'},
        __enter__=lambda *args, **kwargs: resp2,
        __exit__=lambda *args, **kwargs: None
    )
    resps = iter([resp1, resp2])

    request = pretend.stub(
        http=pretend.stub(
            get=pretend.call_recorder(lambda *args, **kwargs: next(resps))
        )
    )

    repos = list_all_projects(request, 'owner')

    assert repos == [{'id': 1234}, {'id': 2345}]
    assert request.http.get.calls == [pretend.call(
        'https://api.github.com/user/repos',
        params={'affiliation': 'owner',
                'sort': 'updated'}
    ), pretend.call(
        'https://api.github.com/user/repos?affiliation=owner&sort=updated&page=2',
        params={'affiliation': 'owner',
                'sort': 'updated'}
    )]
    assert resp1.json.calls == [pretend.call()]
    assert resp2.json.calls == [pretend.call()]


def test_new_project_with_owner(db_session):
    request = pretend.stub(
        db=db_session
    )

    user = UserFactory.create()

    update_all_projects(
        request,
        user,
        ProjectRoleType.OWNER,
        [{'id': 1234, 'owner': {'login': user.username}, 'name': 'foobar', 'private': False}]
    )

    project = db_session.query(Project).filter(Project.github_id == 1234).first()
    assert not project.active
    assert project.public
    assert project.github_id == 1234
    assert project.owner == user.username
    assert project.name == 'foobar'
    assert len(project.roles) == 1

    role = project.roles[0]
    assert role.role_type == ProjectRoleType.OWNER
    assert role.user == user


@pytest.mark.parametrize(
    'project_role_type', [
        ProjectRoleType.COLLABORATOR, ProjectRoleType.READ_ONLY
    ]
)
def test_new_project_non_owner(db_session, project_role_type):
    request = pretend.stub(
        db=db_session
    )

    user = UserFactory.create()

    update_all_projects(
        request,
        user,
        project_role_type,
        [{'id': 1234, 'owner': {'login': user.username}, 'name': 'foobar', 'private': False}]
    )

    projects = db_session.query(Project).all()
    assert not projects


def test_project_role_updated(db_session):
    request = pretend.stub(
        db=db_session
    )

    project_role = ProjectRoleFactory.create(role_type=ProjectRoleType.READ_ONLY)
    project = project_role.project
    user = project_role.user

    update_all_projects(
        request,
        user,
        ProjectRoleType.COLLABORATOR,
        [{'id': project.github_id, 'owner': {'login': project.owner}, 'name': project.name, 'private': False}]
    )

    project = db_session.query(Project).filter(Project.github_id == project.github_id).first()
    assert len(project.roles) == 1

    role = project.roles[0]
    assert role.role_type == ProjectRoleType.COLLABORATOR
    assert role.user == user


@pytest.mark.parametrize(
    'project_role_type',
    [ProjectRoleType.OWNER,
     ProjectRoleType.COLLABORATOR,
     ProjectRoleType.READ_ONLY]
)
def test_update_all_projects_no_updates_required(db_session, project_role_type):
    request = pretend.stub(
        db=db_session
    )

    role = ProjectRoleFactory.create(role_type=project_role_type)
    project = role.project
    user = role.user

    update_all_projects(
        request,
        user,
        project_role_type,
        [{'id': project.github_id, 'owner': {'login': project.owner}, 'name': project.name, 'private': False}]
    )

    project = db_session.query(Project).filter(Project.github_id == project.github_id).first()
    assert len(project.roles) == 1

    role = project.roles[0]
    assert role.role_type == project_role_type
    assert role.user == user


def test_synchronize_user(monkeypatch):
    request = pretend.stub(
        http=pretend.stub(
            headers={}
        )
    )
    user = pretend.stub(
        access_token='access_token'
    )
    repos = pretend.stub()

    def _list_all_projects(req, affiliation):
        assert req is request
        assert req.http.headers == {'Authorization': 'token access_token'}
        return repos

    def _update_all_projects(req, usr, reps, project_role_type):
        assert req is request
        assert req.http.headers == {'Authorization': 'token access_token'}
        assert usr is user
        assert reps == repos
        assert isinstance(project_role_type, ProjectRoleType)

    list_all_projects = pretend.call_recorder(_list_all_projects)
    update_all_projects = pretend.call_recorder(_update_all_projects)

    monkeypatch.setattr(tasks, 'list_all_projects', list_all_projects)
    monkeypatch.setattr(tasks, 'update_all_projects', update_all_projects)

    synchronize_user(request, user)

    assert list_all_projects.calls == [
        pretend.call(request, 'owner'),
        pretend.call(request, 'collaborator'),
        pretend.call(request, 'organization_member')
    ]
    assert update_all_projects.calls == [
        pretend.call(request, user, repos, ProjectRoleType.OWNER),
        pretend.call(request, user, repos, ProjectRoleType.COLLABORATOR),
        pretend.call(request, user, repos, ProjectRoleType.READ_ONLY)
    ]
    assert request.http.headers == {}
