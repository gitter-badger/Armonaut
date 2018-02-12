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

import factory.fuzzy
from armonaut.project.models import Project, ProjectRole, ProjectRoleType
from . import ArmonautFactory
from .users import UserFactory


class ProjectFactory(ArmonautFactory):
    class Meta:
        model = Project

    owner = factory.fuzzy.FuzzyText(length=12)
    name = factory.fuzzy.FuzzyText(length=12)
    github_id = factory.fuzzy.FuzzyInteger(1, 10000)

    webhook_id = factory.fuzzy.FuzzyInteger(1, 100)
    webhook_secret = factory.fuzzy.FuzzyText(length=32)

    active = True
    public = True


class ProjectRoleFactory(ArmonautFactory):
    class Meta:
        model = ProjectRole

    role_type = factory.fuzzy.FuzzyChoice([
        ProjectRoleType.OWNER, ProjectRoleType.COLLABORATOR, ProjectRoleType.READ_ONLY
    ])
    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
