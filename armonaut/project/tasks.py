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
    """Synchronizes the latest information about the user from GitHub including
    user information and all repositories the user has access to.
    """
    request.http.headers['Authorization'] = f'token {user.access_token}'
    try:
        for affiliation, project_role_type in [
                ('owner', ProjectRoleType.OWNER),
                ('collaborator', ProjectRoleType.COLLABORATOR),
                ('organization_member', ProjectRoleType.READ_ONLY)
        ]:
            repos = list_all_projects(request, affiliation)
            update_all_projects(request, user, repos, project_role_type)
    finally:
        request.http.headers.pop('Authorization')


def list_all_projects(request, affiliation):
    """Helper function which traverses GitHubs pagination API in order
    to list all of a users repositories they have access to based on
    that users affiliation to the repository.
    """
    next_url = 'https://api.github.com/user/repos'
    repositories = []
    while next_url is not None:
        with request.http.get(next_url,
                              params={'affiliation': affiliation,
                                      'sort': 'updated'}) as r:
            next_url = None

            # Search for a 'next' link in the Link header.
            link = r.headers.get('Link')
            if link:
                match = _NEXT_URL_REGEX.search(link)
                if match is not None:
                    next_url = match.group(1)

            repositories.extend(r.json())
    return repositories


def update_all_projects(request, user, project_role_type, repos):
    """Given the role type that the user has for the list
    of repositories update all Projects within the database
    with the new role or create a new Project if there isn't one.
    """
    for repo in repos:
        project = (
            request.db.query(Project)
                      .filter(Project.github_id == repo['id'])
                      .first()
        )

        # Save this for use later to maybe save a database lookup.
        lookup_role = True

        # Only allow new projects to be created if
        # we're an owner of the project.
        if project is None:
            if project_role_type == ProjectRoleType.OWNER:
                # We're creating a new project so don't search
                # for roles. They won't be there. :)
                lookup_role = False

                project = Project()
                project.active = False
            else:
                continue

        # Update the project with the latest information.
        project.owner = repo['owner']['login']
        project.name = repo['name']
        project.public = not repo['private']
        project.github_id = repo['id']

        # See if there are any ProjectRoles that need to be updated.
        project_role = None
        if lookup_role:
            project_role = (
                request.db.query(ProjectRole)
                          .filter(ProjectRole.project == project)
                          .filter(ProjectRole.user == user)
                          .first()
            )

        # No ProjectRole exists for the user so we should create one.
        if project_role is None:
            project_role = ProjectRole()
            project_role.user = user
            project_role.project = project
            project_role.role_type = project_role_type
            request.db.add(project_role)

        # If the ProjectRole exists then we should update
        # the role type to the actual type.
        elif project_role.role_type != project_role_type:
            project_role.role_type = project_role_type
            request.db.add(project_role)

        request.db.add(project)

    request.db.flush()
