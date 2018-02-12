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

import datetime
import factory.fuzzy
from armonaut.build.models import Build, Commit, Status
from . import ArmonautFactory
from .projects import ProjectFactory


class CommitFactory(ArmonautFactory):
    class Meta:
        model = Commit

    hexsha = factory.fuzzy.FuzzyText(length=40, chars='01234567890abcdef')
    ref = 'ref/heads/master'

    author_github_id = factory.fuzzy.FuzzyInteger(0, 10000)
    author_name = factory.fuzzy.FuzzyText()
    author_email = factory.fuzzy.FuzzyText()
    message = factory.fuzzy.FuzzyText()


class BuildFactory(ArmonautFactory):
    class Meta:
        model = Build

    number = factory.fuzzy.FuzzyInteger(0, 10000)
    status = Status.pending

    started_at = factory.fuzzy.FuzzyNaiveDateTime(datetime.datetime(2016, 1, 1))
    finished_at = factory.fuzzy.FuzzyNaiveDateTime(datetime.datetime(2016, 1, 1))

    project = factory.SubFactory(ProjectFactory)
    commit = factory.SubFactory(CommitFactory)
