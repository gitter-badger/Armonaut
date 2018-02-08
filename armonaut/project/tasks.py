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

import re
from armonaut import tasks
from armonaut.project.models import Project, ProjectRole, ProjectRoleType

_NEXT_URL_REGEX = re.compile(r'<(https://api\.github\.com/[^>]+)>; rel="next"')


@tasks.task(ignore_result=True, acks_late=True)
def synchronize_user(request, user):

    def list_all_projects(affiliation):
        """Helper function which traverses GitHubs pagination API in order
        to list all of a users repositories they have access to based on
        that users affiliation to the repository.
        """
        next_url = 'https://api.github.com/user/repos'
        repositories = []
        while next_url is not None:
            with request.http.get(next_url, params={'affiliation': affiliation, 'sort': 'updated'}) as r:
                next_url = None
                link = r.headers.get('Link')
                if link:
                    match = _NEXT_URL_REGEX.search(link)
                    if match is not None:
                        next_url = match.group(1)
                repositories.extend(r.json())
        return repositories

    def update_all_projects(project_role_type, repos):
        for repo in repos:
            project = (
                request.db.query(Project)
                .filter(Project.github_id == repo['id'])
                .first()
            )
            if project is None:
                project = Project()

            project.owner = repo['owner']['login']
            project.name = repo['name']
            project.public = not repo['private']

            project_role = (
                request.db.query(ProjectRole)
                .filter(ProjectRole.project == project)
                .filter(ProjectRole.user == user)
                .first()
            )
            if project_role is None:
                project_role = ProjectRole()
                project_role.user = user
                project_role.project = project
            if project_role.role_type != project_role_type:
                project_role.role_type = project_role_type
                request.db.add(project_role)
            request.db.add(project)

        request.db.flush()

    request.http.headers['Authorization'] = f'token {user.access_token}'
    try:
        repos_owner = list_all_projects('owner')
        repos_collaborator = list_all_projects('collaborator')
        repos_org_member = list_all_projects('organization_member')

        update_all_projects(repos_owner, ProjectRoleType.OWNER)
        update_all_projects(repos_collaborator, ProjectRoleType.COLLABORATOR)
        update_all_projects(repos_org_member, ProjectRoleType.READ_ONLY)
    finally:
        request.http.headers.pop('Authorization')
