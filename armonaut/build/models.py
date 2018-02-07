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
from armonaut.db import Model
from sqlalchemy import (Column, String, DateTime,
                        ForeignKey, Enum, BigInteger)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import sql


class Status(enum.Enum):
    pending = 'pending'
    running = 'running'
    success = 'success'
    failure = 'failure'
    error = 'error'


class Commit(Model):
    __tablename__ = 'commits'

    hexsha = Column(String, nullable=False, index=True)
    ref = Column(String, nullable=False)

    author_github_id = Column(BigInteger, default=None)
    author_name = Column(String, nullable=False)
    author_email = Column(String, nullable=False)
    message = Column(String(256), nullable=False)

    build = relationship('Build', back_populates='commit', uselist=False)


class Build(Model):
    __tablename__ = 'builds'

    status = Column(Enum(Status),
                    default=Status.pending,
                    nullable=False,
                    index=True)

    started_at = Column(DateTime, nullable=False, server_default=sql.func.now())
    finished_at = Column(DateTime, nullable=True, default=None)

    project = relationship('Project', back_populates='builds')
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    commit_id = Column(ForeignKey('commits.id'), nullable=False)
    commit = relationship(
        'Commit',
        back_populates='build',
        uselist=False,
        cascade='all, delete-orphan',
        single_parent=True
    )
    jobs = relationship(
        'Job',
        back_populates='build',
        cascade='all, delete-orphan'
    )


class Job(Model):
    __tablename__ = 'jobs'

    status = Column(Enum(Status),
                    default=Status.pending,
                    nullable=False,
                    index=True)

    started_at = Column(DateTime, server_default=sql.func.now())
    finished_at = Column(DateTime, nullable=True, default=None)
    config = Column(JSON(none_as_null=True), nullable=False)

    build = relationship(
        'Build',
        back_populates='jobs'
    )
    build_id = Column(ForeignKey('builds.id'), nullable=False)
